"""Check Newton insertion for scanner residues on a small finite field.

This is a classical identity screen. Each insertion supplies an error root and
its desired scanner value; the current FMA path instead starts from 70
syndrome-derived samples. No reversible circuit is built here.
"""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


DEGREE = 3
MODULUS = 0b1011
NODE_POLYNOMIAL = (5, 3, 1)  # X^2 + 3X + 5 in GF(8).


def _trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def _add(left, right):
    return _trim([
        (left[index] if index < len(left) else 0)
        ^ (right[index] if index < len(right) else 0)
        for index in range(max(len(left), len(right)))
    ])


def _eval(poly, value, mul):
    result = 0
    for coefficient in reversed(poly):
        result = mul(result, value) ^ coefficient
    return result


def _times_linear(poly, root, mul):
    result = [0] * (len(poly) + 1)
    for index, coefficient in enumerate(poly):
        result[index] ^= mul(root, coefficient)
        result[index + 1] ^= coefficient
    return _trim(result)


def _quotient_by_root(poly, root, mul):
    quotient = [0] * (len(poly) - 1)
    quotient[-1] = poly[-1]
    for index in range(len(poly) - 2, 0, -1):
        quotient[index - 1] = poly[index] ^ mul(root, quotient[index])
    if poly[0] ^ mul(root, quotient[0]):
        raise ValueError("root does not divide locator")
    return quotient


def _direct_interpolant(errors, mul, inv):
    locator = [1]
    for root, _ in errors:
        locator = _times_linear(locator, root, mul)

    numerator = [0]
    for root, error in errors:
        quotient = _quotient_by_root(locator, root, mul)
        scanner_value = mul(
            mul(error, root), _eval(NODE_POLYNOMIAL, root, mul)
        )
        derivative = _eval(quotient, root, mul)
        scale = mul(scanner_value, inv(derivative))
        numerator = _add(
            numerator,
            [mul(scale, coefficient) for coefficient in quotient],
        )
    return _trim(numerator)


def _newton_interpolant(errors, mul, inv):
    numerator = [0]
    locator = [1]
    for root, error in errors:
        scanner_value = mul(
            mul(error, root), _eval(NODE_POLYNOMIAL, root, mul)
        )
        denominator = _eval(locator, root, mul)
        if denominator == 0:
            raise ValueError("error roots must be distinct")
        correction = mul(
            scanner_value ^ _eval(numerator, root, mul), inv(denominator)
        )
        numerator = _add(
            numerator,
            [mul(correction, coefficient) for coefficient in locator],
        )
        locator = _times_linear(locator, root, mul)
    return _trim(numerator), _trim(locator)


def run_screen():
    mul = lambda left, right: fma.gf_mul(left, right, MODULUS, DEGREE)
    inv = lambda value: fma.gf_inv(value, MODULUS, DEGREE)
    cases = 0
    for weight in range(1, 5):
        for roots in combinations(range(1, 1 << DEGREE), weight):
            for values in product(range(1, 1 << DEGREE), repeat=weight):
                errors = tuple(zip(roots, values))
                expected = _direct_interpolant(errors, mul, inv)
                actual, locator = _newton_interpolant(errors, mul, inv)
                assert actual == expected
                assert len(locator) == weight + 1 and locator[-1] == 1
                for root, error in errors:
                    expected_value = mul(
                        mul(error, root), _eval(NODE_POLYNOMIAL, root, mul)
                    )
                    assert _eval(actual, root, mul) == expected_value
                cases += 1

    # Full-width Newton update: 2(n-1) Horner products, n-1 products for
    # each polynomial update, and one product for the divided difference.
    # Desired scanner values are treated as inputs; inverses are not counted.
    weight = 35
    variable_products = sum(4 * n - 3 for n in range(1, weight + 1))
    product_cost_t = 42
    estimated_t = variable_products * product_cost_t
    remaining_gate_t = 36_183.74
    return {
        "experiment": "exp-057-newton-residue-screen",
        "status": "PASS" if cases == 97_118 else "FAIL",
        "field": "GF(8)",
        "node_polynomial": list(NODE_POLYNOMIAL),
        "error_weights": [1, 2, 3, 4],
        "exhaustive_distinct_root_and_nonzero_value_cases": cases,
        "newton_equals_direct_lagrange_cases": cases,
        "coefficient_or_root_value_mismatches": 0,
        "gf12_straightforward_gate_proxy": {
            "error_weight": weight,
            "variable_field_products": variable_products,
            "product_cost_t": product_cost_t,
            "estimated_product_t": estimated_t,
            "remaining_fma_to_scan_gate_t": remaining_gate_t,
            "over_gate_before_inverses_and_uncomputation_t": estimated_t - remaining_gate_t,
            "interpretation": "operation-count estimate for this recurrence, not a lower bound",
        },
        "input_contract": {
            "newton_requires": "each error root and its desired scanner residue value",
            "current_exp057_fma_receives": "70 syndrome-derived sample values",
            "direct_update_map_established": False,
        },
        "scope": "Classical recurrence identity and rough arithmetic screen only; no reversible circuit, cleanup, or official verifier.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
