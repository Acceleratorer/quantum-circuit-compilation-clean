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


def run_screen(case_count=32, seed=0xA66060):
    if case_count < 2 or case_count % 2:
        raise ValueError("case_count must be a positive even number")

    mul, inv = _field_ops()
    node, quotients = _node_polynomials(mul)
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

    return {
        "status": "PASS" if not value_mismatches and not phase_mismatches else "FAIL",
        "cases": case_count,
        "weights": weights,
        "forced_fma_prefix_roots": sorted(forced_nodes),
        "recovered_error_values": case_count * 33,
        "value_mismatches": value_mismatches,
        "phase_mismatches": phase_mismatches,
        "scope": "Classical Forney/FMA phase compatibility only; no reversible phase circuit, cleanup, resource count, or official verifier.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
