"""Exhaustively measure branch-history collisions on valid small-field DQI inputs."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-053"))

import fma_state_compression as fma
import normalized_fma


DEGREE = 3
MODULUS = 0b1011
POINTS = tuple(range(8))


def make_field_tables():
    size = 1 << DEGREE
    multiply = [
        [fma.gf_mul(left, right, MODULUS, DEGREE) for right in range(size)]
        for left in range(size)
    ]
    inverse = [0] + [
        next(value for value in range(1, size) if multiply[item][value] == 1)
        for item in range(1, size)
    ]
    return multiply, inverse


def replay_ratios(samples, multiply, inverse):
    state = list(samples)
    branches = []
    rank1, rank2 = 0, 1

    for pivot, point in enumerate(POINTS):
        d, g = state[pivot], 1
        for previous in range(pivot):
            ratio = state[previous]
            delta = point ^ POINTS[previous]
            old_d = d
            if branches[previous]:
                d = multiply[ratio][old_d] ^ g
                g = multiply[delta][old_d]
            else:
                d ^= multiply[ratio][g]
                g = multiply[delta][g]

        swap = g == 0 or (d != 0 and rank1 < rank2)
        if swap:
            ratio = multiply[g][inverse[d]]
            rank1, rank2 = rank2, rank1 + 2
        else:
            ratio = multiply[d][inverse[g]]
            rank2 += 2
        state[pivot] = ratio
        branches.append(swap)

    history = sum(int(branch) << index for index, branch in enumerate(branches))
    return tuple(state), history, rank1


def smallest_fixed_branch_projection(groups):
    for width in range(len(POINTS) + 1):
        masks = []
        for positions in combinations(range(len(POINTS)), width):
            mask = sum(1 << position for position in positions)
            if all(
                len({history & mask for history in histories}) == len(histories)
                for histories in groups
            ):
                masks.append(list(positions))
        if masks:
            return {"branch_bits": width, "position_sets": masks}
    raise AssertionError("the complete branch history must distinguish each fiber")


def run_screen():
    multiply, inverse = make_field_tables()
    multiply_callback = lambda left, right: multiply[left][right]
    ratio_fibers = defaultdict(list)
    ratio_rank_fibers = defaultdict(list)
    case_count = 0

    for weight in range(5):
        for locations in combinations(range(1, 1 << DEGREE), weight):
            for magnitudes in product(range(1, 1 << DEGREE), repeat=weight):
                syndrome = [0] * len(POINTS)
                for location, magnitude in zip(locations, magnitudes):
                    power = location
                    for index in range(len(POINTS)):
                        syndrome[index] ^= multiply[magnitude][power]
                        power = multiply[power][location]

                samples = tuple(
                    fma.syndrome_to_fma_samples(
                        syndrome, POINTS, multiply_callback
                    )
                )
                ratios, history, rank1 = replay_ratios(samples, multiply, inverse)
                if case_count < 32:
                    reference = normalized_fma.replayed_ratios(
                        samples, POINTS, MODULUS, DEGREE
                    )
                    assert ratios == reference[0]
                    assert tuple(bool(history >> i & 1) for i in range(8)) == reference[1]
                ratio_fibers[ratios].append(history)
                ratio_rank_fibers[(ratios, rank1)].append(history)
                case_count += 1

    ratio_groups = list(ratio_fibers.values())
    ratio_rank_groups = list(ratio_rank_fibers.values())
    return {
        "experiment": "exp-053-valid-ratio-history-gf8",
        "field": "GF(8)",
        "points": list(POINTS),
        "error_locations": "nonzero field elements",
        "error_weights": "0..4",
        "cases": case_count,
        "ratio_only": {
            "distinct_vectors": len(ratio_fibers),
            "collision_groups": sum(len(group) > 1 for group in ratio_groups),
            "maximum_fiber": max(map(len, ratio_groups)),
            "minimum_fixed_branch_projection": smallest_fixed_branch_projection(
                ratio_groups
            ),
        },
        "ratio_plus_final_rank": {
            "distinct_keys": len(ratio_rank_fibers),
            "collision_groups": sum(
                len(group) > 1 for group in ratio_rank_groups
            ),
            "maximum_fiber": max(map(len, ratio_rank_groups)),
            "minimum_fixed_branch_projection": smallest_fixed_branch_projection(
                ratio_rank_groups
            ),
        },
        "scope": (
            "Exhaustive valid RS error patterns over GF(8), not a GF(2^12) "
            "bound or a reversible encoder. A fixed branch projection is an "
            "information screen only."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
