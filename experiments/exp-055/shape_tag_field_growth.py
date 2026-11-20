"""Check the factorized shape-tag map as the field and arithmetic grow.

The GF(8) and GF(16) runs exhaust every four-sample input. The GF(2^12) run
uses the competition field and evaluation points, but exhausts only the subset
whose four values lie in 0..15. This is a falsification screen, not a proof for
all GF(2^12) inputs or a reversible circuit.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-053"))

import fma_state_compression as fma  # noqa: E402
import compact_basis_cost as codec  # noqa: E402


GF8_SHAPE_COLORS = [0, 0, 1, 0, 0, 0, 0, 1, 0, 2, 0, 0, 2, 0]
POINTS = list(range(4))


def screen(name: str, degree: int, modulus: int, values: range) -> dict:
    """Exhaust a four-sample domain and rebuild its shape-conflict graph."""
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    payload_shapes: dict[tuple[int, ...], set[int]] = defaultdict(set)
    labels: dict[tuple[int, tuple[int, ...]], tuple[int, ...]] = {}
    input_count = 0

    for data in product(values, repeat=len(POINTS)):
        input_count += 1
        basis = fma.modular_basis(data, POINTS, mul)
        low_index = min(range(2), key=lambda index: fma.row_rank(basis, index))
        row = [fma.trim(list(poly)) for poly in basis[low_index]]
        pivot = row[0][-1] if row[0] != [0] else row[1][-1]
        scale = fma.gf_inv(pivot, modulus, degree)
        row = tuple(
            tuple(fma.trim([mul(scale, value) for value in poly]))
            for poly in row
        )

        gcd, _, _ = fma.poly_xgcd(row[0], row[1], mul, modulus, degree)
        cofactor_w, remainder_w = fma.poly_divmod(
            row[0], gcd, mul, modulus, degree
        )
        cofactor_n, remainder_n = fma.poly_divmod(
            row[1], gcd, mul, modulus, degree
        )
        assert remainder_w == [0] and remainder_n == [0]
        root_samples = tuple(
            data[index]
            for index, point in enumerate(POINTS)
            if fma.poly_eval(gcd, point, mul) == 0
        )
        shape_id, words = codec.pack_factorized_state(
            gcd, cofactor_w, cofactor_n, root_samples
        )
        state = codec.unpack_factorized_state(words, shape_id)
        recovered = codec.recover_factorized_samples(
            *state, POINTS, mul, modulus, degree
        )
        assert tuple(recovered) == data

        label = (shape_id, words)
        prior = labels.setdefault(label, data)
        assert prior == data
        payload_shapes[words].add(shape_id)

    adjacency = [set() for _ in codec.FACTOR_SHAPES]
    for shape_ids in payload_shapes.values():
        for left, right in combinations(shape_ids, 2):
            adjacency[left].add(right)
            adjacency[right].add(left)

    fixed_map_conflicts = [
        {"payload": list(words), "shape_ids": sorted(shape_ids)}
        for words, shape_ids in payload_shapes.items()
        if any(
            GF8_SHAPE_COLORS[left] == GF8_SHAPE_COLORS[right]
            for left, right in combinations(shape_ids, 2)
        )
    ]
    color_count = codec.chromatic_number(adjacency)
    return {
        "field": name,
        "degree": degree,
        "modulus": hex(modulus),
        "evaluation_points": POINTS,
        "input_value_range": [values.start, values.stop - 1],
        "four_sample_inputs_checked": input_count,
        "distinct_factorized_labels": len(labels),
        "distinct_four_word_payloads": len(payload_shapes),
        "conflict_edges": [
            [left, right]
            for left in range(len(adjacency))
            for right in sorted(adjacency[left])
            if left < right
        ],
        "minimum_shape_colors": color_count,
        "minimum_tag_bits": (color_count - 1).bit_length(),
        "gf8_shape_map_conflicts": len(fixed_map_conflicts),
        "first_gf8_map_conflict": (
            fixed_map_conflicts[0] if fixed_map_conflicts else None
        ),
    }


def screen_transformed_context(
    name: str, degree: int, modulus: int, value_count: int
) -> dict:
    """Check the same tag after a real four-point left-basis transform."""
    from normalized_fma import normalized_low_row, normalized_state

    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    left_points, right_points = list(range(4)), list(range(4, 8))
    left_data = (1, 6, 1, 6)
    _, _, _, _, left_basis, _, rank_start = normalized_state(
        left_data, left_points, mul, modulus, degree
    )
    transforms = [
        tuple(
            fma.poly_eval(poly, point, mul)
            for row in left_basis
            for poly in row
        )
        for point in right_points
    ]
    payload_shapes: dict[tuple[int, ...], dict[int, tuple[int, ...]]] = defaultdict(dict)
    labels: dict[tuple[int, tuple[int, ...]], tuple[int, ...]] = {}
    adjacency = [set() for _ in codec.FACTOR_SHAPES]
    invalid_states = 0
    first_invalid_input = None
    first_same_color_collision = None
    same_color_collision_count = 0
    inputs_checked = 0

    for original in product(range(value_count), repeat=4):
        inputs_checked += 1
        transformed_d, transformed_g = [], []
        for value, (a, b, c, d) in zip(original, transforms):
            transformed_d.append(mul(a, value) ^ b)
            transformed_g.append(mul(c, value) ^ d)
        _, _, _, _, basis, _, _ = normalized_state(
            transformed_d,
            right_points,
            mul,
            modulus,
            degree,
            g_values=transformed_g,
            initial_ranks=rank_start,
        )
        fma.assert_basis(transformed_d, transformed_g, right_points, basis, mul)
        row = normalized_low_row(basis, mul, modulus, degree)
        gcd, _, _ = fma.poly_xgcd(row[0], row[1], mul, modulus, degree)
        cofactor_w, remainder_w = fma.poly_divmod(
            row[0], gcd, mul, modulus, degree
        )
        cofactor_n, remainder_n = fma.poly_divmod(
            row[1], gcd, mul, modulus, degree
        )
        assert remainder_w == [0] and remainder_n == [0]
        roots = [
            index
            for index, point in enumerate(right_points)
            if fma.poly_eval(gcd, point, mul) == 0
        ]
        root_samples = tuple(original[index] for index in roots)
        try:
            shape_id, words = codec.pack_factorized_state(
                gcd, cofactor_w, cofactor_n, root_samples
            )
        except ValueError:
            invalid_states += 1
            if first_invalid_input is None:
                first_invalid_input = list(original)
            continue

        # Decode the original, untransformed right samples using the retained
        # left basis. This checks that the collision graph compares real data.
        decoded = []
        saved_roots = dict(zip(roots, root_samples))
        for index, point in enumerate(right_points):
            if index in saved_roots:
                decoded.append(saved_roots[index])
                continue
            w_value = fma.poly_eval(cofactor_w, point, mul)
            n_value = fma.poly_eval(cofactor_n, point, mul)
            a, b, c, d = transforms[index]
            denominator = mul(a, w_value) ^ mul(c, n_value)
            numerator = mul(b, w_value) ^ mul(d, n_value)
            assert denominator != 0
            decoded.append(
                mul(numerator, fma.gf_inv(denominator, modulus, degree))
            )
        assert tuple(decoded) == original

        label = (shape_id, words)
        prior_input = labels.setdefault(label, tuple(original))
        assert prior_input == tuple(original)
        for prior_shape, prior_data in payload_shapes[words].items():
            if prior_shape == shape_id:
                assert prior_data == tuple(original)
                continue
            adjacency[prior_shape].add(shape_id)
            adjacency[shape_id].add(prior_shape)
            if GF8_SHAPE_COLORS[prior_shape] == GF8_SHAPE_COLORS[shape_id]:
                same_color_collision_count += 1
                if first_same_color_collision is None:
                    first_same_color_collision = {
                        "payload": list(words),
                        "shape_ids": [prior_shape, shape_id],
                        "inputs": [list(prior_data), list(original)],
                        "color": GF8_SHAPE_COLORS[shape_id],
                    }
        payload_shapes[words][shape_id] = tuple(original)

    color_count = codec.chromatic_number(adjacency)
    return {
        "field": name,
        "left_points": left_points,
        "right_points": right_points,
        "left_input": list(left_data),
        "start_ranks_from_left_block": list(rank_start),
        "right_input_value_range": [0, value_count - 1],
        "right_inputs_checked": inputs_checked,
        "factorized_states_outside_current_catalog": invalid_states,
        "first_out_of_catalog_input": first_invalid_input,
        "distinct_factorized_labels": len(labels),
        "distinct_four_word_payloads": len(payload_shapes),
        "conflict_edges": sum(map(len, adjacency)) // 2,
        "minimum_shape_colors": color_count,
        "minimum_tag_bits": (color_count - 1).bit_length(),
        "existing_gf8_map_same_color_collisions": same_color_collision_count,
        "first_same_color_collision": first_same_color_collision,
        "contextual_sample_round_trip_errors": 0,
    }


def main() -> None:
    results = {
        "experiment": "exp-055-shape-tag-field-growth",
        "shape_catalog": [list(shape) for shape in codec.FACTOR_SHAPES],
        "runs": [
            screen("GF(8), exhaustive", 3, 0b1011, range(8)),
            screen("GF(16), exhaustive", 4, 0x13, range(16)),
            screen(
                "GF(2^12), low-nibble subset",
                12,
                0x1053,
                range(16),
            ),
        ],
        "transformed_block_runs": [
            screen_transformed_context("GF(8), exhaustive", 3, 0b1011, 8),
            screen_transformed_context(
                "GF(2^12), low-nibble subset", 12, 0x1053, 16
            ),
        ],
        "scope": (
            "The first two runs exhaust pristine four-sample domains with g=1. "
            "The third uses competition GF(2^12) arithmetic and points, but "
            "checks only 16^4 inputs. The transformed-block runs use one exact "
            "4+4 left-basis context; the GF(2^12) run again checks only 16^4 "
            "right inputs. None measures a reversible decoder circuit or "
            "exhausts all GF(2^12) contexts."
        ),
    }
    assert all(run["minimum_tag_bits"] == 2 for run in results["runs"])
    assert all(run["gf8_shape_map_conflicts"] == 0 for run in results["runs"])
    assert results["transformed_block_runs"][0]["minimum_tag_bits"] == 3
    assert results["transformed_block_runs"][0][
        "existing_gf8_map_same_color_collisions"
    ] > 0
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
