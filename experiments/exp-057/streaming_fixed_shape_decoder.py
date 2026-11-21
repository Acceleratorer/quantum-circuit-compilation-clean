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
        "scope": (
            "Classical reversible-state screen for coprime monic quadratic A "
            "and degree-1 B, with A nonzero at all four sample points. It does "
            "not compile the gate circuit or cover the other factorization shapes."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
