"""Classically identify the phase factor missing from the native FMA scan.

This screen uses only GF(2^12) arithmetic. It does not import or execute the
DQI scanner, a circuit simulator, or the private-kernel gate helpers.
"""

from __future__ import annotations

from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-057"))

import fma_state_compression as fma
import phase_compatibility as phase


CASE_COUNT = 64
SEED = 0xA66062


def _derivative(poly: list[int]) -> list[int]:
    """Formal derivative over characteristic two."""
    result = [0] * max(1, len(poly) - 1)
    for degree in range(1, len(poly), 2):
        result[degree - 1] = poly[degree]
    return result


def run_screen(case_count: int = CASE_COUNT, seed: int = SEED) -> dict[str, object]:
    if case_count < 2 or case_count % 2:
        raise ValueError("case_count must be a positive even number")

    mul, inv = phase._field_ops()
    sample_node, sample_quotients = phase._node_polynomials(mul)
    dual_basis = phase._trace_dual_basis(mul)

    powers = [1]
    for _ in range(phase.CODE_POSITIONS - 1):
        powers.append(mul(powers[-1], 2))
    if len(set(powers)) != phase.CODE_POSITIONS or mul(powers[-1], 2) != 1:
        raise AssertionError("field element 2 did not enumerate all nonzero roots")

    sample_node_positions = {
        index for index, root in enumerate(powers) if root in phase.SAMPLE_NODES
    }
    position_by_root = {root: index for index, root in enumerate(powers)}
    kappas = [mul(point, point) ^ point ^ 2048 for point in range(0, 70, 2)]

    allowed_by_weight = {}
    padding_roots_by_weight = {}
    for weight in (31, 35):
        padding_roots = {
            root
            for index in range(weight + 1, 35, 2)
            for root in range(1, phase.FIELD_SIZE)
            if mul(root, root) ^ root ^ kappas[index] == 0
        }
        padding_roots_by_weight[weight] = padding_roots
        excluded_positions = (
            set(range(70))
            | sample_node_positions
            | {position_by_root[root] for root in padding_roots}
        )
        allowed_by_weight[weight] = [
            index for index in range(phase.CODE_POSITIONS)
            if index not in excluded_positions
        ]
    rng = Random(seed)

    sample_root_errors = 0
    padding_root_errors = 0
    identity_errors = 0
    fma_pair_errors = 0
    derivative_zero_errors = 0
    direct_phase_mismatches = 0
    derivative_correction_errors = 0
    weights = {31: 0, 35: 0}
    raw_phase_histogram = {"match": 0, "mismatch": 0}

    for case_index in range(case_count):
        weight = 31 if case_index % 2 == 0 else 35
        weights[weight] += 1
        positions = rng.sample(allowed_by_weight[weight], weight)
        errors = {
            powers[position]: rng.randrange(1, phase.FIELD_SIZE)
            for position in positions
        }
        sample_root_errors += sum(root in phase.SAMPLE_NODES for root in errors)
        padding_root_errors += sum(
            root in padding_roots_by_weight[weight] for root in errors
        )

        samples = phase._syndrome_to_samples(errors, sample_quotients, mul)
        basis = fma.modular_basis(samples, list(range(70)), mul)
        row = min(range(2), key=lambda index: fma.row_rank(basis, index))
        denominator, numerator = basis[row]
        leading_inverse = inv(denominator[-1])
        denominator = [mul(value, leading_inverse) for value in denominator]
        numerator = [mul(value, leading_inverse) for value in numerator]

        locator = phase._error_locator(errors, mul)
        evaluator = phase._error_evaluator(locator, sample_node, errors, mul)
        if denominator != locator or numerator != evaluator:
            fma_pair_errors += 1

        locator_derivative = _derivative(locator)
        expected_phase = 0
        direct_phase = 0
        predicted_correction = 0

        for root, error_value in errors.items():
            mask = rng.randrange(phase.FIELD_SIZE)
            mask_dual = phase._dual_mask_value(mask, dual_basis)

            node_denominator = mul(
                root, phase.fma.poly_eval(sample_node, root, mul)
            )
            if not node_denominator:
                raise AssertionError("an error root collided with a sample node")

            derivative_value = phase.fma.poly_eval(
                locator_derivative, root, mul
            )
            if not derivative_value:
                derivative_zero_errors += 1
                continue

            raw_value = mul(
                phase.fma.poly_eval(numerator, root, mul), inv(node_denominator)
            )
            derivative_value_prediction = mul(error_value, derivative_value)
            if raw_value != derivative_value_prediction:
                identity_errors += 1

            expected_phase ^= (error_value & mask).bit_count() & 1
            direct_phase ^= phase._trace(mul(raw_value, mask_dual), mul)
            predicted_correction ^= phase._trace(
                mul(mul(error_value, derivative_value ^ 1), mask_dual), mul
            )

        if direct_phase != expected_phase:
            direct_phase_mismatches += 1
            raw_phase_histogram["mismatch"] += 1
        else:
            raw_phase_histogram["match"] += 1

        if (direct_phase ^ predicted_correction) != expected_phase:
            derivative_correction_errors += 1

    return {
        "experiment": "exp-057-native-phase-derivative-diagnostic",
        "status": "PASS_IDENTITY"
        if not identity_errors
        and not fma_pair_errors
        and not derivative_zero_errors
        and not derivative_correction_errors
        else "FAIL_IDENTITY",
        "field": "GF(2^12), modulus 0x1053",
        "cases": case_count,
        "weights": weights,
        "roots_at_sample_nodes": sample_root_errors,
        "padding_root_collisions": padding_root_errors,
        "fma_pair_errors": fma_pair_errors,
        "simple_root_derivative_errors": derivative_zero_errors,
        "raw_phase_mismatches": direct_phase_mismatches,
        "raw_phase_histogram": raw_phase_histogram,
        "omega_over_node_equals_error_times_locator_derivative_errors": identity_errors,
        "derivative_correction_errors": derivative_correction_errors,
        "identity": "omega(r)/(r*P_data(r)) = error(r)*sigma_prime(r) at each simple error root",
        "decision": "The direct native-node phase differs by the sigma_prime factor. A valid bridge must account for omega/sigma_prime at error roots; this classical screen does not construct its reversible implementation or establish its cost.",
        "scope": "Classical GF(2^12) diagnosis only; no DQI scanner import, circuit simulation, reversible correction, cleanup, resource count, or official verifier.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
