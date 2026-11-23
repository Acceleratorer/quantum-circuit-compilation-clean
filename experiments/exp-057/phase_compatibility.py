"""Classical check of the exp-057 FMA samples against the DQI MBUC phase."""

from __future__ import annotations

from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


DEGREE = 12
MODULUS = 0x1053
FIELD_SIZE = 1 << DEGREE
CODE_POSITIONS = FIELD_SIZE - 1
SAMPLE_NODES = tuple(range(70))
PREFIX_NODES = (1, 2, 3)


def _field_ops():
    mul = lambda a, b: fma.gf_mul(a, b, MODULUS, DEGREE)
    inv = lambda a: fma.gf_inv(a, MODULUS, DEGREE)
    return mul, inv


def _quotient_by_root(poly, root, mul):
    """Return q where poly(X) = (X + root) q(X)."""
    quotient = [0] * (len(poly) - 1)
    quotient[-1] = poly[-1]
    for index in range(len(poly) - 2, 0, -1):
        quotient[index - 1] = poly[index] ^ mul(root, quotient[index])
    if poly[0] ^ mul(root, quotient[0]):
        raise ValueError("root does not divide polynomial")
    return quotient


def _node_polynomials(mul):
    node = [1]
    for point in SAMPLE_NODES:
        node = fma.poly_mul(node, [point, 1], mul)
    quotients = {
        point: _quotient_by_root(node, point, mul) for point in SAMPLE_NODES
    }
    return node, quotients


def _syndrome_to_samples(errors, quotients, mul):
    syndrome = [0] * len(SAMPLE_NODES)
    for root, value in errors.items():
        power = root
        for index in range(len(syndrome)):
            syndrome[index] ^= mul(value, power)
            power = mul(power, root)
    return tuple(
        _xor_products(quotient, syndrome, mul) for quotient in quotients.values()
    )


def _xor_products(left, right, mul):
    value = 0
    for a, b in zip(left, right):
        value ^= mul(a, b)
    return value


def _error_locator(errors, mul):
    sigma = [1]
    for root in errors:
        sigma = fma.poly_mul(sigma, [root, 1], mul)
    return sigma


def _error_evaluator(sigma, node, errors, mul):
    omega = [0]
    for root, value in errors.items():
        residue = mul(mul(value, root), fma.poly_eval(node, root, mul))
        if residue == 0:
            continue
        quotient = _quotient_by_root(sigma, root, mul)
        if len(omega) < len(quotient):
            omega.extend([0] * (len(quotient) - len(omega)))
        for index, coefficient in enumerate(quotient):
            omega[index] ^= mul(residue, coefficient)
    return omega


def _locator_roots(sigma, mul):
    return [
        value
        for value in range(1, FIELD_SIZE)
        if fma.poly_eval(sigma, value, mul) == 0
    ]


def _recover_error_values(sigma, omega, samples, node, node_quotients, roots, mul, inv):
    derivative = [0] * (len(sigma) - 1)
    for index in range(1, len(sigma), 2):
        derivative[index - 1] = sigma[index]
    node_set = set(SAMPLE_NODES)
    recovered = {}

    for root in roots:
        if root in node_set:
            continue
        denominator = mul(
            mul(
                fma.poly_eval(derivative, root, mul),
                root,
            ),
            fma.poly_eval(node, root, mul),
        )
        recovered[root] = mul(fma.poly_eval(omega, root, mul), inv(denominator))

    for root in roots:
        if root not in node_set:
            continue
        quotient = node_quotients[root]
        other_contributions = 0
        for other_root, value in recovered.items():
            other_contributions ^= mul(
                mul(value, other_root), fma.poly_eval(quotient, other_root, mul)
            )
        denominator = mul(root, fma.poly_eval(quotient, root, mul))
        recovered[root] = mul(samples[root] ^ other_contributions, inv(denominator))
    return recovered


def _trace(value, mul):
    result = 0
    for _ in range(DEGREE):
        result ^= value
        value = mul(value, value)
    if result not in (0, 1):
        raise AssertionError("field trace did not land in GF(2)")
    return result


def _trace_dual_basis(mul):
    rows = [
        [
            *[
                _trace(mul(1 << row, 1 << column), mul)
                for column in range(DEGREE)
            ],
            *[int(row == column) for column in range(DEGREE)],
        ]
        for row in range(DEGREE)
    ]
    for column in range(DEGREE):
        pivot = next(row for row in range(column, DEGREE) if rows[row][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        for row in range(DEGREE):
            if row != column and rows[row][column]:
                rows[row] = [left ^ right for left, right in zip(rows[row], rows[column])]
    dual = [
        sum(rows[row][DEGREE + bit] << row for row in range(DEGREE))
        for bit in range(DEGREE)
    ]
    for bit, value in enumerate(dual):
        if any(_trace(mul(1 << row, value), mul) != (row == bit) for row in range(DEGREE)):
            raise AssertionError("invalid trace-dual basis")
    return dual


def _dual_mask_value(mask, dual):
    value = 0
    for bit, basis_value in enumerate(dual):
        if (mask >> bit) & 1:
            value ^= basis_value
    return value


def _poly_remainder(poly, divisor, mul):
    remainder = poly[:]
    while len(remainder) >= len(divisor):
        offset = len(remainder) - len(divisor)
        leading = remainder[-1]
        for index, coefficient in enumerate(divisor):
            remainder[offset + index] ^= mul(leading, coefficient)
        while len(remainder) > 1 and remainder[-1] == 0:
            remainder.pop()
    return remainder


def _aggregate_phase(sigma, omega, node, errors, decoded, mbuc, position_by_root, dual, mul, inv):
    derivative = [0] * (len(sigma) - 1)
    for index in range(1, len(sigma), 2):
        derivative[index - 1] = sigma[index]

    interpolant = [0]
    residue_sum = 0
    node_phase = 0
    for root in errors:
        sigma_prime = fma.poly_eval(derivative, root, mul)
        if root in SAMPLE_NODES:
            g_value = 0
            node_phase ^= (
                decoded[root] & mbuc[position_by_root[root]]
            ).bit_count() & 1
        else:
            denominator = mul(root, fma.poly_eval(node, root, mul))
            mask_value = _dual_mask_value(mbuc[position_by_root[root]], dual)
            g_value = mul(mask_value, inv(denominator))

        quotient = _quotient_by_root(sigma, root, mul)
        scale = mul(g_value, inv(sigma_prime))
        if len(interpolant) < len(quotient):
            interpolant.extend([0] * (len(quotient) - len(interpolant)))
        for index, coefficient in enumerate(quotient):
            interpolant[index] ^= mul(scale, coefficient)
        residue_sum ^= mul(
            mul(fma.poly_eval(omega, root, mul), g_value), inv(sigma_prime)
        )

    remainder = _poly_remainder(fma.poly_mul(omega, interpolant, mul), sigma, mul)
    degree = len(errors)
    coefficient = remainder[degree - 1] if len(remainder) >= degree else 0
    aggregate_phase = _trace(coefficient, mul) ^ node_phase
    return aggregate_phase, coefficient == residue_sum


def run_screen(case_count=32, seed=0xA66060):
    if case_count < 2 or case_count % 2:
        raise ValueError("case_count must be a positive even number")

    mul, inv = _field_ops()
    node, quotients = _node_polynomials(mul)
    dual = _trace_dual_basis(mul)
    powers = []
    root = 1
    for _ in range(CODE_POSITIONS):
        powers.append(root)
        root = mul(root, 2)
    if root != 1 or len(set(powers)) != CODE_POSITIONS:
        raise AssertionError("2 is not the verifier field's primitive element")
    position_by_root = {value: index for index, value in enumerate(powers)}

    rng = Random(seed)
    phase_mismatches = 0
    residue_identity_errors = 0
    aggregate_phase_mismatches = 0
    value_mismatches = 0
    forced_nodes = set()
    weights = {31: 0, 35: 0}

    for case_index in range(case_count):
        weight = 31 if case_index < case_count // 2 else 35
        weights[weight] += 1
        forced_root = PREFIX_NODES[case_index % len(PREFIX_NODES)]
        forced_position = position_by_root[forced_root]
        positions = rng.sample(range(CODE_POSITIONS), weight)
        if forced_position not in positions:
            positions[-1] = forced_position
        forced_nodes.add(forced_root)

        errors = {
            powers[position]: rng.randrange(1, FIELD_SIZE)
            for position in positions
        }
        samples = _syndrome_to_samples(errors, quotients, mul)
        sigma = _error_locator(errors, mul)
        omega = _error_evaluator(sigma, node, errors, mul)
        roots = _locator_roots(sigma, mul)
        if set(roots) != set(errors):
            value_mismatches += 1
            continue

        decoded = _recover_error_values(
            sigma, omega, samples, node, quotients, roots, mul, inv
        )
        if decoded != errors:
            value_mismatches += 1

        mbuc = [rng.randrange(FIELD_SIZE) for _ in range(CODE_POSITIONS)]
        expected_phase = sum(
            (value & mbuc[position_by_root[location]]).bit_count()
            for location, value in errors.items()
        ) & 1
        decoded_phase = sum(
            (value & mbuc[position_by_root[location]]).bit_count()
            for location, value in decoded.items()
        ) & 1
        phase_mismatches += expected_phase != decoded_phase
        aggregate_phase, residue_matches = _aggregate_phase(
            sigma,
            omega,
            node,
            errors,
            decoded,
            mbuc,
            position_by_root,
            dual,
            mul,
            inv,
        )
        residue_identity_errors += not residue_matches
        aggregate_phase_mismatches += aggregate_phase != expected_phase

    return {
        "status": "PASS"
        if not value_mismatches
        and not phase_mismatches
        and not residue_identity_errors
        and not aggregate_phase_mismatches
        else "FAIL",
        "cases": case_count,
        "weights": weights,
        "forced_fma_prefix_roots": sorted(forced_nodes),
        "recovered_error_values": case_count * 33,
        "value_mismatches": value_mismatches,
        "phase_mismatches": phase_mismatches,
        "residue_identity_errors": residue_identity_errors,
        "aggregate_phase_mismatches": aggregate_phase_mismatches,
        "scope": "Classical Forney/FMA and residue-aggregation checks only; no reversible phase circuit, mask transform, cleanup, resource count, or official verifier.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
