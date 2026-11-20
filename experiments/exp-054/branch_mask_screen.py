"""Measure structure in FMA rank-default exception masks for DQI samples."""

from __future__ import annotations

from math import ceil, comb, log2
from pathlib import Path
from random import Random
import json
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-053"))
import fma_state_compression as fma  # noqa: E402
from normalized_fma import compare_to_reference  # noqa: E402


DEGREE = 12
MODULUS = 0x1053
POINTS = tuple(range(70))
Q = 1 << DEGREE
PAIR_CELL_Q = 871
Q_LIMIT = 890


def build_multiply_table():
    values = np.arange(Q, dtype=np.uint16)
    table = np.empty((Q, Q), dtype=np.uint16)
    for left in range(Q):
        right = values.copy()
        result = np.zeros(Q, dtype=np.uint16)
        shifted = left
        for _ in range(DEGREE):
            result ^= np.where((right & 1) != 0, shifted, 0).astype(np.uint16)
            right >>= 1
            shifted <<= 1
            if shifted & Q:
                shifted ^= MODULUS
        table[left] = result
    return table


def transition_count(mask: int) -> int:
    return ((mask ^ (mask >> 1)) & ((1 << (len(POINTS) - 1)) - 1)).bit_count()


def summarize_masks(masks: list[int]) -> dict[str, object]:
    transitions = [transition_count(mask) for mask in masks]
    max_transitions = max(transitions)
    family_size = 2 * sum(
        comb(len(POINTS) - 1, count)
        for count in range(max_transitions + 1)
    )
    return {
        "cases": len(masks),
        "distinct_exception_masks": len(set(masks)),
        "sampled_unique_label_bits": ceil(log2(max(1, len(set(masks))))),
        "max_transitions": max_transitions,
        "transition_histogram": {
            str(count): transitions.count(count)
            for count in sorted(set(transitions))
        },
        "fixed_bits_for_any_70_bit_mask_with_at_most_sampled_max_transitions": ceil(
            log2(family_size)
        ),
    }


def screen_all_single_error_locations(table, multiply):
    """Run the unnormalized FMA update for all nonzero error locations."""
    betas = np.arange(1, Q, dtype=np.uint16)
    node = [1]
    for point in POINTS:
        node = fma.poly_mul(node, [point, 1], multiply)
    quotients = list(fma._quotients(node, POINTS, multiply))

    powers = np.empty((len(POINTS), len(betas)), dtype=np.uint16)
    powers[0] = betas
    for index in range(1, len(POINTS)):
        powers[index] = table[powers[index - 1], betas]

    d = np.zeros((len(betas), len(POINTS)), dtype=np.uint16)
    for index, quotient in enumerate(quotients):
        sample = np.zeros(len(betas), dtype=np.uint16)
        for power, coefficient in enumerate(quotient):
            if coefficient:
                sample ^= table[coefficient, powers[power]]
        d[:, index] = sample

    g = np.ones_like(d)
    rank1 = np.zeros(len(betas), dtype=np.int16)
    rank2 = np.ones(len(betas), dtype=np.int16)
    mask_low = np.zeros(len(betas), dtype=np.uint64)
    mask_high = np.zeros(len(betas), dtype=np.uint16)

    for pivot_index, point in enumerate(POINTS):
        pivot_d = d[:, pivot_index].copy()
        pivot_g = g[:, pivot_index].copy()
        default = rank1 < rank2
        swap = (pivot_g == 0) | ((pivot_d != 0) & default)
        exception = swap != default
        if pivot_index < 64:
            mask_low |= exception.astype(np.uint64) << pivot_index
        else:
            mask_high |= exception.astype(np.uint16) << (pivot_index - 64)

        next_rank1 = np.where(swap, rank2, rank1)
        next_rank2 = np.where(swap, rank1 + 2, rank2 + 2)
        rank1, rank2 = next_rank1, next_rank2

        for index in range(pivot_index + 1, len(POINTS)):
            old_d = d[:, index].copy()
            old_g = g[:, index].copy()
            delta = point ^ POINTS[index]
            d[:, index] = table[pivot_g, old_d] ^ table[pivot_d, old_g]
            g[:, index] = table[delta, np.where(swap, old_d, old_g)]

    return [
        int(low) | (int(high) << 64)
        for low, high in zip(mask_low, mask_high)
    ]


def make_syndrome(locations, magnitudes, multiply):
    syndrome = [0] * len(POINTS)
    for beta, magnitude in zip(locations, magnitudes):
        power = beta
        for index in range(len(POINTS)):
            syndrome[index] ^= multiply(magnitude, power)
            power = multiply(power, beta)
    return syndrome


def screen_sampled_weights(multiply, sample_count=256):
    results = {}
    masks_by_weight = {1: [], 31: [], 35: []}
    seeds = ((0xF1A054, (31, 35)), (0xF1A055, (1, 31, 35)))
    for seed, weights in seeds:
        rng = Random(seed)
        per_seed = {}
        for weight in weights:
            masks = []
            for _ in range(sample_count):
                locations = rng.sample(range(1, Q), weight)
                magnitudes = [rng.randrange(1, Q) for _ in locations]
                syndrome = make_syndrome(locations, magnitudes, multiply)
                data = fma.syndrome_to_fma_samples(syndrome, POINTS, multiply)
                _, _, exception_mask, _ = compare_to_reference(
                    data, POINTS, multiply, MODULUS, DEGREE
                )
                masks.append(exception_mask)
            per_seed[str(weight)] = summarize_masks(masks)
            masks_by_weight[weight].extend(masks)
        results[hex(seed)] = per_seed
    results["combined_by_weight"] = {
        str(weight): summarize_masks(masks)
        for weight, masks in masks_by_weight.items()
        if masks
    }
    return results, masks_by_weight


def check_scalar_reference(multiply, single_masks):
    checks = 0
    for beta in (1, 2, 17, 68, 69, 70, 4095):
        for magnitude in (1, 13, 0xABC):
            syndrome = make_syndrome([beta], [magnitude], multiply)
            data = fma.syndrome_to_fma_samples(syndrome, POINTS, multiply)
            _, _, scalar_mask, _ = compare_to_reference(
                data, POINTS, multiply, MODULUS, DEGREE
            )
            assert scalar_mask == single_masks[beta - 1]
            checks += 1
    return checks


def main():
    table = build_multiply_table()
    original_multiply = fma.gf_mul
    for left, right in ((0, 0), (1, 4095), (0x105, 0x2A3), (4095, 4095)):
        assert int(table[left, right]) == original_multiply(
            left, right, MODULUS, DEGREE
        )

    def fast_multiply(left, right, modulus, degree):
        if (modulus, degree) == (MODULUS, DEGREE):
            return int(table[left, right])
        return original_multiply(left, right, modulus, degree)

    fma.gf_mul = fast_multiply
    multiply = lambda left, right: int(table[left, right])
    try:
        single_masks = screen_all_single_error_locations(table, multiply)
        scalar_checks = check_scalar_reference(multiply, single_masks)
        sampled, masks_by_weight = screen_sampled_weights(multiply)
    finally:
        fma.gf_mul = original_multiply

    result = {
        "experiment": "exp-054",
        "field": "GF(2^12)",
        "points": len(POINTS),
        "single_error_supports": {
            **summarize_masks(single_masks),
            "domain": "all 4095 nonzero error locations at magnitude 1",
            "scalar_cross_checks_across_magnitudes": scalar_checks,
        },
        "sampled_error_weights": sampled,
        "sampled_masks_across_weights": summarize_masks(
            masks_by_weight[1] + masks_by_weight[31] + masks_by_weight[35]
        ),
        "width_screen": {
            "compiled_pair_cell_qubits": PAIR_CELL_Q,
            "qubit_limit": Q_LIMIT,
            "remaining_qubits": Q_LIMIT - PAIR_CELL_Q,
            "scope": "Optimistic additive side-information screen; excludes a full-circuit liveness proof.",
        },
        "limitations": [
            "The single-error enumeration covers all supports at magnitude 1, with only selected magnitude cross-checks.",
            "Weights 31 and 35 are seeded samples, not an exact bound over valid DQI errors.",
            "Combinatorial transition coding is a bit-count screen only; no reversible encoder or decoder was built.",
        ],
    }
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
