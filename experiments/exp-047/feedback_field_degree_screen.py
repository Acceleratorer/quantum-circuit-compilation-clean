"""Exhaustively fit the packed BM feedback as a field-quadratic function."""

from __future__ import annotations

from itertools import combinations, product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exp-045"))
import bm_state_model as bm


def state_variables(state: bm.PackedBMState, length: int) -> tuple[list[int], list[str]]:
    c = list(state.c_coefficients) + [0] * (length - len(state.c_coefficients))
    backup = list(state.backup_coefficients) + [0] * (length - len(state.backup_coefficients))
    linear_bits = [(state.linear_complexity >> i) & 1 for i in range(length.bit_length())]
    shift_bits = [(state.shift >> i) & 1 for i in range((length + 1).bit_length())]
    variables = c + backup + linear_bits + shift_bits + [state.last_discrepancy]
    kinds = ["field"] * (2 * length) + ["control"] * (len(linear_bits) + len(shift_bits)) + ["field"]
    return variables, kinds


def features(variables: list[int], multiply: list[list[int]]) -> list[int]:
    return [1, *variables, *(multiply[variables[i]][variables[j]]
                              for i in range(len(variables))
                              for j in range(i, len(variables)))]


def fit_prefixes(length: int, degree: int, modulus: int) -> dict[str, object]:
    field = bm.GF2Field(degree, modulus)
    order = 1 << degree
    multiply = [[field.mul(a, b) for b in range(order)] for a in range(order)]
    pivots: dict[int, tuple[list[int], int]] = {}
    state_outputs: dict[tuple[object, ...], int] = {}
    kinds: list[str] | None = None
    feature_count = 0
    rows_checked = 0

    for sequence in product(range(order), repeat=length):
        state = bm.bm_prefix_states(sequence, field)[-1]
        key = state.key()
        predictor = 0
        for offset, coefficient in enumerate(state.c_coefficients, start=1):
            predictor ^= multiply[coefficient][sequence[length - offset]]

        previous = state_outputs.get(key)
        if previous is not None and previous != predictor:
            return {
                "field_degree": degree,
                "prefix_length": length,
                "sequences": order**length,
                "rows_checked": rows_checked + 1,
                "state_collisions": 1,
                "quadratic_fit": False,
                "reason": "same packed state has different feedback values",
            }
        state_outputs[key] = predictor

        variables, row_kinds = state_variables(state, length)
        if kinds is None:
            kinds = row_kinds
            feature_count = 1 + len(variables) + len(variables) * (len(variables) + 1) // 2
        row = features(variables, multiply)
        rhs = predictor
        rows_checked += 1

        for pivot in sorted(pivots):
            factor = row[pivot]
            if factor:
                basis_row, basis_rhs = pivots[pivot]
                for column in range(pivot, feature_count):
                    row[column] ^= multiply[factor][basis_row[column]]
                rhs ^= multiply[factor][basis_rhs]

        pivot = next((column for column, value in enumerate(row) if value), None)
        if pivot is None:
            if rhs:
                return {
                    "field_degree": degree,
                    "prefix_length": length,
                    "sequences": order**length,
                    "rows_checked": rows_checked,
                    "state_collisions": 0,
                    "quadratic_fit": False,
                    "reason": "degree-2 feature span is inconsistent",
                    "feature_count": feature_count,
                }
            continue

        scale = field.inv(row[pivot])
        for column in range(pivot, feature_count):
            row[column] = multiply[scale][row[column]]
        rhs = multiply[scale][rhs]
        pivots[pivot] = (row, rhs)

    coefficients = [0] * feature_count
    for pivot in sorted(pivots, reverse=True):
        row, rhs = pivots[pivot]
        for column in range(pivot + 1, feature_count):
            rhs ^= multiply[row[column]][coefficients[column]]
        coefficients[pivot] = rhs

    variable_count = len(kinds or [])
    field_products = control_field_products = control_products = 0
    index = 1 + variable_count
    for left in range(variable_count):
        for right in range(left, variable_count):
            if not coefficients[index]:
                index += 1
                continue
            left_kind, right_kind = kinds[left], kinds[right]
            if left == right:
                # Squaring a field element is GF(2)-linear; a control bit squares to itself.
                pass
            elif left_kind == right_kind == "field":
                field_products += 1
            elif left_kind == right_kind == "control":
                control_products += 1
            else:
                control_field_products += 1
            index += 1

    return {
        "field_degree": degree,
        "prefix_length": length,
        "sequences": order**length,
        "rows_checked": rows_checked,
        "unique_states": len(state_outputs),
        "quadratic_fit": True,
        "feature_count": feature_count,
        "nonzero_terms": sum(value != 0 for value in coefficients),
        "field_field_products": field_products,
        "control_field_products": control_field_products,
        "control_control_products": control_products,
    }


def main() -> None:
    results = [
        fit_prefixes(length, degree, modulus)
        for degree, modulus, max_length in ((2, 0b111, 3), (3, 0b1011, 5))
        for length in range(1, max_length + 1)
    ]
    output = json.dumps(results, indent=2)
    Path(__file__).with_name("results.json").write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
