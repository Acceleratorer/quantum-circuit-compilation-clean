"""Check a pivot-normalized FMA recurrence and its count/width screen."""

from __future__ import annotations

import json
import importlib.util
from itertools import product
from pathlib import Path
import sys
from random import Random

import numpy as np

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


def load_gate_arithmetic():
    import kickmix as km

    # Load the in-tree arithmetic helpers only; this does not build the decoder.
    sys.modules.setdefault("circ", km)
    path = ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
    spec = importlib.util.spec_from_file_location("dqi_fma_gate_arithmetic", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return km, module


def bit_columns(values, width):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack([((values >> bit) & 1).astype(np.bool_) for bit in range(width)])


def build_normalized_pair_cell(delta):
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(840)
    rank = builder.alloc_qubits(16)
    branch_register = builder.alloc_qubits(1)
    branch = branch_register[0]
    ratio = builder.alloc_qubits(12)

    pivot_d, pivot_g = payload[:12], payload[12:24]
    pair_d, pair_g = payload[24:36], payload[36:48]

    # Canonicalize either FMA branch to (d, g), compute d/g, then restore it.
    builder.cswap(branch, pivot_d, pivot_g)
    inverse_transcript = ar.inverse_inplace_forward(builder, pivot_g)
    ar.mul_xor(builder, pivot_d, pivot_g, ratio)

    # Both branches now use d ^= ratio*g; the controlled swaps select the
    # matching input and output orientation.
    builder.cswap(branch, pair_d, pair_g)
    ar.mul_xor(builder, ratio, pair_g, pair_d)
    builder.gf2_imul(delta, target=pair_g, field=ar.field(12))
    builder.cswap(branch, pair_d, pair_g)

    # The pivot is unchanged, so recompute its ratio to clear the workspace.
    ar.mul_xor(builder, pivot_d, pivot_g, ratio)
    builder.free(ratio)
    ar.inverse_inplace_reverse(builder, pivot_g, inverse_transcript)
    builder.cswap(branch, pivot_d, pivot_g)

    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "branch": branch_register,
        "pivot_d": pivot_d,
        "pivot_g": pivot_g,
        "pair_d": pair_d,
        "pair_g": pair_g,
    }


def check_normalized_pair_cell():
    delta = 17
    km, _, circuit, regs = build_normalized_pair_cell(delta)
    degree, modulus = 12, 0x1053
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    rng = Random(0xF1A0C311)
    cases = []
    for branch in (False, True):
        for _ in range(16):
            pivot_d = rng.randrange(1 << degree)
            pivot_g = rng.randrange(1, 1 << degree) if not branch else rng.randrange(1 << degree)
            if branch and pivot_d == 0:
                pivot_d = 1
            pair_d = rng.randrange(1 << degree)
            pair_g = rng.randrange(1 << degree)
            cases.append((branch, pivot_d, pivot_g, pair_d, pair_g))

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    values = {
        "pivot_d": [case[1] for case in cases],
        "pivot_g": [case[2] for case in cases],
        "pair_d": [case[3] for case in cases],
        "pair_g": [case[4] for case in cases],
    }
    for name, symbols in values.items():
        sim.write_across_shots(regs[name], bit_columns(symbols, degree))
    branch_values = [int(case[0]) for case in cases]
    sim.write_across_shots(regs["branch"], bit_columns(branch_values, 1))
    sim.write_across_shots(regs["rank"], np.zeros((16, len(cases)), dtype=np.bool_))
    sim.do(circuit)

    expected_d, expected_g = [], []
    for branch, pivot_d, pivot_g, pair_d, pair_g in cases:
        numerator, denominator = (pivot_g, pivot_d) if branch else (pivot_d, pivot_g)
        ratio = mul(numerator, fma.gf_inv(denominator, modulus, degree))
        if branch:
            expected_d.append(mul(delta, pair_d))
            expected_g.append(pair_g ^ mul(ratio, pair_d))
        else:
            expected_d.append(pair_d ^ mul(ratio, pair_g))
            expected_g.append(mul(delta, pair_g))

    for name in ("pivot_d", "pivot_g"):
        assert np.array_equal(
            sim.read_across_shots(regs[name]), bit_columns(values[name], degree)
        )
    assert np.array_equal(sim.read_across_shots(regs["pair_d"]), bit_columns(expected_d, degree))
    assert np.array_equal(sim.read_across_shots(regs["pair_g"]), bit_columns(expected_g, degree))
    assert np.array_equal(sim.read_across_shots(regs["rank"]), np.zeros((16, len(cases)), dtype=np.bool_))
    assert np.array_equal(sim.read_across_shots(regs["branch"]), bit_columns(branch_values, 1))
    assert not np.any(sim.read_phase_flipped_across_shots())

    outputs = set(list(regs["payload"]) + list(regs["rank"]) + list(regs["branch"]))
    scratch = [km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in outputs]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    return {
        "cases": len(cases),
        "branches": 2,
        "delta": delta,
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
    }


def resource_screen():
    points = 70
    pair_updates = points * (points - 1) // 2
    ratio_products = points
    ratio_cleanup_products = points
    inversions = points
    products = pair_updates + ratio_products + ratio_cleanup_products
    product_t = 42
    inverse_forward_t, inverse_restore_t = 66, 72
    pair_cswaps_t, pivot_cswaps_t = 24, 24
    fma_t = (
        products * product_t
        + pair_updates * pair_cswaps_t
        + inversions * (inverse_forward_t + inverse_restore_t + pivot_cswaps_t)
    )
    scan_t, branch_rank_t = 45_045, 5_530
    reconstruction_t = 71 * product_t + 8 * 111
    gate_t = 256_943
    naive_pair_bank_q = 70 * 12 + 69 * 12  # g_0=1 is a constant
    return {
        "points": points,
        "pair_updates": pair_updates,
        "variable_products": products,
        "ratio_products_to_compute_and_clear": ratio_products + ratio_cleanup_products,
        "ratio_inversions": inversions,
        "inverse_forward_toffolis": inverse_forward_t,
        "inverse_restore_toffolis": inverse_restore_t,
        "controlled_swap_toffolis_per_pair_update": pair_cswaps_t,
        "controlled_swap_toffolis_per_pivot": pivot_cswaps_t,
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
        "single_pair_cell_qubits": 888,
        "single_pair_cell_toffolis": 312,
        "scope": (
            "Count projection includes ratio cleanup, branch-controlled canonicalizing swaps, and the "
            "measured in-place inverse cell. It assumes the existing sampled reconstruction, scan, and "
            "branch/rank costs. It excludes the 4+66 width schedule and any uncounted phase work."
        ),
    }


def main():
    gf8_cases = screen_gf8_four_samples()
    gf12 = screen_gf12_dqi_samples()
    pair_cell = check_normalized_pair_cell()
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
        "compiled_pair_cell": pair_cell,
        "resource_screen": resource_screen(),
        "scope": (
            "Classical recurrence plus one compiled normalized pair cell. This is not a complete "
            "70-symbol reversible schedule, and the naive full pair bank exceeds Q=890."
        ),
    }
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
