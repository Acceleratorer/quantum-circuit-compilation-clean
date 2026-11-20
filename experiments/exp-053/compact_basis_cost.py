"""Screen classical recovery work for a compact four-point FMA state.

This counts field-arithmetic calls in the existing classical reconstruction
path over every GF(8) four-sample input. The GF(2^12) Toffoli figure is an
arithmetic-only proxy; it is not a compiled reversible circuit or a bound on
workspace, control, phase, or cleanup costs.
"""

from __future__ import annotations

from itertools import combinations, product
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


def poly_divmod_monic(numerator, denominator, mul):
    """Divide by a monic polynomial without variable work for its leading 1."""
    remainder = fma.trim(list(numerator))
    denominator = fma.trim(list(denominator))
    if denominator == [0] or denominator[-1] != 1:
        raise ValueError("the divisor must be nonzero and monic")
    quotient = [0] * max(1, len(remainder) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        factor = remainder[-1]
        quotient[shift] = factor
        for index, coefficient in enumerate(denominator[:-1]):
            remainder[shift + index] ^= mul(factor, coefficient)
        remainder[-1] = 0
        fma.trim(remainder)
    return fma.trim(quotient), remainder


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


def screen_gf12_dqi_cost_proxy(shape_colors=None):
    """Count raw and constant-aware recovery proxies on DQI samples."""
    import normalized_fma

    if shape_colors is not None and len(shape_colors) != len(FACTOR_SHAPES):
        raise ValueError("shape_colors must cover the complete shape catalog")

    degree, modulus = 12, 0x1053
    points, all_points = list(range(4)), list(range(70))
    multiply = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    rng = Random(0xF1A053)
    original_mul, original_inv = fma.gf_mul, fma.gf_inv
    original_poly_eval = fma.poly_eval
    inverse_body = original_inv.__wrapped__
    records = []
    payload_inputs = {}

    def proxy(counts):
        return counts["field_multiply_calls"] * 42 + counts["inverse_calls"] * 138

    for weight in (1, 31, 35):
        for _ in range(16):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(all_points)
            for location, magnitude in zip(locations, magnitudes):
                power = location
                for index in range(len(all_points)):
                    syndrome[index] ^= multiply(magnitude, power)
                    power = multiply(power, location)
            data = tuple(
                fma.syndrome_to_fma_samples(syndrome, all_points, multiply)[:4]
            )

            basis = fma.modular_basis(data, points, multiply)
            low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
            row = [fma.trim(list(poly)) for poly in basis[low_index]]
            pivot = row[0][-1] if row[0] != [0] else row[1][-1]
            scale = fma.gf_inv(pivot, modulus, degree)
            row = tuple(
                tuple(fma.trim([multiply(scale, value) for value in poly]))
                for poly in row
            )

            counts = {"field_multiply_calls": 0, "inverse_calls": 0}

            def counted_mul(left, right, mod, bits):
                counts["field_multiply_calls"] += 1
                return original_mul(left, right, mod, bits)

            def counted_inv(value, mod, bits):
                counts["inverse_calls"] += 1
                current_mul = fma.gf_mul
                fma.gf_mul = original_mul
                try:
                    return inverse_body(value, mod, bits)
                finally:
                    fma.gf_mul = current_mul

            fma.gf_mul, fma.gf_inv = counted_mul, counted_inv
            try:
                gcd, _, _ = fma.poly_xgcd(row[0], row[1], multiply, modulus, degree)
                cofactor_w, remainder = fma.poly_divmod(
                    row[0], gcd, multiply, modulus, degree
                )
                assert remainder == [0]
                cofactor_n, remainder = fma.poly_divmod(
                    row[1], gcd, multiply, modulus, degree
                )
                assert remainder == [0]
                roots = tuple(
                    data[index]
                    for index, point in enumerate(points)
                    if fma.poly_eval(gcd, point, multiply) == 0
                )
                shape_id, words = pack_factorized_state(
                    gcd, cofactor_w, cofactor_n, roots
                )
                payload_inputs.setdefault(words, {}).setdefault(shape_id, set()).add(
                    tuple(data)
                )
                raw_factorized_state = (gcd, cofactor_w, cofactor_n, roots)
                factorize = dict(counts)

                counts = {"field_multiply_calls": 0, "inverse_calls": 0}
                decoded = unpack_factorized_state(words, shape_id)
                recovered = recover_factorized_samples(
                    *decoded, points, multiply, modulus, degree
                )
                assert recovered == list(data)
                recover = dict(counts)

                counts = {"field_multiply_calls": 0, "inverse_calls": 0}
                raw_replay_result = normalized_fma.replayed_ratios(
                    data, points, modulus, degree
                )
                replay = dict(counts)
            finally:
                fma.gf_mul, fma.gf_inv = original_mul, original_inv

            stages = {"factorize": factorize, "recover": recover, "replay": replay}
            stage_t = {name: proxy(count) for name, count in stages.items()}

            # Each evaluation point and the monic gcd leading coefficient are
            # constants. Treat these known-linear operations as zero-T work.
            def evaluate_at_public_point(poly, point, _mul):
                value = 0
                for coefficient in reversed(poly):
                    value = original_mul(value, point, modulus, degree) ^ coefficient
                return value

            counts = {"field_multiply_calls": 0, "inverse_calls": 0}
            fma.gf_mul, fma.gf_inv = counted_mul, counted_inv
            fma.poly_eval = evaluate_at_public_point
            try:
                gcd, _, _ = fma.poly_xgcd(
                    row[0], row[1], multiply, modulus, degree
                )
                assert gcd[-1] == 1
                cofactor_w, remainder = poly_divmod_monic(
                    row[0], gcd, multiply
                )
                assert remainder == [0]
                cofactor_n, remainder = poly_divmod_monic(
                    row[1], gcd, multiply
                )
                assert remainder == [0]
                roots = tuple(
                    data[index]
                    for index, point in enumerate(points)
                    if fma.poly_eval(gcd, point, multiply) == 0
                )
                shape_id, words = pack_factorized_state(
                    gcd, cofactor_w, cofactor_n, roots
                )
                assert (gcd, cofactor_w, cofactor_n, roots) == raw_factorized_state
                optimized_factorize = dict(counts)

                counts = {"field_multiply_calls": 0, "inverse_calls": 0}
                decoded = unpack_factorized_state(words, shape_id)
                optimized_recovered = recover_factorized_samples(
                    *decoded, points, multiply, modulus, degree
                )
                assert optimized_recovered == list(data)
                assert optimized_recovered == recovered
                optimized_recover = dict(counts)

                counts = {"field_multiply_calls": 0, "inverse_calls": 0}
                optimized_replay = normalized_fma.replayed_ratios(
                    data,
                    points,
                    modulus,
                    degree,
                    mul_const=original_mul,
                )
                assert optimized_replay == raw_replay_result
                optimized_branch_replay = dict(counts)
            finally:
                fma.gf_mul, fma.gf_inv = original_mul, original_inv
                fma.poly_eval = original_poly_eval

            optimized_stages = {
                "factorize": optimized_factorize,
                "recover": optimized_recover,
                "replay": optimized_branch_replay,
            }
            optimized_stage_t = {
                name: proxy(count) for name, count in optimized_stages.items()
            }
            records.append(
                {
                    "weight": weight,
                    "shape": FACTOR_SHAPES[shape_id],
                    "factorization_t_proxy": stage_t["factorize"],
                    "sample_recovery_t_proxy": stage_t["recover"],
                    "branch_replay_t_proxy": stage_t["replay"],
                    "total_t_proxy": sum(stage_t.values()),
                    "linear_constants_factorization_t_proxy": (
                        optimized_stage_t["factorize"]
                    ),
                    "linear_constants_recovery_t_proxy": (
                        optimized_stage_t["recover"]
                    ),
                    "linear_constants_replay_t_proxy": (
                        optimized_stage_t["replay"]
                    ),
                    "linear_constants_total_t_proxy": sum(
                        optimized_stage_t.values()
                    ),
                }
            )

    color_label_inputs = {}
    if shape_colors is not None:
        for words, shape_inputs in payload_inputs.items():
            for shape_id, inputs in shape_inputs.items():
                label = (shape_colors[shape_id], words)
                color_label_inputs.setdefault(label, set()).update(inputs)
    return {
        "cases": len(records),
        "weights": [1, 31, 35],
        "shape_counts": {
            str(shape): sum(record["shape"] == shape for record in records)
            for shape in sorted({record["shape"] for record in records})
        },
        "mean_t_proxy": {
            name: sum(record[name] for record in records) / len(records)
            for name in (
                "factorization_t_proxy",
                "sample_recovery_t_proxy",
                "branch_replay_t_proxy",
                "total_t_proxy",
            )
        },
        "maximum_t_proxy": {
            name: max(record[name] for record in records)
            for name in (
                "factorization_t_proxy",
                "sample_recovery_t_proxy",
                "branch_replay_t_proxy",
                "total_t_proxy",
            )
        },
        "linear_constants_mean_t_proxy": {
            name: sum(record[name] for record in records) / len(records)
            for name in (
                "linear_constants_factorization_t_proxy",
                "linear_constants_recovery_t_proxy",
                "linear_constants_replay_t_proxy",
                "linear_constants_total_t_proxy",
            )
        },
        "linear_constants_maximum_t_proxy": {
            name: max(record[name] for record in records)
            for name in (
                "linear_constants_factorization_t_proxy",
                "linear_constants_recovery_t_proxy",
                "linear_constants_replay_t_proxy",
                "linear_constants_total_t_proxy",
            )
        },
        "linear_constant_optimizations": [
            "public evaluation-point multipliers are linear maps over GF(2)",
            "multiplication by the monic gcd leading coefficient 1 is omitted",
            "both paths produce identical factors, samples, ratios, and branches",
        ],
        "shape_color_sample_check": (
            None
            if shape_colors is None
            else {
                "distinct_inputs": sum(
                    len(inputs)
                    for shape_inputs in payload_inputs.values()
                    for inputs in shape_inputs.values()
                ),
                "distinct_four_word_payloads": len(payload_inputs),
                "distinct_colored_labels": len(color_label_inputs),
                "colored_label_collisions": sum(
                    max(0, len(inputs) - 1)
                    for inputs in color_label_inputs.values()
                ),
                "scope": (
                    "Checks the GF(8)-derived two-bit shape coloring on these 48 "
                    "seeded GF(2^12) prefixes only; it is not a full-field proof."
                ),
            }
        ),
        "scope": (
            "Arithmetic-only GF(2^12) proxy over 48 seeded valid 70-symbol DQI "
            "samples. Both paths start after low-row formation and normalization. "
            "The raw path charges every field multiply 42T and inverse 138T; "
            "the constant-aware path treats public point multipliers and the "
            "monic leading 1 as linear. Inverse internals are not double-counted. "
            "Neither path counts CNOTs or compiles a full 4+66 schedule."
        ),
    }


def chromatic_number(adjacency):
    """Return the exact chromatic number of the small GF(8) conflict graph."""
    order = sorted(range(len(adjacency)), key=lambda vertex: len(adjacency[vertex]), reverse=True)
    colors = [-1] * len(adjacency)

    def colorable(limit, index=0, maximum=-1):
        if index == len(order):
            return True
        vertex = order[index]
        for color in range(min(limit - 1, maximum + 1) + 1):
            if all(colors[neighbor] != color for neighbor in adjacency[vertex]):
                colors[vertex] = color
                if colorable(limit, index + 1, max(maximum, color)):
                    return True
                colors[vertex] = -1
        return False

    return next(limit for limit in range(1, len(adjacency) + 1) if colorable(limit))


def color_graph(adjacency, color_count):
    """Return a deterministic coloring or fail if the count is too small."""
    order = sorted(
        range(len(adjacency)),
        key=lambda vertex: len(adjacency[vertex]),
        reverse=True,
    )
    colors = [-1] * len(adjacency)

    def assign(index=0):
        if index == len(order):
            return True
        vertex = order[index]
        for color in range(color_count):
            if all(colors[neighbor] != color for neighbor in adjacency[vertex]):
                colors[vertex] = color
                if assign(index + 1):
                    return True
                colors[vertex] = -1
        return False

    if not assign():
        raise ValueError("the conflict graph needs more colors")
    return colors


def screen_factorized_packer_tag_upper_bound():
    """Color all shape overlaps allowed by the four-word packer format."""
    payload_shapes = {}
    for shape_id, (gcd_degree, degree_a, degree_b) in enumerate(FACTOR_SHAPES):
        payload_words = (
            2 * gcd_degree + degree_a + max(0, degree_b + 1)
        )
        for values in product((0, 1), repeat=payload_words):
            if degree_b >= 0 and values[gcd_degree + degree_a + degree_b] == 0:
                continue
            words = tuple(values) + (0,) * (4 - payload_words)
            payload_shapes.setdefault(words, set()).add(shape_id)

    adjacency = [set() for _ in FACTOR_SHAPES]
    for shape_ids in payload_shapes.values():
        for left, right in combinations(shape_ids, 2):
            adjacency[left].add(right)
            adjacency[right].add(left)
    color_count = chromatic_number(adjacency)
    colors = color_graph(adjacency, color_count)
    state_count = sum(len(shape_ids) for shape_ids in payload_shapes.values())
    tagged_label_count = len(
        {
            (colors[shape_id], words)
            for words, shape_ids in payload_shapes.items()
            for shape_id in shape_ids
        }
    )
    assert state_count == tagged_label_count
    return {
        "support_patterns_checked": len(payload_shapes),
        "labels_over_support_patterns": state_count,
        "payload_collision_fibers": sum(
            len(shape_ids) > 1 for shape_ids in payload_shapes.values()
        ),
        "maximum_shape_fiber": max(map(len, payload_shapes.values())),
        "conflict_graph_edges": sum(map(len, adjacency)) // 2,
        "minimum_shape_colors": color_count,
        "minimum_tag_bits": (color_count - 1).bit_length(),
        "shape_color_map": [
            {"shape_id": index, "color": color}
            for index, color in enumerate(colors)
        ],
        "tagged_label_collisions": state_count - tagged_label_count,
        "scope": (
            "Enumerates all zero/nonzero support patterns admitted by the four-word "
            "packer, enforcing exact nonzero degree for B. It does not enforce "
            "gcd, node-root, coprimality, or modular-basis constraints, so it is a "
            "field-size-independent upper bound on the generic packer domain, not "
            "the image of the DQI encoder."
        ),
    }


def screen_fixed_shape_streaming_labels():
    """Screen three samples plus one retained A coefficient on valid GF(8) states.

    A coefficient-only side label must color the conflict graph induced by
    states that agree on the three outputs and retained coefficient.
    """
    degree, modulus, points = 3, 0b1011, tuple(range(4))
    size = 1 << degree
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    states = []
    for a0, a1 in product(range(size), repeat=2):
        denominator = [a0, a1, 1]
        if any(fma.poly_eval(denominator, value, mul) == 0 for value in range(size)):
            continue
        for b0 in range(size):
            for b1 in range(1, size):
                numerator = [b0, b1]
                samples = tuple(
                    mul(
                        fma.poly_eval(numerator, point, mul),
                        fma.gf_inv(
                            fma.poly_eval(denominator, point, mul), modulus, degree
                        ),
                    )
                    for point in points
                )
                history = fma.sequential_state(samples, points, mul)[2]
                states.append((a0, a1, samples, history))

    assert len(states) == 1568
    assert len({state[2] for state in states}) == len(states)
    options = []
    for sample_points in combinations(points, 3):
        for retained_index in (0, 1):
            fibers = {}
            for a0, a1, samples, history in states:
                retained = (a0, a1)[retained_index]
                discarded = (a1, a0)[retained_index]
                key = tuple(samples[index] for index in sample_points) + (retained,)
                fibers.setdefault(key, []).append((discarded, history))

            adjacency = [set() for _ in range(size)]
            same_history_pairs = 0
            for fiber in fibers.values():
                for left, right in combinations(fiber, 2):
                    if left[0] != right[0]:
                        adjacency[left[0]].add(right[0])
                        adjacency[right[0]].add(left[0])
                    if left[1] == right[1]:
                        same_history_pairs += 1

            chromatic = chromatic_number(adjacency)
            options.append(
                {
                    "sample_points": list(sample_points),
                    "retained_cofactor_a_coefficient": retained_index,
                    "distinct_keys": len(fibers),
                    "keys_with_collisions": sum(len(fiber) > 1 for fiber in fibers.values()),
                    "maximum_fiber": max(map(len, fibers.values())),
                    "same_branch_history_pairs": same_history_pairs,
                    "minimum_coefficient_only_tag_bits": (chromatic - 1).bit_length(),
                    "coefficient_conflict_graph_chromatic_number": chromatic,
                }
            )

    multiplier_tag_screens = []
    for sample_points in combinations(points, 3):
        for retained_index in (0, 1):
            fibers = {}
            for a0, a1, samples, _ in states:
                retained = (a0, a1)[retained_index]
                discarded = (a1, a0)[retained_index]
                key = tuple(samples[index] for index in sample_points) + (retained,)
                fibers.setdefault(key, []).append(discarded)

            collision_fibers = [values for values in fibers.values() if len(values) > 1]
            candidate = None
            forms_checked = 0
            for coefficients in product(range(size), repeat=4):
                forms_checked += 1
                excluded_kernels = set()
                valid = True
                for key, values in fibers.items():
                    if len(values) < 2:
                        continue
                    multiplier = 0
                    for coefficient, key_value in zip(coefficients, key):
                        multiplier ^= mul(coefficient, key_value)
                    if multiplier == 0:
                        valid = False
                        break
                    for left, right in combinations(values, 2):
                        excluded_kernels.add(mul(multiplier, left ^ right))
                kernels = set(range(1, size)) - excluded_kernels if valid else set()
                if kernels:
                    candidate = {
                        "field_linear_key_coefficients": list(coefficients),
                        "valid_projection_kernels": sorted(kernels),
                    }
                    break
            multiplier_tag_screens.append(
                {
                    "sample_points": list(sample_points),
                    "retained_cofactor_a_coefficient": retained_index,
                    "collision_keys": len(collision_fibers),
                    "field_linear_forms_checked": forms_checked,
                    "candidate": candidate,
                }
            )

            affine_kernel_candidate = None
            affine_forms_checked = 0
            for coefficients in product(range(size), repeat=4):
                affine_forms_checked += 1
                forbidden_offsets = set()
                for key, values in fibers.items():
                    if len(values) < 2:
                        continue
                    base = 0
                    for coefficient, key_value in zip(coefficients, key):
                        base ^= mul(coefficient, key_value)
                    forbidden_offsets.add(base)
                    forbidden_offsets.update(
                        base ^ (left ^ right)
                        for left, right in combinations(values, 2)
                    )
                offsets = set(range(size)) - forbidden_offsets
                if offsets:
                    affine_kernel_candidate = {
                        "field_linear_key_coefficients": list(coefficients),
                        "valid_constant_offsets": sorted(offsets),
                    }
                    break
            multiplier_tag_screens[-1]["affine_kernel_forms_checked"] = (
                affine_forms_checked
            )
            multiplier_tag_screens[-1]["affine_kernel_candidate"] = (
                affine_kernel_candidate
            )

    assert all(option["maximum_fiber"] == 4 for option in options)
    assert all(option["minimum_coefficient_only_tag_bits"] >= 3 for option in options)
    assert all(option["same_branch_history_pairs"] > 0 for option in options)
    return {
        "shape_states": len(states),
        "sample_and_coefficient_keys_injective": False,
        "options_checked": len(options),
        "options": options,
        "bilinear_key_multiplier_tag": {
            "layouts_checked": len(multiplier_tag_screens),
            "layouts_with_two_bit_tag": sum(
                screen["candidate"] is not None for screen in multiplier_tag_screens
            ),
            "field_linear_forms_checked_per_layout": size ** 4,
            "projection_kernels_checked_per_form": size - 1,
            "tag_form": "fixed 2-bit GF(2)-linear projection of d * u(key)",
            "layout_results": multiplier_tag_screens,
            "scope": (
                "Exhausts all GF(8)-linear forms u of the three retained samples and "
                "retained A coefficient, and all rank-2 GF(2)-linear projections "
                "(enumerated by their seven possible 1-D kernels). This does not test "
                "key-dependent projections outside the affine-kernel family below, "
                "higher-degree tags, or GF(2^12)."
            ),
        },
        "affine_key_kernel_tag": {
            "layouts_checked": len(multiplier_tag_screens),
            "field_linear_parts_per_layout": size ** 4,
            "constant_offsets_per_linear_part": size,
            "affine_kernels_per_layout": size ** 5,
            "layouts_with_two_bit_tag": sum(
                screen["affine_kernel_candidate"] is not None
                for screen in multiplier_tag_screens
            ),
            "kernel_form": "v(key) = c + sum(lambda_i * key_i) over GF(8)",
            "tag_form": "per-key rank-2 GF(2)-linear projection with kernel span(v(key))",
            "scope": (
                "Exhausts all affine GF(8)-field-linear kernel functions on each key. "
                "This does not test arbitrary GF(2)-linear or nonlinear kernel functions, "
                "other key-dependent projections, or GF(2^12)."
            ),
        },
        "scope": (
            "All monic irreducible quadratic A and degree-1 B over GF(8), with four "
            "public points. Rejects only a coefficient-only side label and branch-history "
            "label for the three-samples-plus-one-A-coefficient layouts, plus fixed-projection "
            "bilinear tags d * u(key) and field-affine projection kernels. Nonlinear "
            "key-dependent projections, higher-degree tags, and GF(2^12) remain untested."
        ),
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
    payload_shapes = {}
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
            payload_shapes.setdefault(packed_words, set()).add(shape_id)
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
    shape_conflicts = [set() for _ in FACTOR_SHAPES]
    for shape_ids in payload_shapes.values():
        for left, right in combinations(shape_ids, 2):
            shape_conflicts[left].add(right)
            shape_conflicts[right].add(left)
    color_count = chromatic_number(shape_conflicts)
    shape_colors = color_graph(shape_conflicts, color_count)
    color_labels = {
        (shape_colors[shape_id], packed_words)
        for packed_words, shape_ids in payload_shapes.items()
        for shape_id in shape_ids
    }
    assert len(color_labels) == len(packed_labels)
    rank1_headroom = 8 - max_rank1.bit_length()
    shape_tag_bits = (len(FACTOR_SHAPES) - 1).bit_length()
    assert shape_tag_bits <= rank1_headroom
    color_tag_screen = {
        "distinct_four_word_payloads": len(payload_shapes),
        "payload_collision_fibers": sum(
            len(shape_ids) > 1 for shape_ids in payload_shapes.values()
        ),
        "maximum_shape_fiber": max(map(len, payload_shapes.values())),
        "conflict_graph_edges": sum(map(len, shape_conflicts)) // 2,
        "minimum_shape_colors": color_count,
        "minimum_tag_bits": (color_count - 1).bit_length(),
        "shape_color_map": [
            {"shape_id": index, "color": color}
            for index, color in enumerate(shape_colors)
        ],
        "colored_label_collisions": len(packed_labels) - len(color_labels),
        "scope": (
            "Exhaustive over all 4,096 arbitrary GF(8) four-sample inputs. This "
            "reduces the shape label from four bits to two on that domain; it "
            "does not prove the same conflict graph over GF(2^12) or compile a "
            "reversible color decoder."
        ),
    }
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
            "compressed_shape_tag": color_tag_screen,
            "generic_packer_tag_upper_bound": (
                screen_factorized_packer_tag_upper_bound()
            ),
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
        "gf12_dqi_cost_proxy": screen_gf12_dqi_cost_proxy(shape_colors),
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
        "fixed_shape_streaming_label": screen_fixed_shape_streaming_labels(),
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
