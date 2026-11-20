"""Check a pivot-normalized FMA recurrence and its count/width screen."""

from __future__ import annotations

import json
import importlib.util
from itertools import combinations, product
from pathlib import Path
import sys
from random import Random

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def normalized_state(
    data, points, mul, modulus, degree, g_values=None, initial_ranks=(0, 1)
):
    d = list(data)
    g = [1] * len(data) if g_values is None else list(g_values)
    basis = [[[1], [0]], [[0], [1]]]
    rank1, rank2 = initial_ranks
    history, rank_exceptions = 0, 0
    ratios = []

    for j, point in enumerate(points):
        dj, gj = d[j], g[j]
        swap = gj == 0 or (dj != 0 and rank1 < rank2)
        history |= int(swap) << j
        rank_exceptions |= int(swap != (rank1 < rank2)) << j

        if swap:
            assert dj != 0
            ratio = fma.gf_mul(
                gj, fma.gf_inv(dj, modulus, degree), modulus, degree
            )
            ratios.append(ratio)
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
            ratios.append(ratio)
            step = [[[1], [ratio]], [[0], [point, 1]]]
            for i in range(j + 1, len(points)):
                old_d, old_g = d[i], g[i]
                d[i] = old_d ^ fma.gf_mul(ratio, old_g, modulus, degree)
                g[i] = fma.gf_mul(points[i] ^ point, old_g, modulus, degree)
            rank2 += 2

        basis = fma.matrix_mul(step, basis, mul)

    return d, g, history, rank_exceptions, basis, tuple(ratios), (rank1, rank2)


def replayed_ratios(data, points, modulus, degree):
    """Overwrite each sample with its ratio and replay prior branch updates."""
    state, branches = list(data), []
    rank1, rank2 = 0, 1
    pair_products, rank_exceptions = 0, 0

    for j, point in enumerate(points):
        d, g = state[j], 1
        for k in range(j):
            ratio = state[k]
            delta = points[j] ^ points[k]
            old_d = d
            if branches[k]:
                d = fma.gf_mul(ratio, old_d, modulus, degree) ^ g
                g = fma.gf_mul(delta, old_d, modulus, degree)
            else:
                d ^= fma.gf_mul(ratio, g, modulus, degree)
                g = fma.gf_mul(delta, g, modulus, degree)
            pair_products += 1

        assert d or g
        swap = g == 0 or (d != 0 and rank1 < rank2)
        rank_exceptions |= int(swap != (rank1 < rank2)) << j
        if swap:
            assert d != 0
            ratio = fma.gf_mul(
                g, fma.gf_inv(d, modulus, degree), modulus, degree
            )
            rank1, rank2 = rank2, rank1 + 2
        else:
            assert g != 0
            ratio = fma.gf_mul(
                d, fma.gf_inv(g, modulus, degree), modulus, degree
            )
            rank2 += 2
        state[j] = ratio
        branches.append(swap)

    return tuple(state), tuple(branches), pair_products, rank_exceptions


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
    (
        _, _, history, rank_exceptions, candidate, ratios, final_ranks
    ) = normalized_state(data, points, mul, modulus, degree)
    replay, replay_history, pair_products, replay_exceptions = replayed_ratios(
        data, points, modulus, degree
    )
    assert (replay, replay_history) == (ratios, tuple(
        (history >> j) & 1 for j in range(len(points))
    ))
    assert pair_products == len(points) * (len(points) - 1) // 2
    assert rank_exceptions == replay_exceptions
    assert history == fma.sequential_state(data, points, mul)[2]
    fma.assert_basis(data, [1] * len(points), points, candidate, mul)
    assert sorted(fma.row_rank(reference, row) for row in range(2)) == sorted(
        fma.row_rank(candidate, row) for row in range(2)
    )
    assert normalized_low_row(reference, mul, modulus, degree) == (
        normalized_low_row(candidate, mul, modulus, degree)
    )
    return ratios, replay_history, rank_exceptions, final_ranks


def screen_gf8_four_samples():
    degree, modulus, points = 3, 0b1011, list(range(4))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    cases = 0
    ratio_fibers = {}
    ratio_history_fibers = {}
    ratio_rank_fibers = {}
    exception_histogram = {}
    for data in product(range(1 << degree), repeat=len(points)):
        ratios, history, exception_mask, final_ranks = compare_to_reference(
            data, points, mul, modulus, degree
        )
        fiber = ratio_fibers.setdefault(ratios, [0, set()])
        fiber[0] += 1
        fiber[1].add(history)
        ratio_history_fibers[(ratios, history)] = (
            ratio_history_fibers.get((ratios, history), 0) + 1
        )
        ratio_rank_fibers.setdefault((ratios, final_ranks[0]), []).append(history)
        exception_count = exception_mask.bit_count()
        exception_histogram[exception_count] = (
            exception_histogram.get(exception_count, 0) + 1
        )
        cases += 1
    ambiguous_ratio_rank_states = [
        values for values in ratio_rank_fibers.values() if len(values) > 1
    ]
    bit_one_resolves_all = all(
        len({history[1] for history in values}) == len(values)
        for values in ratio_rank_fibers.values()
    )
    assert max(map(len, ratio_rank_fibers.values())) == 2
    assert bit_one_resolves_all
    return {
        "cases": cases,
        "distinct_ratio_vectors": len(ratio_fibers),
        "maximum_input_fiber": max(fiber[0] for fiber in ratio_fibers.values()),
        "maximum_branch_histories_per_ratio_vector": max(
            len(fiber[1]) for fiber in ratio_fibers.values()
        ),
        "ratio_vector_is_injective": len(ratio_fibers) == cases,
        "distinct_ratio_history_pairs": len(ratio_history_fibers),
        "maximum_input_fiber_from_ratio_history": max(
            ratio_history_fibers.values()
        ),
        "ratio_and_history_are_injective": len(ratio_history_fibers) == cases,
        "ratio_plus_final_rank_states": len(ratio_rank_fibers),
        "ratio_plus_final_rank_ambiguous_states": len(
            ambiguous_ratio_rank_states
        ),
        "maximum_inputs_per_ratio_plus_final_rank": max(
            len(values) for values in ratio_rank_fibers.values()
        ),
        "branch_bit_1_resolves_all_ratio_plus_rank_collisions": (
            bit_one_resolves_all
        ),
        "max_rank_rule_exceptions": max(exception_histogram),
        "rank_rule_exception_histogram": {
            str(count): exception_histogram[count]
            for count in sorted(exception_histogram)
        },
        "replayed_pair_products_per_case": len(points) * (len(points) - 1) // 2,
    }


def screen_gf8_valid_eight_point_patterns():
    """Measure branch-label multiplicity on every valid GF(8), n=8 error."""
    degree, modulus, points = 3, 0b1011, list(range(8))
    q = 1 << degree
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    ratio_rank_fibers = {}
    ratio_history_states = set()
    patterns = 0

    for weight in range(len(points) // 2 + 1):
        for locations in combinations(range(1, q), weight):
            for magnitudes in product(range(1, q), repeat=weight):
                syndrome = [0] * len(points)
                for location, magnitude in zip(locations, magnitudes):
                    power = location
                    for index in range(len(points)):
                        syndrome[index] ^= mul(magnitude, power)
                        power = mul(power, location)
                data = fma.syndrome_to_fma_samples(syndrome, points, mul)
                _, _, history, _, _, ratios, final_ranks = normalized_state(
                    data, points, mul, modulus, degree
                )
                key = (tuple(ratios), final_ranks[0])
                ratio_rank_fibers.setdefault(key, []).append(history)
                ratio_history_states.add((tuple(ratios), history))
                patterns += 1

    maximum_fiber = max(map(len, ratio_rank_fibers.values()))
    ambiguous_states = sum(
        len(values) > 1 for values in ratio_rank_fibers.values()
    )
    single_branch_bits_that_resolve_all = [
        bit
        for bit in range(len(points))
        if all(
            len({(history >> bit) & 1 for history in values}) == len(values)
            for values in ratio_rank_fibers.values()
        )
    ]
    assert patterns == 97_119
    assert len(ratio_history_states) == patterns
    return {
        "patterns": patterns,
        "distinct_ratio_plus_final_rank_states": len(ratio_rank_fibers),
        "ambiguous_ratio_plus_final_rank_states": ambiguous_states,
        "maximum_inputs_per_ratio_plus_final_rank": maximum_fiber,
        "minimum_fixed_tag_bits_from_maximum_fiber": (maximum_fiber - 1).bit_length(),
        "single_branch_bits_that_resolve_all_collisions": (
            single_branch_bits_that_resolve_all
        ),
        "ratio_plus_full_history_is_injective": (
            len(ratio_history_states) == patterns
        ),
    }


def screen_gf8_transformed_four_point_blocks():
    """Screen ratio/rank fibers after a sampled left-basis transformation."""
    degree, modulus = 3, 0b1011
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    left_points, right_points = list(range(4)), list(range(4, 8))
    rng = Random(0xB10C4)
    left_cases = [
        tuple(rng.randrange(1 << degree) for _ in left_points)
        for _ in range(16)
    ]
    checked_cases = 0
    worst_fiber = 0
    setup_cases_with_fiber_over_two = 0
    common_branch_tags = set(range(len(right_points)))

    for left_data in left_cases:
        basis = fma.modular_basis(left_data, left_points, mul)
        transforms = [
            tuple(fma.poly_eval(poly, point, mul) for row in basis for poly in row)
            for point in right_points
        ]
        for start_rank in range(10):
            fibers = {}
            ratio_history_states = set()
            for original in product(range(1 << degree), repeat=len(right_points)):
                transformed_d, transformed_g = [], []
                for value, (a, b, c, d) in zip(original, transforms):
                    transformed_d.append(mul(a, value) ^ b)
                    transformed_g.append(mul(c, value) ^ d)
                _, _, history, _, _, ratios, final_ranks = normalized_state(
                    transformed_d,
                    right_points,
                    mul,
                    modulus,
                    degree,
                    g_values=transformed_g,
                    initial_ranks=(start_rank, 9 - start_rank),
                )
                fibers.setdefault((ratios, final_ranks[0]), []).append(history)
                ratio_history_states.add((ratios, history))
                checked_cases += 1

            maximum_fiber = max(map(len, fibers.values()))
            worst_fiber = max(worst_fiber, maximum_fiber)
            setup_cases_with_fiber_over_two += maximum_fiber > 2
            assert len(ratio_history_states) == 1 << (degree * len(right_points))
            branch_tags = {
                bit
                for bit in range(len(right_points))
                if all(
                    len({(history >> bit) & 1 for history in histories})
                    == len(histories)
                    for histories in fibers.values()
                )
            }
            common_branch_tags &= branch_tags

    return {
        "left_basis_cases": len(left_cases),
        "start_rank_values_per_basis": 10,
        "right_inputs_per_setup": 1 << (degree * len(right_points)),
        "checked_cases": checked_cases,
        "maximum_inputs_per_ratio_plus_final_rank": worst_fiber,
        "minimum_fixed_tag_bits_from_maximum_fiber": (worst_fiber - 1).bit_length(),
        "setup_cases_with_fiber_over_two": setup_cases_with_fiber_over_two,
        "single_branch_bits_that_resolve_all_setups": sorted(common_branch_tags),
        "ratio_plus_full_history_injective_in_each_setup": True,
        "left_sample_seed": "0xB10C4",
        "scope": (
            "16 sampled pristine four-point left blocks over GF(8), each applied "
            "to all 4,096 right four-sample inputs at each valid rank1 value "
            "with rank1+rank2=9. This does not bound GF(2^12) or 70-point fibers."
        ),
    }


def screen_gf12_dqi_samples():
    degree, modulus, points = 12, 0x1053, list(range(70))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    rng = Random(0xF1A053)
    cases = 0
    per_weight = 16
    zero_ratios_by_weight = {}
    rank_exceptions_by_weight = {}
    exception_masks_by_final_rank = {}

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
            ratios, _, rank_exception_mask, final_ranks = compare_to_reference(
                data, points, mul, modulus, degree
            )
            zero_ratios_by_weight.setdefault(weight, []).append(
                sum(ratio == 0 for ratio in ratios)
            )
            rank_exceptions_by_weight.setdefault(weight, set()).add(
                rank_exception_mask
            )
            exception_masks_by_final_rank.setdefault(weight, {}).setdefault(
                final_ranks, set()
            ).add(rank_exception_mask)
            cases += 1

    return {
        "cases": cases,
        "per_error_weight": per_weight,
        "weights": [1, 31, 35],
        "replayed_pair_products_per_case": len(points) * (len(points) - 1) // 2,
        "max_zero_ratios_by_weight": {
            str(weight): max(counts)
            for weight, counts in zero_ratios_by_weight.items()
        },
        "max_rank_rule_exceptions_by_weight": {
            str(weight): max(mask.bit_count() for mask in masks)
            for weight, masks in rank_exceptions_by_weight.items()
        },
        "distinct_rank_rule_exception_masks_by_weight": {
            str(weight): len(masks)
            for weight, masks in rank_exceptions_by_weight.items()
        },
        "distinct_final_rank_pairs_by_weight": {
            str(weight): len(by_rank)
            for weight, by_rank in exception_masks_by_final_rank.items()
        },
        "exception_mask_unique_for_final_rank_by_weight": {
            str(weight): all(len(masks) == 1 for masks in by_rank.values())
            for weight, by_rank in exception_masks_by_final_rank.items()
        },
        "rank_rule_exception_masks_hex_by_weight": {
            str(weight): [hex(mask) for mask in sorted(masks)]
            for weight, masks in rank_exceptions_by_weight.items()
        },
    }


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
    rank = builder.alloc_qubits(8)
    branch_register = builder.alloc_qubits(1)
    branch = branch_register[0]
    ratio = builder.alloc_qubits(12)

    pivot_d, pivot_g = payload[:12], payload[12:24]
    pair_d, pair_g = payload[24:36], payload[36:48]

    # Canonicalize either FMA branch to (d, g), compute d/g, then restore it.
    builder.cswap(branch, pivot_d, pivot_g)
    inverse_transcript = ar.inverse_inplace_forward(builder, pivot_g)
    ar.mul_xor(builder, pivot_d, pivot_g, ratio)

    # The swap branch pre-swaps the input pair so the shared update returns
    # the FMA-ordered output without a second swap.
    builder.cswap(branch, pair_d, pair_g)
    ar.mul_xor(builder, ratio, pair_g, pair_d)
    builder.gf2_imul(delta, target=pair_g, field=ar.field(12))

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
    sim.write_across_shots(regs["rank"], np.zeros((8, len(cases)), dtype=np.bool_))
    sim.do(circuit)

    expected_d, expected_g = [], []
    for branch, pivot_d, pivot_g, pair_d, pair_g in cases:
        numerator, denominator = (pivot_g, pivot_d) if branch else (pivot_d, pivot_g)
        ratio = mul(numerator, fma.gf_inv(denominator, modulus, degree))
        if branch:
            expected_d.append(pair_g ^ mul(ratio, pair_d))
            expected_g.append(mul(delta, pair_d))
        else:
            expected_d.append(pair_d ^ mul(ratio, pair_g))
            expected_g.append(mul(delta, pair_g))

    for name in ("pivot_d", "pivot_g"):
        assert np.array_equal(
            sim.read_across_shots(regs[name]), bit_columns(values[name], degree)
        )
    assert np.array_equal(sim.read_across_shots(regs["pair_d"]), bit_columns(expected_d, degree))
    assert np.array_equal(sim.read_across_shots(regs["pair_g"]), bit_columns(expected_g, degree))
    assert np.array_equal(sim.read_across_shots(regs["rank"]), np.zeros((8, len(cases)), dtype=np.bool_))
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


def resource_screen(pair_cell):
    points = 70
    pair_updates = points * (points - 1) // 2
    ratio_products = points
    ratio_cleanup_products = points
    inversions = points
    products = pair_updates + ratio_products + ratio_cleanup_products
    product_t = 42
    inverse_forward_t, inverse_restore_t = 66, 72
    pair_cswaps_t, pivot_cswaps_t = 12, 24
    fma_t = (
        products * product_t
        + pair_updates * pair_cswaps_t
        + inversions * (inverse_forward_t + inverse_restore_t + pivot_cswaps_t)
    )
    scan_t, branch_rank_t = 45_045, 4_830
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
        "single_pair_cell_qubits": pair_cell["compiled_qubits"],
        "single_pair_cell_toffolis": pair_cell["toffoli_like_gates"],
        "scope": (
            "Count projection includes ratio cleanup, branch-controlled pair input swaps, and the "
            "measured in-place inverse cell. It assumes the existing sampled reconstruction, scan, and "
            "branch/rank costs. It excludes the 4+66 width schedule and any uncounted phase work."
        ),
    }


def main():
    gf8 = screen_gf8_four_samples()
    gf12 = screen_gf12_dqi_samples()
    pair_cell = check_normalized_pair_cell()
    result = {
        "experiment": "exp-053",
        "result": "PASS",
        "gf8_eight_point_branch_label_screen": (
            screen_gf8_valid_eight_point_patterns()
        ),
        "gf8_transformed_four_point_block_screen": (
            screen_gf8_transformed_four_point_blocks()
        ),
        "normalized_fma_screen": {
            "gf8_all_four_sample_vectors": gf8["cases"],
            "gf8_ratio_replay": gf8,
            "gf12_valid_70_symbol_samples": gf12,
            "branch_history_matches_reference": True,
            "row_ranks_match_reference": True,
            "normalized_low_row_matches_reference": True,
        },
        "compiled_pair_cell": pair_cell,
        "resource_screen": resource_screen(pair_cell),
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
