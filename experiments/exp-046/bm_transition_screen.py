"""Exact low-degree screen of the packed BM one-symbol transition over GF(2)."""

from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exp-045"))
import bm_state_model as bm


def state_bits(state: bm.PackedBMState, prefix_length: int) -> list[int]:
    bits = list(state.c_coefficients) + [0] * (prefix_length - len(state.c_coefficients))
    bits += list(state.backup_coefficients) + [0] * (prefix_length - len(state.backup_coefficients))
    bits += [(state.linear_complexity >> i) & 1 for i in range(prefix_length.bit_length())]
    bits += [(state.shift >> i) & 1 for i in range((prefix_length + 1).bit_length())]
    bits.append(state.last_discrepancy)
    return bits


def add_to_basis(value: int, basis: list[int]) -> None:
    while value:
        pivot = value.bit_length() - 1
        if basis[pivot]:
            value ^= basis[pivot]
        else:
            basis[pivot] = value
            return


def in_span(value: int, basis: list[int]) -> bool:
    while value:
        pivot = value.bit_length() - 1
        if not basis[pivot]:
            return False
        value ^= basis[pivot]
    return True


def degree_profile(inputs: list[list[int]], outputs: list[list[int]], max_degree: int = 4) -> dict[str, object]:
    rows = len(inputs)
    features = len(inputs[0])
    targets = [
        sum(output[column] << row for row, output in enumerate(outputs))
        for column in range(len(outputs[0]))
    ]
    basis = [0] * rows
    full = (1 << rows) - 1
    degrees: list[int | None] = [None] * len(targets)
    profile: dict[str, int] = {}

    def record(degree: int) -> None:
        for index, target in enumerate(targets):
            if degrees[index] is None and in_span(target, basis):
                degrees[index] = degree
        profile[f"degree_le_{degree}"] = sum(value is not None for value in degrees)

    add_to_basis(full, basis)
    record(0)
    feature_columns = [
        sum(input_row[column] << row for row, input_row in enumerate(inputs))
        for column in range(features)
    ]
    for degree in range(1, max_degree + 1):
        for selection in combinations(range(features), degree):
            monomial = full
            for index in selection:
                monomial &= feature_columns[index]
            add_to_basis(monomial, basis)
        record(degree)

    return {
        "rows": rows,
        "input_bits": features,
        "output_bits": len(targets),
        "output_bits_with_min_degree_at_most": profile,
        "minimum_degrees_through_bound": degrees,
    }


def screen(prefix_length: int) -> dict[str, object]:
    field = bm.GF2Field(1, 0b11)
    forward_inputs: list[list[int]] = []
    forward_outputs: list[list[int]] = []
    reverse_inputs: list[list[int]] = []
    reverse_outputs: list[list[int]] = []
    conditioned_inputs: list[list[int]] = []
    conditioned_outputs: list[list[int]] = []

    for encoded in range(1 << prefix_length):
        sequence = [(encoded >> i) & 1 for i in range(prefix_length)]
        previous = bm.bm_prefix_states(sequence, field)[-1]
        previous_bits = state_bits(previous, prefix_length)
        for symbol in (0, 1):
            following = bm.bm_prefix_states((*sequence, symbol), field)[-1]
            following_bits = state_bits(following, prefix_length + 1)
            forward_inputs.append(previous_bits + [symbol])
            forward_outputs.append(following_bits)
            reverse_inputs.append(following_bits)
            reverse_outputs.append(previous_bits + [symbol])
            conditioned_inputs.append(following_bits + [symbol])
            conditioned_outputs.append(previous_bits)

    # If either map is not injective on the reachable domain, it needs extra history.
    assert len({tuple(row) for row in forward_inputs}) == len(forward_inputs)
    assert len({tuple(row) for row in forward_outputs}) == len(forward_outputs)
    assert len({tuple(row) for row in reverse_inputs}) == len(reverse_inputs)

    return {
        "field": "GF(2)",
        "prefix_length": prefix_length,
        "reachable_transitions": len(forward_inputs),
        "forward": degree_profile(forward_inputs, forward_outputs),
        "inverse_given_symbol": degree_profile(conditioned_inputs, conditioned_outputs),
        "inverse_recovering_symbol": degree_profile(reverse_inputs, reverse_outputs),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-prefix", type=int, default=5)
    parser.add_argument("--max-prefix", type=int, default=9)
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("results.json"))
    args = parser.parse_args()
    if args.min_prefix < 1 or args.max_prefix < args.min_prefix or args.max_prefix > 10:
        raise SystemExit("prefix lengths must satisfy 1 <= min <= max <= 10")

    results = [screen(length) for length in range(args.min_prefix, args.max_prefix + 1)]
    serialized = json.dumps(results, indent=2) + "\n"
    args.out.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
