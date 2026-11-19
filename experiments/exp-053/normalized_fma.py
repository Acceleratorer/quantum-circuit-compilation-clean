"""Check a pivot-normalized FMA recurrence and its count/width screen."""

from __future__ import annotations

import json
from itertools import product
from pathlib import Path
import sys
from random import Random


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def normalized_state(data, points, mul, modulus, degree):
    d, g = list(data), [1] * len(data)
    basis = [[[1], [0]], [[0], [1]]]
    rank1, rank2, history = 0, 1, 0

    for j, point in enumerate(points):
        dj, gj = d[j], g[j]
        swap = gj == 0 or (dj != 0 and rank1 < rank2)
        history |= int(swap) << j

        if swap:
            assert dj != 0
            ratio = fma.gf_mul(
                gj, fma.gf_inv(dj, modulus, degree), modulus, degree
            )
            step = [[[ratio], [1]], [[point, 1], [0]]]
            for i in range(j + 1, len(points)):
                old_d, old_g = d[i], g[i]
                d[i] = fma.gf_mul(ratio, old_d, modulus, degree) ^ old_g
                g[i] = fma.gf_mul(points[i] ^ point, old_d, modulus, degree)
            rank1, rank2 = rank2, rank1 + 2
        else:
            assert gj != 0
            ratio = fma.gf_mul(
                dj, fma.gf_inv(gj, modulus, degree), modulus, degree
            )
            step = [[[1], [ratio]], [[0], [point, 1]]]
            for i in range(j + 1, len(points)):
                old_d, old_g = d[i], g[i]
                d[i] = old_d ^ fma.gf_mul(ratio, old_g, modulus, degree)
                g[i] = fma.gf_mul(points[i] ^ point, old_g, modulus, degree)
            rank2 += 2

        basis = fma.matrix_mul(step, basis, mul)

    return d, g, history, basis


def normalized_low_row(basis, mul, modulus, degree):
    row = min(range(2), key=lambda index: fma.row_rank(basis, index))
    w, n = (fma.trim(list(poly)) for poly in basis[row])
    pivot = w[-1] if w != [0] else n[-1]
    scale = fma.gf_inv(pivot, modulus, degree)
    return tuple(
        tuple(fma.trim([mul(scale, value) for value in poly]))
        for poly in (w, n)
    )


def compare_to_reference(data, points, mul, modulus, degree):
    reference = fma.modular_basis(data, points, mul)
    _, _, history, candidate = normalized_state(
        data, points, mul, modulus, degree
    )
    assert history == fma.sequential_state(data, points, mul)[2]
    fma.assert_basis(data, [1] * len(points), points, candidate, mul)
    assert sorted(fma.row_rank(reference, row) for row in range(2)) == sorted(
        fma.row_rank(candidate, row) for row in range(2)
    )
    assert normalized_low_row(reference, mul, modulus, degree) == (
        normalized_low_row(candidate, mul, modulus, degree)
    )


def screen_gf8_four_samples():
    degree, modulus, points = 3, 0b1011, list(range(4))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    cases = 0
    for data in product(range(1 << degree), repeat=len(points)):
        compare_to_reference(data, points, mul, modulus, degree)
        cases += 1
    return cases


def screen_gf12_dqi_samples():
    degree, modulus, points = 12, 0x1053, list(range(70))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    rng = Random(0xF1A053)
    cases = 0
    per_weight = 16

    for weight in (1, 31, 35):
        for _ in range(per_weight):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(points)
            for beta, magnitude in zip(locations, magnitudes):
                power = beta
                for index in range(len(points)):
                    syndrome[index] ^= mul(magnitude, power)
                    power = mul(power, beta)
            data = fma.syndrome_to_fma_samples(syndrome, points, mul)
            compare_to_reference(data, points, mul, modulus, degree)
            cases += 1

    return {"cases": cases, "per_error_weight": per_weight, "weights": [1, 31, 35]}


def resource_screen():
    points = 70
    pair_updates = points * (points - 1) // 2
    ratio_products = points
    inversions = points
    products = pair_updates + ratio_products
    product_t, inverse_t = 42, 111  # 42T GF12 multiply; 66T inverse + 45T erasure
    fma_t = products * product_t + inversions * inverse_t
    scan_t, branch_rank_t = 45_045, 5_530
    reconstruction_t = 71 * product_t + 8 * inverse_t
    gate_t = 256_943
    naive_pair_bank_q = 70 * 12 + 69 * 12  # g_0=1 is a constant
    return {
        "points": points,
        "pair_updates": pair_updates,
        "variable_products": products,
        "ratio_inversions": inversions,
        "fma_arithmetic_toffolis": fma_t,
        "sampled_reconstruction_toffolis_assumption": reconstruction_t,
        "root_scan_toffolis": scan_t,
        "branch_rank_toffolis": branch_rank_t,
        "projected_total_toffolis": fma_t + reconstruction_t + scan_t + branch_rank_t,
        "gate_toffolis": gate_t,
        "projected_margin": gate_t - fma_t - reconstruction_t - scan_t - branch_rank_t,
        "naive_full_pair_bank_qubits": naive_pair_bank_q,
        "qubit_limit": 890,
        "naive_pair_bank_over_limit": naive_pair_bank_q - 890,
        "scope": (
            "Count projection assumes the existing sampled reconstruction, scan, and branch/rank costs. "
            "It excludes a width schedule, ratio-register liveness, and any uncounted phase work."
        ),
    }


def main():
    gf8_cases = screen_gf8_four_samples()
    gf12 = screen_gf12_dqi_samples()
    result = {
        "experiment": "exp-053",
        "result": "PASS",
        "normalized_fma_screen": {
            "gf8_all_four_sample_vectors": gf8_cases,
            "gf12_valid_70_symbol_samples": gf12,
            "branch_history_matches_reference": True,
            "row_ranks_match_reference": True,
            "normalized_low_row_matches_reference": True,
        },
        "resource_screen": resource_screen(),
        "scope": (
            "Classical recurrence and count screen only. The normalized in-place pair update is not a "
            "complete 70-symbol reversible schedule and the naive full pair bank exceeds Q=890."
        ),
    }
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
