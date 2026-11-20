"""Screen classical recovery work for a compact four-point FMA state.

This counts field-arithmetic calls in the existing classical reconstruction
path over every GF(8) four-sample input. The GF(2^12) Toffoli figure is an
arithmetic-only proxy; it is not a compiled reversible circuit or a bound on
workspace, control, phase, or cleanup costs.
"""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
from random import Random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-052"))
import fma_state_compression as fma  # noqa: E402
from fma_locator_history import recover_factorized_samples  # noqa: E402


# At low-row rank <=4, W=0 would force deg(N)<=1 while N vanishes at all four
# public points. Thus W/G is nonzero and monic after the low row is normalized.
FACTOR_SHAPES = tuple(
    (gcd_degree, degree_a, degree_b)
    for gcd_degree in range(3)
    for degree_a in range(3 - gcd_degree)
    for degree_b in range(-1, 2 - gcd_degree)
)
FACTOR_SHAPE_TO_ID = {shape: index for index, shape in enumerate(FACTOR_SHAPES)}


def factorized_word_count(shape):
    gcd_degree, degree_a, degree_b = shape
    return 2 * gcd_degree + degree_a + max(0, degree_b + 1)


def pack_factorized_state(gcd, cofactor_w, cofactor_n, root_samples):
    """Pack the factorized polynomials and root values into four field words."""
    gcd = fma.trim(list(gcd))
    cofactor_w = fma.trim(list(cofactor_w))
    cofactor_n = fma.trim(list(cofactor_n))
    gcd_degree = len(gcd) - 1
    degree_a = len(cofactor_w) - 1
    degree_b = -1 if cofactor_n == [0] else len(cofactor_n) - 1
    shape = (gcd_degree, degree_a, degree_b)
    if gcd[-1] != 1 or cofactor_w[-1] != 1 or shape not in FACTOR_SHAPE_TO_ID:
        raise ValueError("factorized state is outside the normalized four-point domain")
    if len(root_samples) != gcd_degree:
        raise ValueError("the gcd roots and saved root samples do not match")

    words = gcd[:-1] + cofactor_w[:-1]
    if degree_b >= 0:
        words += cofactor_n
    words += list(root_samples)
    if len(words) > 4:
        raise ValueError("factorized state exceeds four field words")
    return FACTOR_SHAPE_TO_ID[shape], tuple(words + [0] * (4 - len(words)))


def unpack_factorized_state(words, shape_id):
    """Decode the four-word payload using its four-bit shape tag."""
    if len(words) != 4 or not 0 <= shape_id < len(FACTOR_SHAPES):
        raise ValueError("invalid four-word state header")
    gcd_degree, degree_a, degree_b = FACTOR_SHAPES[shape_id]
    offset = 0
    gcd = list(words[offset : offset + gcd_degree]) + [1]
    offset += gcd_degree
    cofactor_w = list(words[offset : offset + degree_a]) + [1]
    offset += degree_a
    b_words = max(0, degree_b + 1)
    cofactor_n = list(words[offset : offset + b_words]) or [0]
    offset += b_words
    root_samples = tuple(words[offset : offset + gcd_degree])
    offset += gcd_degree
    if offset > 4 or any(words[offset:]):
        raise ValueError("payload padding is not canonical")
    return gcd, cofactor_w, cofactor_n, root_samples


def rank_pair_after_history(history, steps):
    rank1, rank2 = 0, 1
    for index in range(steps):
        if history >> index & 1:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2
    return rank1, rank2


def screen_gf12_codec(samples=2048):
    degree, modulus, points = 12, 0x1053, list(range(4))
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    rng = Random(0x4D5156)
    labels = {}
    shapes = set()
    maximum_words = 0
    maximum_rank1 = 0
    label_collisions = 0

    for _ in range(samples):
        data = tuple(rng.randrange(1 << degree) for _ in points)
        basis = fma.modular_basis(data, points, mul)
        low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
        row = [fma.trim(list(poly)) for poly in basis[low_index]]
        pivot = row[0][-1] if row[0] != [0] else row[1][-1]
        scale = fma.gf_inv(pivot, modulus, degree)
        row = tuple(
            tuple(fma.trim([mul(scale, value) for value in poly]))
            for poly in row
        )
        gcd, _, _ = fma.poly_xgcd(row[0], row[1], mul, modulus, degree)
        cofactor_w, remainder = fma.poly_divmod(
            row[0], gcd, mul, modulus, degree
        )
        assert remainder == [0]
        cofactor_n, remainder = fma.poly_divmod(
            row[1], gcd, mul, modulus, degree
        )
        assert remainder == [0]
        root_samples = tuple(
            data[index]
            for index, point in enumerate(points)
            if fma.poly_eval(gcd, point, mul) == 0
        )
        shape_id, words = pack_factorized_state(
            gcd, cofactor_w, cofactor_n, root_samples
        )
        decoded = unpack_factorized_state(words, shape_id)
        assert recover_factorized_samples(
            *decoded, points, mul, modulus, degree
        ) == list(data)
        history = fma.sequential_state(data, points, mul)[2]
        rank1, rank2 = rank_pair_after_history(history, len(points))
        assert rank1 + rank2 == 2 * len(points) + 1
        label = (shape_id, words)
        prior_input = labels.get(label)
        if prior_input is not None and prior_input != data:
            label_collisions += 1
        else:
            labels[label] = data
        shapes.add(shape_id)
        gcd_degree, degree_a, degree_b = FACTOR_SHAPES[shape_id]
        word_count = factorized_word_count(FACTOR_SHAPES[shape_id])
        maximum_words = max(maximum_words, word_count)
        maximum_rank1 = max(maximum_rank1, rank1)

    assert label_collisions == 0
    rank1_headroom = 8 - maximum_rank1.bit_length()
    shape_tag_bits = (len(FACTOR_SHAPES) - 1).bit_length()
    assert shape_tag_bits <= rank1_headroom
    return {
        "seeded_inputs_checked": samples,
        "distinct_packed_labels": len(labels),
        "packed_label_collisions": label_collisions,
        "observed_shapes": len(shapes),
        "maximum_field_words": maximum_words,
        "maximum_rank1_after_four_points": maximum_rank1,
        "rank1_unused_high_bits": rank1_headroom,
        "shape_tag_fits_rank1_headroom": True,
        "scope": "Seeded sample only; not an exhaustive GF(2^12) proof or a reversible circuit.",
    }


def screen() -> dict[str, object]:
    degree, modulus = 3, 0b1011
    points = list(range(4))
    original_mul = fma.gf_mul
    original_inv = fma.gf_inv
    inverse_body = original_inv.__wrapped__
    counts = {"field_multiply_calls": 0, "inverse_calls": 0}

    def counted_mul(left: int, right: int, mod: int, bits: int) -> int:
        counts["field_multiply_calls"] += 1
        return original_mul(left, right, mod, bits)

    def counted_inv(value: int, mod: int, bits: int) -> int:
        counts["inverse_calls"] += 1
        current_mul = fma.gf_mul
        fma.gf_mul = original_mul
        try:
            return inverse_body(value, mod, bits)
        finally:
            fma.gf_mul = current_mul

    fma.gf_mul = counted_mul
    fma.gf_inv = counted_inv
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    records = []
    packed_labels = {}
    shape_counts = {}
    packed_collisions = 0
    max_rank1 = 0
    max_basis_words = 0
    max_basis_example = None
    try:
        for data in product(range(1 << degree), repeat=len(points)):
            basis = fma.modular_basis(data, points, mul)
            basis_lengths = [
                [len(fma.trim(list(poly))) for poly in row] for row in basis
            ]
            basis_words = sum(map(sum, basis_lengths))
            if basis_words > max_basis_words:
                max_basis_words = basis_words
                max_basis_example = {
                    "input": list(data),
                    "row_polynomial_lengths": basis_lengths,
                }
            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
            row = [fma.trim(list(poly)) for poly in basis[low_index]]
            pivot = row[0][-1] if row[0] != [0] else row[1][-1]
            scale = fma.gf_inv(pivot, modulus, degree)
            row = tuple(
                tuple(fma.trim([mul(scale, value) for value in poly]))
                for poly in row
            )
            normalize_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            common, _, _ = fma.poly_xgcd(row[0], row[1], mul, modulus, degree)
            cofactor_w, remainder = fma.poly_divmod(
                row[0], common, mul, modulus, degree
            )
            assert remainder == [0]
            cofactor_n, remainder = fma.poly_divmod(
                row[1], common, mul, modulus, degree
            )
            assert remainder == [0]
            root_samples = tuple(
                data[index]
                for index, point in enumerate(points)
                if fma.poly_eval(common, point, mul) == 0
            )
            factorize_operations = dict(counts)
            shape = (
                len(common) - 1,
                -1 if cofactor_w == [0] else len(cofactor_w) - 1,
                -1 if cofactor_n == [0] else len(cofactor_n) - 1,
            )
            factorized_words = factorized_word_count(shape)
            assert factorized_words <= len(points)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            recovered = recover_factorized_samples(
                common,
                cofactor_w,
                cofactor_n,
                root_samples,
                points,
                mul,
                modulus,
                degree,
            )
            decode_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            low = (
                fma.poly_mul(common, cofactor_w, mul),
                fma.poly_mul(common, cofactor_n, mul),
            )
            row_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            got_low, complement, _ = fma.reconstruct_complementary_row(
                low, recovered, points, mul, modulus, degree
            )
            complement_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            history = fma.sequential_state(recovered, points, mul)[2]
            branch_operations = dict(counts)
            shape_id, packed_words = pack_factorized_state(
                common, cofactor_w, cofactor_n, root_samples
            )
            decoded_state = unpack_factorized_state(packed_words, shape_id)
            assert decoded_state == (
                common,
                cofactor_w,
                cofactor_n,
                root_samples,
            )
            assert recover_factorized_samples(
                *decoded_state, points, mul, modulus, degree
            ) == list(data)
            label = (shape_id, packed_words)
            prior_input = packed_labels.get(label)
            if prior_input is not None and prior_input != tuple(data):
                packed_collisions += 1
            else:
                packed_labels[label] = tuple(data)
            shape = FACTOR_SHAPES[shape_id]
            shape_counts[shape] = shape_counts.get(shape, 0) + 1

            rank1, rank2 = rank_pair_after_history(history, len(points))
            assert rank1 + rank2 == 2 * len(points) + 1
            max_rank1 = max(max_rank1, rank1)

            compact_state_stages = {
                "normalize_low_row": normalize_operations,
                "factorize_low_row": factorize_operations,
                "recover_samples": decode_operations,
                "replay_branch_history": branch_operations,
            }
            compact_state_component_t = {
                name: stage["field_multiply_calls"] * 42
                + stage["inverse_calls"] * 138
                for name, stage in compact_state_stages.items()
            }
            compact_state_proxy_t = sum(compact_state_component_t.values())
            operations = {
                key: sum(
                    stage[key]
                    for stage in (
                        decode_operations,
                        row_operations,
                        complement_operations,
                        branch_operations,
                    )
                )
                for key in counts
            }
            components = {
                "decode_samples": decode_operations,
                "compose_low_row": row_operations,
                "reconstruct_complement": complement_operations,
                "replay_branch_history": branch_operations,
            }
            component_t = {
                name: stage["field_multiply_calls"] * 42
                + stage["inverse_calls"] * 138
                for name, stage in components.items()
            }
            proxy_t = sum(component_t.values())

            assert recovered == list(data)
            assert tuple(tuple(poly) for poly in got_low) == row
            assert history == fma.sequential_state(data, points, mul)[2]
            fma.assert_basis(
                recovered, [1] * len(points), points, [got_low, complement], mul
            )
            ranks = sorted(
                fma.row_rank([got_low, complement], index) for index in range(2)
            )
            assert ranks == sorted(fma.row_rank(basis, index) for index in range(2))
            records.append(
                {
                    "input": list(data),
                    "field_multiply_calls": operations["field_multiply_calls"],
                    "inverse_calls": operations["inverse_calls"],
                    "arithmetic_only_t_proxy": proxy_t,
                    "components": component_t,
                    "factorized_state_words": factorized_words,
                    "compact_history_t_proxy": compact_state_proxy_t,
                    "compact_history_components": compact_state_component_t,
                }
            )
    finally:
        fma.gf_mul = original_mul
        fma.gf_inv = original_inv

    records.sort(key=lambda record: record["arithmetic_only_t_proxy"], reverse=True)
    assert packed_collisions == 0 and len(packed_labels) == len(records)
    rank1_headroom = 8 - max_rank1.bit_length()
    shape_tag_bits = (len(FACTOR_SHAPES) - 1).bit_length()
    assert shape_tag_bits <= rank1_headroom
    costs = [record["arithmetic_only_t_proxy"] for record in records]
    compact_history_costs = sorted(
        record["compact_history_t_proxy"] for record in records
    )
    return {
        "field": "GF(8)",
        "four_sample_inputs_checked": len(records),
        "checks": [
            "factorized payload reconstructs all four input samples",
            "reconstructed complementary row satisfies the basis constraints",
            "branch history matches direct replay",
            "four-word payload and shape tag round-trip all four samples",
        ],
        "factorized_state_codec": {
            "four_sample_inputs_checked": len(records),
            "distinct_packed_labels": len(packed_labels),
            "packed_label_collisions": packed_collisions,
            "maximum_field_words": max(
                record["factorized_state_words"] for record in records
            ),
            "observed_shapes": len(shape_counts),
            "shape_catalog_size": len(FACTOR_SHAPES),
            "shape_tag_bits": shape_tag_bits,
            "shape_catalog": [
                {"id": index, "gcd_degree": shape[0], "cofactor_w_degree": shape[1], "cofactor_n_degree": shape[2]}
                for index, shape in enumerate(FACTOR_SHAPES)
            ],
            "maximum_rank1_after_four_points": max_rank1,
            "rank1_register_bits": 8,
            "rank1_unused_high_bits": rank1_headroom,
            "shape_tag_fits_rank1_headroom": True,
            "scope": (
                "Classical pack/unpack plus sample recovery across all 4,096 GF(8) "
                "four-sample inputs. The shape tag is not yet computed or cleared "
                "by a reversible circuit."
            ),
            "seeded_gf12_sample": screen_gf12_codec(),
        },
        "gf12_cost_assumptions": {
            "field_multiply_call_t": 42,
            "inverse_call_t": 138,
        },
        "maximum": records[0],
        "materialized_basis": {
            "maximum_coefficient_words": max_basis_words,
            "example": max_basis_example,
            "extra_qubits_over_four_sample_words": (max_basis_words - 4) * 12,
            "projected_payload_qubits": 840 - 48 + max_basis_words * 12,
            "qubit_limit": 890,
            "over_limit_before_workspace": 840 - 48 + max_basis_words * 12 - 890,
            "scope": "All four-sample GF(8) inputs; direct storage of every polynomial coefficient, without streaming or compression.",
        },
        "maximum_component_arithmetic_only_t_proxy": {
            name: max(record["components"][name] for record in records)
            for name in records[0]["components"]
        },
        "compact_history_round_trip": {
            "description": (
                "Normalize and factor the low row, recover the four samples from "
                "the factorized state, then replay the four-point branch history. "
                "This omits complementary-row reconstruction."
            ),
            "maximum_factorized_state_words": max(
                record["factorized_state_words"] for record in records
            ),
            "maximum_arithmetic_only_t_proxy": max(
                record["compact_history_t_proxy"] for record in records
            ),
            "median_arithmetic_only_t_proxy": compact_history_costs[
                len(compact_history_costs) // 2
            ],
            "maximum_component_t_proxy": {
                name: max(record["compact_history_components"][name] for record in records)
                for name in records[0]["compact_history_components"]
            },
            "scope": (
                "All 4,096 arbitrary GF(8) four-sample inputs. Every counted "
                "multiply call is charged 42T and every inverse 138T, including "
                "constant-coefficient multiplies that can be linear gates. This "
                "is a conservative arithmetic proxy, not a compiled reversible "
                "circuit or full 4+66 schedule."
            ),
        },
        "median_arithmetic_only_t_proxy": costs[len(costs) // 2],
        "scope": (
            "Counts classical arithmetic calls for decode, complementary-row "
            "reconstruction, and four-point branch replay. Every multiply call "
            "is charged 42T, including fixed-coefficient calls. It does not "
            "compile a circuit and excludes control, degree framing, phase, "
            "scratch, and cleanup costs."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2, sort_keys=True))
