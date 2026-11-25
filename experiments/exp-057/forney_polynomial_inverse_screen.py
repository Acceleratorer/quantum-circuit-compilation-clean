"""Count a direct polynomial Forney-residue conversion on verifier-shaped cases."""

from __future__ import annotations

from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "experiments" / name) for name in ("exp-049", "exp-057")]

import fma_state_compression as fma
import phase_compatibility as phase


CASE_COUNT = 64
SEED = 0xA66062
PRODUCT_COST_T = 42
INVERSE_COST_T = 66
REPLACEMENT_BUDGET_T = 36183.74


def _trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def _derivative(poly: list[int]) -> list[int]:
    return _trim([poly[i] if i & 1 else 0 for i in range(1, len(poly))] or [0])


def _add(left: list[int], right: list[int]) -> list[int]:
    return _trim([
        (left[i] if i < len(left) else 0) ^ (right[i] if i < len(right) else 0)
        for i in range(max(len(left), len(right)))
    ])


class _FieldCounts:
    def __init__(self, mul, inv):
        self._mul = mul
        self._inv = inv
        self.products = 0
        self.inversions = 0

    def multiply(self, left: int, right: int) -> int:
        self.products += 1
        return self._mul(left, right)

    def inverse(self, value: int) -> int:
        self.inversions += 1
        return self._inv(value)


def _divmod_poly(dividend: list[int], divisor: list[int], counts: _FieldCounts):
    dividend, divisor = _trim(dividend), _trim(divisor)
    if divisor == [0]:
        raise ZeroDivisionError("polynomial divisor is zero")
    quotient = [0] * max(1, len(dividend) - len(divisor) + 1)
    inverse_lead = counts.inverse(divisor[-1])
    while dividend != [0] and len(dividend) >= len(divisor):
        shift = len(dividend) - len(divisor)
        factor = counts.multiply(dividend[-1], inverse_lead)
        quotient[shift] ^= factor
        # The leading product is known to cancel by construction.
        dividend[-1] = 0
        for index, coefficient in enumerate(divisor[:-1]):
            dividend[shift + index] ^= counts.multiply(factor, coefficient)
        dividend = _trim(dividend)
    return _trim(quotient), dividend


def _poly_multiply(left: list[int], right: list[int], counts: _FieldCounts):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] ^= counts.multiply(a, b)
    return _trim(result)


def _xgcd(left: list[int], right: list[int], counts: _FieldCounts):
    r0, r1 = _trim(list(left)), _trim(list(right))
    s0, s1, t0, t1 = [1], [0], [0], [1]
    while r1 != [0]:
        quotient, remainder = _divmod_poly(r0, r1, counts)
        r0, r1 = r1, remainder
        s0, s1 = s1, _add(s0, _poly_multiply(quotient, s1, counts))
        t0, t1 = t1, _add(t0, _poly_multiply(quotient, t1, counts))
    scale = counts.inverse(r0[-1])
    return (
        [counts.multiply(value, scale) for value in s0],
        [counts.multiply(value, scale) for value in t0],
        r0,
    )


def _remainder(poly: list[int], modulus: list[int], counts: _FieldCounts):
    return _divmod_poly(poly, modulus, counts)[1]


def run_screen(case_count: int = CASE_COUNT, seed: int = SEED) -> dict[str, object]:
    if case_count < 2 or case_count % 2:
        raise ValueError("case_count must be a positive even number")

    mul, inv = phase._field_ops()
    _, node_quotients = phase._node_polynomials(mul)
    powers = [1]
    for _ in range(phase.CODE_POSITIONS - 1):
        powers.append(mul(powers[-1], 2))
    position_by_root = {root: index for index, root in enumerate(powers)}
    sample_node_positions = {
        index for index, root in enumerate(powers) if root in phase.SAMPLE_NODES
    }
    kappas = [mul(point, point) ^ point ^ 2048 for point in range(0, 70, 2)]
    allowed_by_weight = {}
    for weight in (31, 35):
        padding_roots = {
            root
            for index in range(weight + 1, 35, 2)
            for root in range(1, phase.FIELD_SIZE)
            if mul(root, root) ^ root ^ kappas[index] == 0
        }
        excluded = (
            set(range(70))
            | sample_node_positions
            | {position_by_root[root] for root in padding_roots}
        )
        allowed_by_weight[weight] = [
            index for index in range(phase.CODE_POSITIONS) if index not in excluded
        ]
    rng = Random(seed)
    product_counts, inverse_counts = [], []
    direct_products, direct_inversions = [], []
    residue_checks = direct_residue_checks = 0

    for case in range(case_count):
        weight = 31 if case % 2 == 0 else 35
        errors = {
            powers[position]: rng.randrange(1, phase.FIELD_SIZE)
            for position in rng.sample(allowed_by_weight[weight], weight)
        }
        samples = phase._syndrome_to_samples(errors, node_quotients, mul)
        basis = fma.modular_basis(samples, list(range(70)), mul)
        row = min(range(2), key=lambda index: fma.row_rank(basis, index))
        sigma, omega = (_trim(poly) for poly in basis[row])
        scale = inv(sigma[-1])
        sigma = [mul(value, scale) for value in sigma]
        omega = [mul(value, scale) for value in omega]
        sigma_prime = _derivative(sigma)

        counts = _FieldCounts(mul, inv)
        _, inverse_sigma_prime, gcd = _xgcd(sigma, sigma_prime, counts)
        if len(gcd) != 1 or gcd[0] == 0:
            raise AssertionError("sample locator is not squarefree")
        converted = _remainder(
            _poly_multiply(omega, inverse_sigma_prime, counts), sigma, counts
        )
        for root in errors:
            denominator = fma.poly_eval(sigma_prime, root, mul)
            if not denominator:
                raise AssertionError("zero locator derivative at an error root")
            expected = mul(fma.poly_eval(omega, root, mul), inv(denominator))
            if fma.poly_eval(converted, root, mul) != expected:
                raise AssertionError("converted residue does not match omega/sigma_prime")
            residue_checks += 1
        product_counts.append(counts.products)
        inverse_counts.append(counts.inversions)

        # Solve sigma_prime * A = omega (mod sigma) without materializing the
        # complete inverse polynomial first.
        direct = _FieldCounts(mul, inv)
        r0, r1, a0, a1 = list(sigma), list(sigma_prime), [0], list(omega)
        while r1 != [0]:
            quotient, remainder = _divmod_poly(r0, r1, direct)
            next_a = _add(a0, _poly_multiply(quotient, a1, direct))
            r0, r1, a0, a1 = r1, remainder, a1, next_a
        if len(r0) != 1 or r0[0] == 0:
            raise AssertionError("sample locator derivative is not invertible")
        normalization = direct.inverse(r0[0])
        a0 = [direct.multiply(value, normalization) for value in a0]
        direct_residue = _remainder(a0, list(sigma), direct)
        for root in errors:
            expected = mul(
                fma.poly_eval(omega, root, mul),
                inv(fma.poly_eval(sigma_prime, root, mul)),
            )
            if fma.poly_eval(direct_residue, root, mul) != expected:
                raise AssertionError("direct-RHS residue does not match omega/sigma_prime")
            direct_residue_checks += 1
        direct_products.append(direct.products)
        direct_inversions.append(direct.inversions)

    costs = [
        products * PRODUCT_COST_T + inversions * INVERSE_COST_T
        for products, inversions in zip(product_counts, inverse_counts)
    ]
    direct_costs = [
        products * PRODUCT_COST_T + inversions * INVERSE_COST_T
        for products, inversions in zip(direct_products, direct_inversions)
    ]
    return {
        "experiment": "exp-057-forney-polynomial-inverse-screen",
        "status": "PASS_RESIDUES" if residue_checks > 0 else "FAIL_RESIDUES",
        "field": "GF(2^12), modulus 0x1053",
        "seed": hex(seed),
        "cases": case_count,
        "weights": {"31": case_count // 2, "35": case_count // 2},
        "gcd_one_cases": case_count,
        "forney_residue_checks": residue_checks,
        "field_products_mean_max": [
            round(sum(product_counts) / case_count, 1), max(product_counts)
        ],
        "field_inversions_mean_max": [
            round(sum(inverse_counts) / case_count, 1), max(inverse_counts)
        ],
        "estimated_T_mean_max": [round(sum(costs) / case_count, 1), max(costs)],
        "inverse_then_multiply_residue_checks": residue_checks,
        "direct_rhs_field_products_mean_max": [
            round(sum(direct_products) / case_count, 1), max(direct_products)
        ],
        "direct_rhs_field_inversions_mean_max": [
            round(sum(direct_inversions) / case_count, 1), max(direct_inversions)
        ],
        "direct_rhs_residue_checks": direct_residue_checks,
        "direct_rhs_estimated_T_mean_max": [
            round(sum(direct_costs) / case_count, 1), max(direct_costs)
        ],
        "replacement_budget_T": REPLACEMENT_BUDGET_T,
        "within_budget": max(costs + direct_costs) <= REPLACEMENT_BUDGET_T,
        "scope": (
            "Classical sample-path operation count for ordinary polynomial EEA and "
            "remainder arithmetic. No reversible circuit, fixed-branch upper bound, "
            "workspace/cleanup, or official verifier."
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
