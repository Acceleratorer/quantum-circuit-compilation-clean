"""Screen compact state needed to recover FMA branch history.

Exhaustively checks every GF(8), eight-point error pattern through weight four,
including all nonzero magnitude assignments, exact full-basis matrices, a 4+4
compact recovery state, and every arbitrary four-sample GF(8) input with both
explicit exceptions and a fused factorized state.
"""

from __future__ import annotations

from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def recover_pristine_samples(low_row, exceptions, points, mul, modulus, degree):
    """Recover the left FMA samples from its low row and correction labels."""
    gcd, _, _ = fma.poly_xgcd(
        low_row[0], low_row[1], mul, modulus, degree
    )
    w_reduced, remainder = fma.poly_divmod(
        low_row[0], gcd, mul, modulus, degree
    )
    assert remainder == [0]
    n_reduced, remainder = fma.poly_divmod(
        low_row[1], gcd, mul, modulus, degree
    )
    assert remainder == [0]
    exception_values = {
        index: d_value for index, d_value, _ in exceptions
    }

    recovered = []
    for index, point in enumerate(points):
        w_value = fma.poly_eval(low_row[0], point, mul)
        n_value = fma.poly_eval(low_row[1], point, mul)
        if w_value:
            recovered.append(mul(n_value, fma.gf_inv(w_value, modulus, degree)))
            continue

        assert n_value == 0
        if index in exception_values:
            recovered.append(exception_values[index])
            continue

        w_value = fma.poly_eval(w_reduced, point, mul)
        n_value = fma.poly_eval(n_reduced, point, mul)
        assert w_value != 0
        recovered.append(mul(n_value, fma.gf_inv(w_value, modulus, degree)))

    return recovered


def arbitrary_four_sample_exception_screen():
    """Exhaust all pristine GF(8) samples at the first four FMA points."""
    degree, modulus = 3, 0b1011
    q = 1 << degree
    points = list(range(4))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    node_polynomial = [1]
    for point in points:
        node_polynomial = fma.poly_mul(node_polynomial, [point, 1], mul)
    exception_counts = {}
    compact_states = {}
    common_root_counts = {}
    factorized_word_counts = {}
    factorized_states = {}
    recovered_inputs = 0
    state_collisions = 0
    factorized_state_collisions = 0
    maximum_exceptions = 0
    maximum_common_roots = 0
    maximum_factorized_words = 0

    for encoded in range(q ** len(points)):
        data = [
            (encoded >> (degree * index)) & (q - 1)
            for index in range(len(points))
        ]
        basis = fma.modular_basis(data, points, mul)
        low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
        low_row = [fma.trim(list(poly)) for poly in basis[low_index]]
        pivot = low_row[0][-1] if low_row[0] != [0] else low_row[1][-1]
        scale = fma.gf_inv(pivot, modulus, degree)
        low_row = tuple(
            tuple(fma.trim([mul(scale, value) for value in poly]))
            for poly in low_row
        )

        _, _, exceptions = fma.reconstruct_complementary_row(
            low_row, data, points, mul, modulus, degree
        )
        recovered = recover_pristine_samples(
            low_row, exceptions, points, mul, modulus, degree
        )
        assert recovered == data
        recovered_inputs += 1

        exception_state = tuple(
            (index, d_value) for index, d_value, _ in exceptions
        )
        state = (low_row, exception_state)
        prior_input = compact_states.get(state)
        if prior_input is not None and prior_input != tuple(data):
            state_collisions += 1
        else:
            compact_states[state] = tuple(data)

        count = len(exceptions)
        maximum_exceptions = max(maximum_exceptions, count)
        exception_counts[str(count)] = exception_counts.get(str(count), 0) + 1

        gcd, _, _ = fma.poly_xgcd(
            low_row[0], low_row[1], mul, modulus, degree
        )
        assert gcd[-1] == 1
        _, remainder = fma.poly_divmod(
            node_polynomial, gcd, mul, modulus, degree
        )
        assert remainder == [0]
        a, remainder = fma.poly_divmod(
            low_row[0], gcd, mul, modulus, degree
        )
        assert remainder == [0]
        b, remainder = fma.poly_divmod(
            low_row[1], gcd, mul, modulus, degree
        )
        assert remainder == [0]
        common_roots = [
            index
            for index, point in enumerate(points)
            if fma.poly_eval(gcd, point, mul) == 0
        ]
        root_samples = tuple(data[index] for index in common_roots)
        root_records = [
            (index, data[index], 1) for index in common_roots
        ]
        assert recover_pristine_samples(
            low_row, root_records, points, mul, modulus, degree
        ) == data

        factorized_state = (
            tuple(gcd), tuple(a), tuple(b), root_samples
        )
        prior_input = factorized_states.get(factorized_state)
        if prior_input is not None and prior_input != tuple(data):
            factorized_state_collisions += 1
        else:
            factorized_states[factorized_state] = tuple(data)

        # G is monic. Omit A's leading word only when that word is fixed at 1.
        g_words = len(gcd) - 1
        a_words = (
            0
            if a == [0]
            else len(a) - int(a[-1] == 1)
        )
        b_words = 0 if b == [0] else len(b)
        factorized_words = g_words + a_words + b_words + len(root_samples)
        maximum_factorized_words = max(
            maximum_factorized_words, factorized_words
        )
        factorized_word_counts[str(factorized_words)] = (
            factorized_word_counts.get(str(factorized_words), 0) + 1
        )
        maximum_common_roots = max(maximum_common_roots, len(common_roots))
        common_root_counts[str(len(common_roots))] = (
            common_root_counts.get(str(len(common_roots)), 0) + 1
        )

    assert recovered_inputs == q ** len(points)
    assert len(compact_states) == recovered_inputs
    assert len(factorized_states) == recovered_inputs
    assert state_collisions == 0
    assert factorized_state_collisions == 0
    assert maximum_exceptions <= 2
    assert maximum_common_roots <= 2
    assert maximum_factorized_words <= len(points)
    return {
        "field": "GF(8)",
        "points": points,
        "input_domain": "all pristine four-sample d vectors; g_i=1",
        "cases": q ** len(points),
        "recovered_inputs": recovered_inputs,
        "distinct_compact_states": len(compact_states),
        "state_collisions": state_collisions,
        "exception_sample_count_distribution": exception_counts,
        "maximum_exception_samples": maximum_exceptions,
        "result": "normalized_low_row_and_exceptions_recover_all_inputs",
        "fused_factorized_state": {
            "components": [
                "monic gcd G coefficients without the fixed leading 1",
                "cofactor A=W/G coefficients",
                "cofactor B=N/G coefficients",
                "original d samples at common roots of G among the four points",
            ],
            "common_root_locations_derived_from_gcd": True,
            "gcd_divides_four_point_node_polynomial": True,
            "cases": q ** len(points),
            "distinct_states": len(factorized_states),
            "state_collisions": factorized_state_collisions,
            "common_root_sample_count_distribution": common_root_counts,
            "maximum_common_root_samples": maximum_common_roots,
            "field_word_count_distribution": factorized_word_counts,
            "maximum_field_words": maximum_factorized_words,
            "result": "factorized_row_and_root_samples_recover_all_inputs",
            "scope": (
                "Exhaustive GF(8) information screen. The state has at most "
                "four field words on this domain; polynomial degree framing "
                "and an in-place reversible encoder are not implemented."
            ),
        },
        "scope": (
            "Exhaustive information screen over all 4,096 GF(8) d vectors "
            "at points 0,1,2,3 with pristine g_i=1. It is not a reversible "
            "GF(2^12) circuit or a 70-point resource bound."
        ),
    }


def screen():
    degree, modulus = 3, 0b1011
    q = 1 << degree
    points = list(range(q))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    report = []
    total_patterns = 0
    row_histories = {}
    basis_histories = {}
    left_state_histories = {}
    compact_state_histories = {}
    exception_counts = {}
    history_recovery_checks = 0

    for weight in range(len(points) // 2 + 1):
        supports = 0
        multiple_histories = 0
        max_histories = 1

        for support in combinations(range(1, q), weight):
            histories = set()
            for magnitudes in product(range(1, q), repeat=weight):
                syndrome = [0] * len(points)
                for beta, magnitude in zip(support, magnitudes):
                    power = beta
                    for index in range(len(points)):
                        syndrome[index] ^= mul(magnitude, power)
                        power = mul(power, beta)

                d = fma.syndrome_to_fma_samples(syndrome, points, mul)
                original_d = list(d)
                g = [1] * len(points)
                rank1, rank2 = 0, 1
                history = 0
                basis = [[[1], [0]], [[0], [1]]]
                left_basis = None
                left_history = None

                for step in range(len(points)):
                    pivot_d, pivot_g = d[step], g[step]
                    swap = pivot_g == 0 or (pivot_d != 0 and rank1 < rank2)
                    x_minus_point = [points[step], 1]
                    zero = [0]
                    step_matrix = (
                        [[[pivot_g], [pivot_d]], [x_minus_point, zero]]
                        if swap
                        else [[[pivot_g], [pivot_d]], [zero, x_minus_point]]
                    )
                    basis = fma.matrix_mul(step_matrix, basis, mul)
                    if swap:
                        rank1, rank2 = rank2, rank1 + 2
                        history |= 1 << step
                    else:
                        rank2 += 2
                    if step == 3:
                        left_basis = [
                            [list(poly) for poly in row] for row in basis
                        ]
                        left_history = history

                    for index in range(step + 1, len(points)):
                        old_d, old_g = d[index], g[index]
                        d[index] = mul(pivot_g, old_d) ^ mul(pivot_d, old_g)
                        g[index] = mul(
                            points[index] ^ points[step], old_d if swap else old_g
                        )

                low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
                low = [fma.trim(list(poly)) for poly in basis[low_index]]
                pivot = low[0][-1] if low[0] != [0] else low[1][-1]
                scale = fma.gf_inv(pivot, modulus, degree)
                low_row = tuple(
                    tuple(fma.trim([mul(scale, value) for value in poly]))
                    for poly in low
                )
                row_histories.setdefault(low_row, set()).add(history)

                basis_key = tuple(
                    tuple(tuple(fma.trim(list(poly))) for poly in row)
                    for row in basis
                )
                basis_histories.setdefault(basis_key, set()).add(history)

                left_low_index = min(
                    range(2), key=lambda i: fma.row_rank(left_basis, i)
                )
                left_low = [
                    fma.trim(list(poly)) for poly in left_basis[left_low_index]
                ]
                left_pivot = (
                    left_low[0][-1] if left_low[0] != [0] else left_low[1][-1]
                )
                left_scale = fma.gf_inv(left_pivot, modulus, degree)
                left_low = tuple(
                    tuple(fma.trim([mul(left_scale, value) for value in poly]))
                    for poly in left_low
                )
                _, _, exceptions = fma.reconstruct_complementary_row(
                    left_low, original_d[:4], points[:4], mul, modulus, degree
                )
                exception_state = tuple(
                    (index, d_value) for index, d_value, _ in exceptions
                )
                recovered_left = recover_pristine_samples(
                    left_low, exceptions, points[:4], mul, modulus, degree
                )
                assert recovered_left == original_d[:4]
                recovered_history = fma.sequential_state(
                    recovered_left, points[:4], mul
                )[2]
                assert recovered_history == left_history
                history_recovery_checks += 1
                exception_counts[len(exceptions)] = (
                    exception_counts.get(len(exceptions), 0) + 1
                )
                left_state = (left_low, exception_state)
                left_state_histories.setdefault(left_state, set()).add(
                    left_history
                )
                compact_state = (
                    left_low,
                    exception_state,
                    tuple(original_d[4:]),
                )
                compact_state_histories.setdefault(compact_state, set()).add(
                    left_history
                )

                histories.add(history)

            supports += 1
            total_patterns += (q - 1) ** weight
            max_histories = max(max_histories, len(histories))
            multiple_histories += len(histories) > 1

        report.append(
            {
                "weight": weight,
                "supports": supports,
                "supports_with_multiple_branch_histories": multiple_histories,
                "max_histories_for_one_support": max_histories,
            }
        )

    assert total_patterns == 97_119
    multi_history_rows = [
        (row, histories)
        for row, histories in row_histories.items()
        if len(histories) > 1
    ]
    witness_row, witness_histories = max(
        multi_history_rows, key=lambda item: len(item[1])
    )
    multi_history_bases = [
        histories for histories in basis_histories.values() if len(histories) > 1
    ]
    multi_history_compact_states = [
        histories
        for histories in compact_state_histories.values()
        if len(histories) > 1
    ]
    multi_history_left_states = [
        histories
        for histories in left_state_histories.values()
        if len(histories) > 1
    ]
    max_left_state_histories = max(
        (len(histories) for histories in left_state_histories.values()),
        default=0,
    )
    max_compact_histories = max(
        (len(histories) for histories in compact_state_histories.values()),
        default=0,
    )
    return {
        "experiment": "exp-052-locator-history",
        "field": "GF(8)",
        "points": len(points),
        "valid_patterns": total_patterns,
        "result": "locator_support_alone_is_insufficient",
        "report": report,
        "final_normalized_low_row": {
            "unique_rows": len(row_histories),
            "rows_with_multiple_branch_histories": len(multi_history_rows),
            "max_histories_for_one_row": len(witness_histories),
            "max_history_witness": {
                "row": [list(poly) for poly in witness_row],
                "histories": sorted(witness_histories),
            },
            "result": "the_final_low_row_alone_does_not_determine_branch_history",
        },
        "final_basis_matrix": {
            "unique_matrices": len(basis_histories),
            "matrices_with_multiple_branch_histories": len(multi_history_bases),
            "max_histories_for_one_matrix": max(
                (len(histories) for histories in basis_histories.values()),
                default=0,
            ),
            "result": (
                "the_exact_full_basis_alone_determines_branch_history"
                if not multi_history_bases
                else "the_exact_full_basis_alone_does_not_determine_branch_history"
            ),
        },
        "split_4_plus_4_compact_state": {
            "left_recovery_state": {
                "state_components": [
                    "normalized left low row",
                    "left common-zero exception samples",
                ],
                "states": len(left_state_histories),
                "states_with_multiple_left_branch_histories": len(
                    multi_history_left_states
                ),
                "max_left_histories_for_one_state": max_left_state_histories,
                "minimum_extra_history_bits_for_max_fiber": (
                    max_left_state_histories - 1
                ).bit_length(),
                "direct_sample_recovery_checks": history_recovery_checks,
                "exception_sample_count_distribution": exception_counts,
                "result": (
                    "left_low_row_and_exceptions_recover_branch_history"
                    if not multi_history_left_states
                    else "left_low_row_and_exceptions_need_a_history_label"
                ),
            },
            "state_components": [
                "normalized left low row",
                "left common-zero exception samples",
                "right pristine d samples",
            ],
            "states": len(compact_state_histories),
            "states_with_multiple_left_branch_histories": len(
                multi_history_compact_states
            ),
            "max_left_histories_for_one_state": max_compact_histories,
            "minimum_extra_history_bits_for_max_fiber": (
                max_compact_histories - 1
            ).bit_length(),
            "result": (
                "compact_state_determines_left_branch_history"
                if not multi_history_compact_states
                else "compact_state_alone_does_not_determine_left_branch_history"
            ),
            "scope": (
                "Exact for all 97,119 valid GF(8), eight-point error patterns "
                "through weight 4 at split 4+4. This is an information screen, "
                "not a reversible circuit or GF(2^12) width bound."
            ),
        },
        "arbitrary_four_sample_exception_screen": (
            arbitrary_four_sample_exception_screen()
        ),
        "scope": (
            "Exact for all GF(8), eight-point error patterns through weight 4. "
            "Across all 97,119 cases, 99 normalized final low rows occurred; "
            "eight were associated with multiple branch histories (up to "
            "five). The final low row alone therefore does not recover the "
            "history. This is not a 70-point GF(2^12) circuit or Toffoli "
            "bound."
        ),
    }


if __name__ == "__main__":
    if sys.argv[1:] == ["--four-sample-exceptions"]:
        result = arbitrary_four_sample_exception_screen()
    elif not sys.argv[1:]:
        result = screen()
    else:
        raise SystemExit("usage: fma_locator_history.py [--four-sample-exceptions]")
    print(json.dumps(result, indent=2, sort_keys=True))
