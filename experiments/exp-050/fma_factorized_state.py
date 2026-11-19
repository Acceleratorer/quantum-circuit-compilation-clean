"""Screen a compact factorization of a minimum-rank FMA row.

The screen exhausts small valid Reed–Solomon error patterns and checks that
the normalized low row, factored by its common divisor, plus the samples at
common FMA nodes reconstructs the original transformed samples. It also counts
the field-word payload. This is a classical state-encoding screen, not a
reversible circuit or a gate-count estimate.
"""

from collections import Counter
from itertools import combinations, product
from random import Random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "exp-049"))
import fma_state_compression as fma  # noqa: E402


def node_polynomial(points, mul):
    result = [1]
    for point in points:
        result = fma.poly_mul(result, [point, 1], mul)
    return result


def error_syndrome(betas, values, n, mul):
    syndrome = [0] * n
    for beta, error in zip(betas, values):
        power = beta
        for index in range(n):
            syndrome[index] ^= mul(error, power)
            power = mul(power, beta)
    return syndrome


def expected_locator_evaluator(betas, values, node, mul):
    locator = [1]
    for beta in betas:
        locator = fma.poly_mul(locator, [beta, 1], mul)

    evaluator = [0]
    for beta, error in zip(betas, values):
        quotient = [1]
        for other in betas:
            if other != beta:
                quotient = fma.poly_mul(quotient, [other, 1], mul)
        factor = mul(mul(error, beta), fma.poly_eval(node, beta, mul))
        evaluator = fma.poly_add(
            evaluator,
            [mul(factor, coefficient) for coefficient in quotient],
        )
    return fma.trim(locator), fma.trim(evaluator)


def factorized_encoding(data, points, betas, values, degree, modulus, mul):
    node = node_polynomial(points, mul)
    expected_w, expected_n = expected_locator_evaluator(betas, values, node, mul)
    basis = fma.modular_basis(data, points, mul)
    row_index = min(range(2), key=lambda index: fma.row_rank(basis, index))
    w, n = (fma.trim(list(poly)) for poly in basis[row_index])
    pivot = w[-1] if w != [0] else n[-1]
    scale = fma.gf_inv(pivot, modulus, degree)
    w = fma.trim([mul(scale, value) for value in w])
    n = fma.trim([mul(scale, value) for value in n])
    assert (w, n) == (expected_w, expected_n)

    gcd, _, _ = fma.poly_xgcd(w, n, mul, modulus, degree)
    expected_common = [beta for beta in betas if beta in points]
    common_factor = node_polynomial(expected_common, mul)
    assert gcd == common_factor

    a, remainder = fma.poly_divmod(w, gcd, mul, modulus, degree)
    assert remainder == [0] and a[-1] == 1
    b, remainder = fma.poly_divmod(n, gcd, mul, modulus, degree)
    assert remainder == [0]

    exception_indices = [
        index for index, point in enumerate(points)
        if fma.poly_eval(gcd, point, mul) == 0
    ]
    exceptions = [data[index] for index in exception_indices]
    errors = len(betas)
    common_count = len(expected_common)

    # Store monic G and A without their leading 1s, B padded to deg(A), and
    # one sample per common node. Their total is exactly 2*errors words.
    g_payload = gcd[:-1]
    a_payload = a[:-1]
    b_width = errors - common_count
    b_payload = b[:b_width] + [0] * max(0, b_width - len(b))
    assert len(g_payload) == common_count
    assert len(a_payload) == errors - common_count
    assert len(b_payload) == errors - common_count
    assert len(exceptions) == common_count
    payload = tuple(g_payload + a_payload + b_payload + exceptions)
    assert len(payload) == 2 * errors

    reconstructed = []
    exception_cursor = 0
    for point in points:
        if fma.poly_eval(gcd, point, mul) == 0:
            reconstructed.append(exceptions[exception_cursor])
            exception_cursor += 1
        else:
            denominator = fma.poly_eval(a, point, mul)
            assert denominator != 0
            reconstructed.append(
                mul(fma.poly_eval(b, point, mul), fma.gf_inv(denominator, modulus, degree))
            )
    assert exception_cursor == len(exceptions)
    assert reconstructed == data

    # Include the two degrees as framing metadata; a fixed-width circuit still
    # needs to encode or derive them reversibly.
    state_key = (errors, common_count, tuple(gcd), tuple(a), tuple(b), tuple(exceptions))
    return state_key, {
        "errors": errors,
        "common_nodes": common_count,
        "payload_words": len(payload),
        "payload_bound": len(points),
        "reconstruction": "PASS",
    }


def screen_valid_domain(degree, modulus, n):
    q = 1 << degree
    if n > q:
        raise ValueError("the field must contain at least n distinct FMA points")
    points = list(range(n))
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    fibers = Counter()
    max_payload = 0
    max_common = 0
    patterns = 0

    for weight in range(n // 2 + 1):
        for betas in combinations(range(1, q), weight):
            for values in product(range(1, q), repeat=weight):
                syndrome = error_syndrome(betas, values, n, mul)
                data = fma.syndrome_to_fma_samples(syndrome, points, mul)
                key, result = factorized_encoding(
                    data, points, betas, values, degree, modulus, mul
                )
                fibers[key] += 1
                max_payload = max(max_payload, result["payload_words"])
                max_common = max(max_common, result["common_nodes"])
                patterns += 1

    return {
        "field": f"GF(2^{degree})",
        "points": n,
        "valid_patterns": patterns,
        "distinct_encodings": len(fibers),
        "max_preimage": max(fibers.values()),
        "injective": len(fibers) == patterns,
        "max_payload_words": max_payload,
        "max_common_nodes": max_common,
    }


def screen_dqi_cases():
    degree, modulus, n = 12, 0x1053, 70
    points = list(range(n))
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    rng = Random(0x50F1A)
    cases = [
        ((), ()),
        ((17,), (913,)),
        (tuple(rng.sample(range(70, 1 << degree), 31)),
         tuple(rng.randrange(1, 1 << degree) for _ in range(31))),
        (tuple([1, 2, 3, 4] + rng.sample(range(70, 1 << degree), 31)),
         tuple(rng.randrange(1, 1 << degree) for _ in range(35))),
        (tuple(rng.sample(range(1, 70), 35)),
         tuple(rng.randrange(1, 1 << degree) for _ in range(35))),
        (tuple(rng.sample(range(70, 1 << degree), 35)),
         tuple(rng.randrange(1, 1 << degree) for _ in range(35))),
    ]
    results = []
    for betas, values in cases:
        syndrome = error_syndrome(betas, values, n, mul)
        data = fma.syndrome_to_fma_samples(syndrome, points, mul)
        _, result = factorized_encoding(data, points, betas, values, degree, modulus, mul)
        results.append(result)
    return results


def main():
    for result in (
        screen_valid_domain(2, 0b111, 4),
        screen_valid_domain(3, 0b1011, 6),
        screen_valid_domain(4, 0b10011, 4),
    ):
        print(result)
    for result in screen_dqi_cases():
        print(result)


if __name__ == "__main__":
    main()
