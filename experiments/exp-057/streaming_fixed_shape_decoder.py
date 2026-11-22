"""Classical screen for an in-place four-word rational decoder state."""

from __future__ import annotations

from itertools import product
import json
from random import Random
import sys

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


POINTS = (0, 1, 2, 3)


def ops(degree: int, modulus: int):
    multiply = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    inverse = lambda a: fma.gf_inv(a, modulus, degree)

    def divide(a: int, b: int) -> int:
        if b == 0:
            raise ZeroDivisionError
        return multiply(a, inverse(b))

    return multiply, inverse, divide


def evaluate(a0, a1, b0, b1, point, mul, div):
    denominator = mul(point, point) ^ mul(a1, point) ^ a0
    numerator = mul(b1, point) ^ b0
    return div(numerator, denominator)


def sample_words(coefficients, mul, div):
    a0, a1, b0, b1 = coefficients
    return tuple(evaluate(a0, a1, b0, b1, x, mul, div) for x in POINTS)


def pivot_data(d0, d1, d2, mul):
    c0 = d2 ^ mul(2, d1) ^ mul(3, d0)
    c1 = mul(2, d2 ^ d1)
    constant = mul(4, d2) ^ mul(2, d1)
    if c0:
        return 0, c0, c1, constant
    if c1:
        return 1, c0, c1, constant
    raise ValueError("the first three samples do not determine a pivot")


def coefficients_from_prefix(d0, d1, d2, remaining, mul, div):
    pivot, c0, c1, constant = pivot_data(d0, d1, d2, mul)
    if pivot == 0:
        a1 = remaining
        a0 = div(constant ^ mul(c1, a1), c0)
    else:
        a0 = remaining
        a1 = div(constant, c1)
    b0 = mul(d0, a0)
    b1 = d1 ^ mul(d0 ^ d1, a0) ^ mul(d1, a1)
    return (a0, a1, b0, b1), pivot


def prefix_state_from_coefficients(coefficients, mul, div):
    a0, a1, _, _ = coefficients
    d0, d1, d2, _ = sample_words(coefficients, mul, div)
    pivot, _, _, _ = pivot_data(d0, d1, d2, mul)
    remaining = a1 if pivot == 0 else a0
    reconstructed, check_pivot = coefficients_from_prefix(
        d0, d1, d2, remaining, mul, div
    )
    if check_pivot != pivot or reconstructed != coefficients:
        raise ValueError("prefix state did not reconstruct its input")
    return (d0, d1, d2, remaining), pivot


def samples_from_prefix_state(state, mul, div):
    d0, d1, d2, remaining = state
    coefficients, _ = coefficients_from_prefix(d0, d1, d2, remaining, mul, div)
    d3 = evaluate(*coefficients, POINTS[3], mul, div)
    return (d0, d1, d2, d3)


def apply_matrix(rows, point, pair, mul):
    d_value, g_value = pair
    return tuple(
        mul(fma.poly_eval(w, point, mul), d_value)
        ^ mul(fma.poly_eval(n, point, mul), g_value)
        for w, n in rows
    )


def matrix_determinant(rows, mul):
    return fma.poly_add(
        fma.poly_mul(rows[0][0], rows[1][1], mul),
        fma.poly_mul(rows[0][1], rows[1][0], mul),
    )


def assert_same_row_module(rows, samples, points, mul, inverse, modulus, degree):
    basis = fma.modular_basis(samples, points, mul)
    low_index = min(range(2), key=lambda index: fma.row_rank(basis, index))
    direct_low = basis[low_index]
    low_scale = inverse(direct_low[0][-1])
    normalized_low = tuple(
        tuple(mul(low_scale, value) for value in polynomial)
        for polynomial in direct_low
    )
    assert normalized_low == tuple(tuple(polynomial) for polynomial in rows[0])

    direct_complement = basis[1 - low_index]
    determinant = matrix_determinant((rows[0], direct_complement), mul)
    complement_scale = inverse(determinant[-1])
    direct_complement = tuple(
        tuple(mul(complement_scale, value) for value in polynomial)
        for polynomial in direct_complement
    )
    node = [1]
    for point in points:
        node = fma.poly_mul(node, [point, 1], mul)
    assert matrix_determinant((rows[0], direct_complement), mul) == node

    differences = tuple(
        fma.poly_add(left, right)
        for left, right in zip(rows[1], direct_complement)
    )
    quotients = []
    for difference, low_polynomial in zip(differences, rows[0]):
        quotient, remainder = fma.poly_divmod(
            difference, low_polynomial, mul, modulus, degree
        )
        assert remainder == [0]
        quotients.append(tuple(quotient))
    assert quotients[0] == quotients[1]


def complementary_matrix_from_prefix_state(state, mul, div, modulus, degree):
    """Recover the canonical four-point FMA matrix from its compact low row."""
    coefficients, _ = coefficients_from_prefix(*state[:3], state[3], mul, div)
    a0, a1, b0, b1 = coefficients
    low_row = ([a0, a1, 1], [b0, b1])
    prefix_samples = samples_from_prefix_state(state, mul, div)
    low, complementary, exceptions = fma.reconstruct_complementary_row(
        low_row,
        prefix_samples,
        POINTS,
        mul,
        modulus,
        degree,
    )
    if exceptions:
        raise ValueError("the prefix needs exceptional-sample labels")
    node = [1]
    for point in POINTS:
        node = fma.poly_mul(node, [point, 1], mul)
    if matrix_determinant((low, complementary), mul) != node:
        raise ValueError("the reconstructed matrix has the wrong determinant")
    return (low, complementary), prefix_samples


def bezout_complementary_matrix_from_prefix_state(state, mul, div, modulus, degree):
    """Build an unreduced complementary row directly from the prefix state."""
    coefficients, _ = coefficients_from_prefix(*state[:3], state[3], mul, div)
    a0, a1, b0, b1 = coefficients
    inverse_b1 = div(1, b1)
    quotient = [
        mul(inverse_b1, a1 ^ mul(inverse_b1, b0)),
        inverse_b1,
    ]
    gcd = a0 ^ mul(quotient[0], b0)
    if gcd == 0:
        raise ValueError("the prefix low row is not coprime")

    node = [1]
    for point in POINTS:
        node = fma.poly_mul(node, [point, 1], mul)
    scaled_node = [mul(div(1, gcd), value) for value in node]
    complementary_numerator = fma.poly_mul(quotient, scaled_node, mul)
    low = ([a0, a1, 1], [b0, b1])
    prefix_samples = samples_from_prefix_state(state, mul, div)
    return (low, (complementary_numerator, scaled_node)), prefix_samples


def apply_tail_symbol(state, pair, point, mul, div, modulus, degree):
    """Apply the Bezout form of the four-point FMA basis to one later symbol."""
    rows, _ = bezout_complementary_matrix_from_prefix_state(
        state, mul, div, modulus, degree
    )
    return apply_matrix(rows, point, pair, mul)


def inverse_matrix_pair(rows, point, pair, mul, inverse):
    a = fma.poly_eval(rows[0][0], point, mul)
    b = fma.poly_eval(rows[0][1], point, mul)
    c = fma.poly_eval(rows[1][0], point, mul)
    d = fma.poly_eval(rows[1][1], point, mul)
    determinant = mul(a, d) ^ mul(b, c)
    if determinant == 0:
        raise ZeroDivisionError("the tail-point matrix is singular")
    inverse_determinant = inverse(determinant)
    out_d, out_g = pair
    return (
        mul(inverse_determinant, mul(d, out_d) ^ mul(b, out_g)),
        mul(inverse_determinant, mul(c, out_d) ^ mul(a, out_g)),
    )


def screen_gf8_tail_transition():
    degree, modulus = 3, 0b1011
    mul, inverse, div = ops(degree, modulus)
    checked = 0
    pivot_counts = [0, 0]
    tail_point = 4
    matrix_fibers = {}
    matrix_b1_keys = set()
    matrix_b1_collisions = 0
    discriminator_reconstruction_errors = 0
    for coefficients in product(range(8), range(8), range(8), range(1, 8)):
        if not valid_shape(coefficients, mul, div):
            continue
        state, pivot = prefix_state_from_coefficients(coefficients, mul, div)
        canonical_rows, prefix_samples = complementary_matrix_from_prefix_state(
            state, mul, div, modulus, degree
        )
        rows, bezout_samples = bezout_complementary_matrix_from_prefix_state(
            state, mul, div, modulus, degree
        )
        assert bezout_samples == prefix_samples
        assert_same_row_module(
            canonical_rows,
            prefix_samples,
            POINTS,
            mul,
            inverse,
            modulus,
            degree,
        )
        assert_same_row_module(
            rows,
            prefix_samples,
            POINTS,
            mul,
            inverse,
            modulus,
            degree,
        )
        for index, sample in enumerate(prefix_samples):
            assert apply_matrix(rows, POINTS[index], (sample, 1), mul) == (0, 0)
        matrix = tuple(
            fma.poly_eval(polynomial, tail_point, mul)
            for row in rows
            for polynomial in row
        )
        matrix_fibers[matrix] = matrix_fibers.get(matrix, 0) + 1
        matrix_b1_key = (matrix, coefficients[3])
        if matrix_b1_key in matrix_b1_keys:
            matrix_b1_collisions += 1
        matrix_b1_keys.add(matrix_b1_key)

        a, b, c, d = matrix
        a0, a1, _, b1 = coefficients
        recovered_a1 = mul(div(c, d), b1) ^ div(b, b1)
        recovered_b0 = b ^ mul(tail_point, b1)
        recovered_a0 = (
            a ^ mul(tail_point, recovered_a1) ^ mul(tail_point, tail_point)
        )
        if (recovered_a0, recovered_a1, recovered_b0, b1) != coefficients:
            discriminator_reconstruction_errors += 1

        tail_input = (checked % 8, 1)
        tail_output = apply_matrix(rows, tail_point, tail_input, mul)
        assert inverse_matrix_pair(
            rows, tail_point, tail_output, mul, inverse
        ) == tail_input
        checked += 1
        pivot_counts[pivot] += 1
    return {
        "field": "GF(8)",
        "supported_prefixes": checked,
        "pivot_counts": {"a0": pivot_counts[0], "a1": pivot_counts[1]},
        "prefix_annihilation_errors": 0,
        "tail_round_trip_errors": 0,
        "bezout_complementary_rows": checked,
        "tail_point": 4,
        "distinct_tail_matrices": len(matrix_fibers),
        "matrix_only_collisions": checked - len(matrix_fibers),
        "maximum_coefficients_per_tail_matrix": max(matrix_fibers.values()),
        "minimum_b1_discriminator_bits": (
            max(matrix_fibers.values()) - 1
        ).bit_length(),
        "matrix_and_b1_collisions": matrix_b1_collisions,
        "b1_discriminator_reconstruction_errors": discriminator_reconstruction_errors,
        "result": "PASS",
    }


def screen_gf12_verifier_tail_transition(count_per_weight=16):
    degree, modulus = 12, 0x1053
    points = tuple(range(70))
    mul, inverse, div = ops(degree, modulus)
    rng = Random(0x4A66058)

    node = [1]
    for point in points:
        node = fma.poly_mul(node, [point, 1], mul)
    quotients = tuple(fma._quotients(node, points, mul))[:5]

    checked = 0
    pivot_counts = [0, 0]
    matrix_b1_reconstruction_errors = 0
    for weight in (31, 35):
        for _ in range(count_per_weight):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(points)
            for location, magnitude in zip(locations, magnitudes):
                power = location
                for index in range(len(points)):
                    syndrome[index] ^= mul(magnitude, power)
                    power = mul(power, location)
            samples = tuple(
                fma._xor(
                    mul(coefficient, value)
                    for coefficient, value in zip(quotient, syndrome)
                )
                for quotient in quotients
            )
            coefficients = coefficients_from_samples(samples[:4], mul, div)
            state, pivot = prefix_state_from_coefficients(
                coefficients, mul, div
            )
            assert samples_from_prefix_state(state, mul, div) == samples[:4]
            canonical_rows, prefix_samples = complementary_matrix_from_prefix_state(
                state, mul, div, modulus, degree
            )
            rows, bezout_samples = bezout_complementary_matrix_from_prefix_state(
                state, mul, div, modulus, degree
            )
            assert prefix_samples == samples[:4]
            assert bezout_samples == prefix_samples
            assert_same_row_module(
                canonical_rows,
                prefix_samples,
                POINTS,
                mul,
                inverse,
                modulus,
                degree,
            )
            assert_same_row_module(
                rows,
                prefix_samples,
                POINTS,
                mul,
                inverse,
                modulus,
                degree,
            )
            for index, sample in enumerate(prefix_samples):
                assert apply_matrix(rows, points[index], (sample, 1), mul) == (0, 0)
            matrix = tuple(
                fma.poly_eval(polynomial, points[4], mul)
                for row in rows
                for polynomial in row
            )
            a, b, c, d = matrix
            a0, a1, b0, b1 = coefficients
            recovered_a1 = mul(div(c, d), b1) ^ div(b, b1)
            recovered_b0 = b ^ mul(points[4], b1)
            recovered_a0 = (
                a
                ^ mul(points[4], recovered_a1)
                ^ mul(points[4], points[4])
            )
            if (recovered_a0, recovered_a1, recovered_b0, b1) != coefficients:
                matrix_b1_reconstruction_errors += 1
            tail_input = (samples[4], 1)
            tail_output = apply_tail_symbol(
                state, tail_input, points[4], mul, div, modulus, degree
            )
            assert inverse_matrix_pair(
                rows, points[4], tail_output, mul, inverse
            ) == tail_input
            checked += 1
            pivot_counts[pivot] += 1
    return {
        "field": "GF(2^12)",
        "verifier_form_samples": checked,
        "error_weights": {"31": count_per_weight, "35": count_per_weight},
        "pivot_counts": {"a0": pivot_counts[0], "a1": pivot_counts[1]},
        "prefix_annihilation_errors": 0,
        "tail_round_trip_errors": 0,
        "bezout_complementary_rows": checked,
        "matrix_b1_reconstruction_errors": matrix_b1_reconstruction_errors,
        "tail_point": 4,
        "result": "PASS",
        "scope": "Seeded classical one-symbol transition only; no gate circuit or 66-symbol schedule.",
    }


def coefficients_from_samples(samples, mul, div):
    d0, d1, d2, d3 = samples
    pivot, c0, c1, constant = pivot_data(d0, d1, d2, mul)
    x = POINTS[3]
    x2 = mul(x, x)

    if pivot == 0:
        alpha = div(constant, c0)
        beta = div(c1, c0)
        d0d1 = d0 ^ d1
        denominator_0 = x2 ^ alpha
        denominator_1 = x ^ beta
        numerator_0 = mul(d0, alpha) ^ mul(
            x, d1 ^ mul(d0d1, alpha)
        )
        numerator_1 = mul(d0, beta) ^ mul(
            x, mul(d0d1, beta) ^ d1
        )
    else:
        alpha = div(constant, c1)
        denominator_0 = x2 ^ mul(x, alpha)
        denominator_1 = 1
        numerator_0 = mul(x, d1 ^ mul(d1, alpha))
        numerator_1 = d0 ^ mul(x, d0 ^ d1)

    remaining = div(
        numerator_0 ^ mul(d3, denominator_0),
        numerator_1 ^ mul(d3, denominator_1),
    )
    coefficients, inverse_pivot = coefficients_from_prefix(
        d0, d1, d2, remaining, mul, div
    )
    if inverse_pivot != pivot:
        raise ValueError("sample-derived pivot changed")
    return coefficients


def valid_shape(coefficients, mul, div):
    a0, a1, b0, b1 = coefficients
    if b1 == 0:
        return False
    denominator = lambda x: mul(x, x) ^ mul(a1, x) ^ a0
    if any(denominator(point) == 0 for point in POINTS):
        return False
    root_b = div(b0, b1)
    return denominator(root_b) != 0


def exhaustive_gf8():
    mul, _, div = ops(3, 0b1011)
    states = 0
    outputs = {}
    pivots = [0, 0]
    for coefficients in product(range(8), range(8), range(8), range(1, 8)):
        if not valid_shape(coefficients, mul, div):
            continue
        samples = sample_words(coefficients, mul, div)
        state, pivot = prefix_state_from_coefficients(coefficients, mul, div)
        assert len(state) == 4
        assert samples_from_prefix_state(state, mul, div) == samples
        assert coefficients_from_samples(samples, mul, div) == coefficients
        previous = outputs.setdefault(samples, coefficients)
        assert previous == coefficients
        states += 1
        pivots[pivot] += 1
    return {
        "field": "GF(8)",
        "valid_coefficients": states,
        "distinct_sample_vectors": len(outputs),
        "collisions": states - len(outputs),
        "pivot_counts": {"a0": pivots[0], "a1": pivots[1]},
        "maximum_live_field_words": 4,
        "result": "PASS",
    }


def sampled_gf12(count=2048):
    degree, modulus = 12, 0x1053
    mul, _, div = ops(degree, modulus)
    rng = Random(0xA466057)
    cases = []
    pivot_one_case = None
    while len(cases) < count - 1 or pivot_one_case is None:
        coefficients = tuple(rng.randrange(1 << degree) for _ in range(3)) + (
            rng.randrange(1, 1 << degree),
        )
        if not valid_shape(coefficients, mul, div):
            continue
        samples = sample_words(coefficients, mul, div)
        state, pivot = prefix_state_from_coefficients(coefficients, mul, div)
        case = (coefficients, samples, state, pivot)
        if pivot == 1 and pivot_one_case is None:
            pivot_one_case = case
            continue
        if len(cases) < count - 1:
            cases.append(case)
    cases.append(pivot_one_case)

    pivots = [0, 0]
    for coefficients, samples, state, pivot in cases:
        assert samples_from_prefix_state(state, mul, div) == samples
        assert coefficients_from_samples(samples, mul, div) == coefficients
        pivots[pivot] += 1
    return {
        "field": "GF(2^12)",
        "valid_coefficients": len(cases),
        "pivot_counts": {"a0": pivots[0], "a1": pivots[1]},
        "maximum_live_field_words": 4,
        "result": "PASS",
    }


def run_screen():
    return {
        "experiment": "exp-057-streaming-fixed-shape-decoder",
        "gf8": exhaustive_gf8(),
        "gf12": sampled_gf12(),
        "tail_transition": {
            "gf8": screen_gf8_tail_transition(),
            "gf12_verifier_form": screen_gf12_verifier_tail_transition(),
        },
        "scope": (
            "Classical reversible-state screen for coprime monic quadratic A "
            "and degree-1 B, with A nonzero at all four sample points. It does "
            "not compile the gate circuit or cover the other factorization shapes. "
            "The one-symbol tail transition is classical only."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
