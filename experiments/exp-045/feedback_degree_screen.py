"""Exhaustively test low-degree feedback formulas on packed GF(2) BM states."""

from __future__ import annotations

from itertools import combinations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bm_state_model as bm


def _in_span(columns: list[int], target: int) -> bool:
    basis: dict[int, int] = {}
    for column in columns:
        value = column
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break

    while target:
        pivot = target.bit_length() - 1
        if pivot not in basis:
            return False
        target ^= basis[pivot]
    return True


def _screen_length(length: int) -> dict[str, int | bool | str]:
    field = bm.GF2Field(1, 0b11)
    rows: list[list[int]] = []
    feedback = 0

    for row in range(1 << length):
        sequence = [(row >> i) & 1 for i in range(length)]
        state = bm.bm_prefix_states(sequence, field)[-1]
        features = list(state.c_coefficients + (0,) * (length - len(state.c_coefficients)))
        features += list(state.backup_coefficients + (0,) * (length - len(state.backup_coefficients)))
        features += [(state.linear_complexity >> i) & 1 for i in range(length.bit_length())]
        features += [(state.shift >> i) & 1 for i in range((length + 1).bit_length())]
        features.append(state.last_discrepancy)
        rows.append(features)

        value = 0
        for offset, coefficient in enumerate(state.c_coefficients, 1):
            value ^= coefficient & sequence[length - offset]
        if value:
            feedback |= 1 << row

    state_columns = [
        sum(rows[row][column] << row for row in range(len(rows)))
        for column in range(len(rows[0]))
    ]
    constant = (1 << len(rows)) - 1
    affine_columns = [constant, *state_columns]
    quadratic_columns = affine_columns + [
        state_columns[left] & state_columns[right]
        for left, right in combinations(range(len(state_columns)), 2)
    ]

    return {
        "field": "GF(2)",
        "prefix_length": length,
        "prefixes": len(rows),
        "packed_state_bits": len(rows[0]),
        "feedback_affine": _in_span(affine_columns, feedback),
        "feedback_degree_at_most_2": _in_span(quadratic_columns, feedback),
    }


if __name__ == "__main__":
    print(json.dumps([_screen_length(length) for length in range(5, 13)], indent=2))
