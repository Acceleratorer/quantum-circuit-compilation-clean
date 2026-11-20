"""Screen the projective sentinel encoding for the streamed FMA label map."""

from __future__ import annotations

from collections import defaultdict
from itertools import product
import json
from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-053"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


DEGREE = 3
MODULUS = 0b1011
POINTS = tuple(range(4))
FIELD_SIZE = 1 << DEGREE


def multiply(left, right):
    return fma.gf_mul(left, right, MODULUS, DEGREE)


def inverse(value):
    return fma.gf_inv(value, MODULUS, DEGREE)


def apply_pivot(matrix, ratio, branch, delta, mul=multiply):
    a, b, c, d = matrix
    if branch:
        return (
            mul(ratio, a) ^ c,
            mul(ratio, b) ^ d,
            mul(delta, a),
            mul(delta, b),
        )
    return (
        a ^ mul(ratio, c),
        b ^ mul(ratio, d),
        mul(delta, c),
        mul(delta, d),
    )


def prefix_matrix(pivot, ratios, branches, points=POINTS, mul=multiply):
    matrix = (1, 0, 0, 1)
    for previous in range(pivot):
        delta = points[pivot] ^ points[previous]
        matrix = apply_pivot(
            matrix, ratios[previous], branches[previous], delta, mul
        )
    return matrix


def sentinel_for(matrix, order, mul=multiply, inv=inverse):
    a, _, c, _ = matrix
    if not a or not c:
        return None
    return mul(a, inv(c)) if not order else mul(c, inv(a))


def advance_rank(rank1, rank2, branch):
    return (rank2, rank1 + 2) if branch else (rank1, rank2 + 2)


def encode_step(matrix, sample, order, mul=multiply, inv=inverse):
    a, b, c, d = matrix
    numerator = mul(a, sample) ^ b
    denominator = mul(c, sample) ^ d
    branch = denominator == 0 or (numerator != 0 and order)
    if branch:
        assert numerator != 0
        ratio = mul(denominator, inv(numerator))
    else:
        assert denominator != 0
        ratio = mul(numerator, inv(denominator))
    sentinel = sentinel_for(matrix, order, mul, inv)
    label = (
        sentinel
        if sentinel is not None and numerator == 0 and not branch
        else ratio
    )
    return label, ratio, branch


def encode(samples, points=POINTS, mul=multiply, inv=inverse):
    """Map samples to triangular labels using a per-prefix field permutation."""
    if len(samples) != len(points):
        raise ValueError("samples and points must have equal length")
    ratios = []
    branches = []
    labels = []
    rank1, rank2 = 0, 1

    for pivot, sample in enumerate(samples):
        matrix = prefix_matrix(pivot, ratios, branches, points, mul)
        order = rank1 < rank2
        label, ratio, branch = encode_step(matrix, sample, order, mul, inv)
        labels.append(label)
        ratios.append(ratio)
        branches.append(branch)
        rank1, rank2 = advance_rank(rank1, rank2, branch)

    return tuple(labels), tuple(ratios), tuple(branches)


def decode(labels, points=POINTS, mul=multiply, inv=inverse):
    if len(labels) != len(points):
        raise ValueError("labels and points must have equal length")
    ratios = []
    branches = []
    recovered = []
    rank1, rank2 = 0, 1

    for pivot, label in enumerate(labels):
        matrix = prefix_matrix(pivot, ratios, branches, points, mul)
        a, b, c, d = matrix
        order = rank1 < rank2
        sentinel = sentinel_for(matrix, order, mul, inv)

        if sentinel is not None and label == sentinel:
            branch, ratio = False, 0
        elif label == 0:
            branch = True if sentinel is not None else a == 0
            ratio = 0
        else:
            branch, ratio = order, label

        if branch:
            numerator, denominator = 1, ratio
        else:
            numerator, denominator = ratio, 1

        original_numerator = mul(d, numerator) ^ mul(b, denominator)
        original_denominator = mul(c, numerator) ^ mul(a, denominator)
        assert original_denominator != 0
        sample = mul(original_numerator, inv(original_denominator))

        recovered.append(sample)
        ratios.append(ratio)
        branches.append(branch)
        rank1, rank2 = advance_rank(rank1, rank2, branch)

    return tuple(recovered)


def screen_gf8():
    label_to_sample = {}
    child_labels = defaultdict(dict)
    collision_contexts = set()
    cases = 0

    for samples in product(range(FIELD_SIZE), repeat=len(POINTS)):
        labels, _, _ = encode(samples)
        assert decode(labels) == samples
        assert labels not in label_to_sample or label_to_sample[labels] == samples
        label_to_sample[labels] = samples
        cases += 1

        for pivot in range(len(POINTS)):
            prefix = labels[:pivot]
            children = child_labels[(pivot, prefix)]
            prior = children.get(labels[pivot])
            assert prior is None or prior == samples[pivot]
            children[labels[pivot]] = samples[pivot]

            ratios, branches = [], []
            rank1, rank2 = 0, 1
            for previous in range(pivot):
                matrix = prefix_matrix(previous, ratios, branches)
                order = rank1 < rank2
                sentinel = sentinel_for(matrix, order)
                value = labels[previous]
                if sentinel is not None and value == sentinel:
                    branch, ratio = False, 0
                elif value == 0:
                    branch = True if sentinel is not None else matrix[0] == 0
                    ratio = 0
                else:
                    branch, ratio = order, value
                ratios.append(ratio)
                branches.append(branch)
                rank1, rank2 = advance_rank(rank1, rank2, branch)

            if sentinel_for(prefix_matrix(pivot, ratios, branches), rank1 < rank2) is not None:
                collision_contexts.add((pivot, prefix))

    assert len(label_to_sample) == FIELD_SIZE ** len(POINTS)
    assert child_labels
    assert all(len(children) == FIELD_SIZE for children in child_labels.values())
    return {
        "field": "GF(8)",
        "points": list(POINTS),
        "arbitrary_input_vectors": cases,
        "distinct_encoded_vectors": len(label_to_sample),
        "decode_errors": 0,
        "local_prefix_contexts": {
            str(pivot): sum(key[0] == pivot for key in child_labels)
            for pivot in range(len(POINTS))
        },
        "local_maps_all_bijective": True,
        "contexts_requiring_sentinel": len(collision_contexts),
        "maximum_local_fiber": 1,
        "result": "PASS",
        "scope": (
            "Exhaustive over every four-sample GF(8) vector. The sentinel "
            "replaces the d=0 branch's duplicate zero ratio with the missing "
            "ratio at the omitted projective input. This is a classical "
            "bijection screen; no reversible gate circuit or 70-point cost "
            "schedule is established."
        ),
    }


def screen_gf12_dqi():
    import fma_state_compression as fma
    import normalized_fma

    degree, modulus = 12, 0x1053
    points = list(range(70))
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    inv = lambda value: fma.gf_inv(value, modulus, degree)
    rng = Random(0xF1A053)
    cases_per_weight = 16
    checked = 0

    for weight in (1, 31, 35):
        for _ in range(cases_per_weight):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(points)
            for location, magnitude in zip(locations, magnitudes):
                power = location
                for index in range(len(points)):
                    syndrome[index] ^= mul(magnitude, power)
                    power = mul(power, location)

            samples = fma.syndrome_to_fma_samples(syndrome, points, mul)
            labels, ratios, branches = encode(samples, points, mul, inv)
            assert decode(labels, points, mul, inv) == tuple(samples)
            reference = normalized_fma.replayed_ratios(
                samples, points, modulus, degree
            )
            assert ratios == reference[0]
            assert branches == reference[1]
            checked += 1

    return {
        "field": "GF(2^12)",
        "points": len(points),
        "valid_dqi_samples": checked,
        "error_weights": [1, 31, 35],
        "round_trip_errors": 0,
        "raw_ratios_match_reference": True,
        "branch_history_matches_reference": True,
        "result": "PASS",
        "scope": (
            "48 seeded valid 70-symbol DQI samples. The projective sentinel "
            "label round-trips each sample vector and its raw ratios and "
            "branch history match the independent direct recurrence. This "
            "does not establish a reversible circuit or resource schedule."
        ),
    }


def screen_gf12_arbitrary_70(case_count=64):
    """Check the full 70-symbol label codec on arbitrary GF(2^12) vectors."""
    import normalized_fma

    degree, modulus = 12, 0x1053
    points = tuple(range(70))
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    inv = lambda value: fma.gf_inv(value, modulus, degree)
    rng = Random(0xB1EC7)
    checked = 0

    for _ in range(case_count):
        samples = tuple(rng.randrange(1 << degree) for _ in points)
        labels, ratios, branches = encode(samples, points, mul, inv)
        assert decode(labels, points, mul, inv) == samples
        reference = normalized_fma.replayed_ratios(
            samples, points, modulus, degree
        )
        assert ratios == reference[0]
        assert branches == reference[1]
        checked += 1

    return {
        "field": "GF(2^12)",
        "points": len(points),
        "arbitrary_vectors": checked,
        "round_trip_errors": 0,
        "recurrence_mismatches": 0,
        "result": "PASS",
        "scope": (
            "Seeded arbitrary 70-symbol vectors, not restricted to verifier "
            "syndromes. This supports the general triangular-bijection "
            "argument but is not a proof or a reversible circuit/resource "
            "schedule."
        ),
    }


def screen_transition_collision():
    identity = (1, 0, 0, 1)
    row_swap = (0, 1, 1, 0)
    order, delta, sample = False, 1, 0
    left_label, left_ratio, left_branch = encode_step(identity, sample, order)
    right_label, right_ratio, right_branch = encode_step(row_swap, sample, order)
    left = (
        apply_pivot(identity, left_ratio, left_branch, delta),
        left_label,
    )
    right = (
        apply_pivot(row_swap, right_ratio, right_branch, delta),
        right_label,
    )
    assert left == right == (identity, 0)
    return {
        "field": "GF(8)",
        "rank_order": order,
        "delta": delta,
        "input_states": [
            {"matrix": list(identity), "sample": sample},
            {"matrix": list(row_swap), "sample": sample},
        ],
        "common_output_matrix": list(identity),
        "common_label": 0,
        "joint_update_injective": False,
        "result": "COLLISION",
        "scope": (
            "A single fixed-determinant counterexample rejects the local "
            "transition (matrix, sample) -> (updated matrix, label) when the "
            "matrix is treated as independent input. It does not test the full "
            "triangular label sequence, whose earlier labels determine the "
            "prefix matrix."
        ),
    }


def screen():
    return {
        "gf8_exhaustive": screen_gf8(),
        "gf12_dqi_samples": screen_gf12_dqi(),
        "gf12_arbitrary_70_symbols": screen_gf12_arbitrary_70(),
        "joint_update_collision": screen_transition_collision(),
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2, sort_keys=True))
