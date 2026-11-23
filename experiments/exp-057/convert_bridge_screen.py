"""Single-pattern diagnostic for the exp-057 FMA-to-residue phase bridge.

Run locally with:
    uv run --no-project --with numpy --with kickmix==1.0.0 python \
        experiments/exp-057/convert_bridge_screen.py

The reference pair is a control for the existing CONVERT + scan circuit. This
does not implement the complete FMA schedule or qualify a submission.
"""

from __future__ import annotations

import json
from pathlib import Path
import random
import sys

import numpy as np
import kickmix as km


ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "experiments" / "exp-049"),
    str(ROOT / "experiments" / "exp-057"),
    str(ROOT / "src" / "dqi" / "pro_q2_897"),
]
sys.modules.setdefault("circ", km)
sys.modules.setdefault("kickmix.kickmix", km)

import fma_state_compression as fma
import phase_compatibility as phase
from exp.convert_short_hankel.phase34 import convert_safe
from exp.scan.scan import scan
from exp.decoder.extract import constants as scan_constants
from exp.mask_projection.kernel import trace_columns
import field as arithmetic


def _apply_linear(columns, value):
    result = 0
    for bit, column in enumerate(columns):
        if value >> bit & 1:
            result ^= column
    return result


def _residual_masks(masks, powers, multiply):
    trace = trace_columns()
    dual = arithmetic.inverse_columns(trace)
    values = [_apply_linear(dual, masks[index]) for index in range(70)]
    augmented = []
    for point, value in zip(powers[:70], values):
        row = []
        power = point
        for _ in range(70):
            row.append(power)
            power = multiply(power, point)
        augmented.append(row + [value])

    inverse = lambda value: fma.gf_inv(value, phase.MODULUS, phase.DEGREE)
    for column in range(70):
        pivot = next(
            row for row in range(column, 70) if augmented[row][column]
        )
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        scale = inverse(augmented[column][column])
        augmented[column] = [multiply(value, scale) for value in augmented[column]]
        for row in range(70):
            factor = augmented[row][column]
            if row != column and factor:
                augmented[row] = [
                    left ^ multiply(factor, right)
                    for left, right in zip(augmented[row], augmented[column])
                ]

    coefficients = [augmented[index][-1] for index in range(70)]
    residual = []
    for point, mask in zip(powers, masks):
        value = 0
        for coefficient in reversed(coefficients):
            value = multiply(value, point) ^ coefficient
        value = multiply(value, point)
        residual.append(mask ^ _apply_linear(trace, value))
    if any(residual[:70]):
        raise AssertionError("mask projection did not clear the selected prefix")
    return residual


def _padded_pair(numerator, denominator, weight, kappas, multiply):
    padding = [1]
    for index in range(weight + 1, 35, 2):
        padding = fma.poly_mul(padding, [kappas[index], 1, 1], multiply)
    top = fma.poly_mul(numerator, padding, multiply)
    bottom = fma.poly_mul(denominator, padding, multiply)
    if len(top) > 35 or len(bottom) != 36 or bottom[-1] != 1:
        raise AssertionError("invalid degree-35 padded pair")
    return top + [0] * (35 - len(top)), bottom[:35]


def run_screen():
    multiply, _ = phase._field_ops()
    _, sample_quotients = phase._node_polynomials(multiply)
    rng = random.Random(0xA66060)
    powers = []
    beta = 1
    for _ in range(phase.CODE_POSITIONS):
        powers.append(beta)
        beta = multiply(beta, 2)
    position_by_root = {value: index for index, value in enumerate(powers)}

    weight = 31
    positions = rng.sample(range(70, phase.CODE_POSITIONS), weight)
    errors = {powers[index]: rng.randrange(1, phase.FIELD_SIZE) for index in positions}
    samples = phase._syndrome_to_samples(errors, sample_quotients, multiply)
    basis = fma.modular_basis(samples, list(range(70)), multiply)
    row = min(range(2), key=lambda index: fma.row_rank(basis, index))
    denominator, numerator = basis[row]
    inverse_lead = fma.gf_inv(denominator[-1], phase.MODULUS, phase.DEGREE)
    denominator = [multiply(value, inverse_lead) for value in denominator]
    numerator = [multiply(value, inverse_lead) for value in numerator]
    locator = phase._error_locator(errors, multiply)
    if denominator != locator:
        raise AssertionError("FMA basis did not recover the monic locator")

    _, kappas, scan_node, _ = scan_constants(35)
    fma_pair = _padded_pair(numerator, denominator, weight, kappas, multiply)

    # The DQI reference pair uses residues e*beta*P_scan(beta); it checks the
    # circuit harness independently of the candidate FMA numerator.
    reference_numerator = [0]
    for root, error in errors.items():
        residue = multiply(
            multiply(error, root), fma.poly_eval(scan_node, root, multiply)
        )
        quotient = phase._quotient_by_root(locator, root, multiply)
        if len(reference_numerator) < len(quotient):
            reference_numerator.extend(
                [0] * (len(quotient) - len(reference_numerator))
            )
        for index, coefficient in enumerate(quotient):
            reference_numerator[index] ^= multiply(residue, coefficient)
    reference_pair = _padded_pair(
        reference_numerator, locator, weight, kappas, multiply
    )

    masks = [rng.randrange(phase.FIELD_SIZE) for _ in range(phase.CODE_POSITIONS)]
    residual = _residual_masks(masks, powers, multiply)
    expected_phase = sum(
        (error & residual[position_by_root[root]]).bit_count()
        for root, error in errors.items()
    ) & 1

    builder = km.CircuitBuilder()
    numerator_words = [builder.alloc_qubits(12) for _ in range(35)]
    denominator_words = [builder.alloc_qubits(12) for _ in range(35)]
    mask_words = [builder.alloc_bits(12) for _ in range(phase.CODE_POSITIONS)]
    phase_token = convert_safe(builder, numerator_words, denominator_words, monic_root=True)
    scan(builder, numerator_words, denominator_words, mask_words, skip_points=tuple(range(70)))
    convert_safe(
        builder,
        numerator_words,
        denominator_words,
        True,
        phase_token=phase_token,
    )
    circuit = builder.finish_circuit()

    pairs = (fma_pair, reference_pair)
    simulator = km.Simulator(
        batch_size=2,
        debug_print=False,
        counting_operations=True,
        seed=0,
    )
    simulator.use_same_registers_as(circuit)

    def bit_columns(values):
        values = np.asarray(values, dtype=np.uint32)
        return np.stack([((values >> bit) & 1).astype(bool) for bit in range(12)])

    for index, register in enumerate(numerator_words):
        simulator.write_across_shots(
            register, bit_columns([pair[0][index] for pair in pairs])
        )
    for index, register in enumerate(denominator_words):
        simulator.write_across_shots(
            register, bit_columns([pair[1][index] for pair in pairs])
        )
    residual_array = np.asarray(residual, dtype=np.uint32)
    mask_bits = np.stack(
        [((residual_array >> bit) & 1).astype(bool) for bit in range(12)],
        axis=1,
    ).reshape(-1, 1)
    mask_bits = np.repeat(mask_bits, 2, axis=1)
    all_masks = km.array([bit for word in mask_words for bit in word])
    simulator.write_across_shots(all_masks, mask_bits)
    simulator.do(circuit)

    observed = simulator.read_phase_flipped_across_shots().astype(int).tolist()
    for index, register in enumerate(numerator_words):
        if not np.array_equal(
            simulator.read_across_shots(register),
            bit_columns([pair[0][index] for pair in pairs]),
        ):
            raise AssertionError("CONVERT did not restore the numerator bank")
    for index, register in enumerate(denominator_words):
        if not np.array_equal(
            simulator.read_across_shots(register),
            bit_columns([pair[1][index] for pair in pairs]),
        ):
            raise AssertionError("CONVERT did not restore the denominator bank")
    if not np.array_equal(simulator.read_across_shots(all_masks), mask_bits):
        raise AssertionError("scan did not restore the mask bank")

    live = set().union(*(set(register) for register in numerator_words + denominator_words))
    scratch = [
        km.q(index)
        for index in range(circuit.num_qubits)
        if km.q(index) not in live
    ]
    if scratch and np.any(simulator.read_across_shots(km.array(scratch))):
        raise AssertionError("CONVERT/scan left dirty scratch")

    return {
        "experiment": "exp-057-fma-convert-scan-bridge",
        "status": "DIRECT_FMA_PAIR_FAILED" if observed[0] != expected_phase else "DIRECT_FMA_PAIR_PASSED",
        "error_weight": weight,
        "paired_inputs": ["FMA low-rank row", "canonical DQI residue pair"],
        "expected_phase": expected_phase,
        "observed_phase": {
            "fma_low_rank_row": observed[0],
            "canonical_dqi_residue_pair": observed[1],
        },
        "canonical_reference_matches": observed[1] == expected_phase,
        "input_pair_restored": True,
        "residual_masks_restored": True,
        "clean_scratch_qubits": len(scratch),
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "simulated_toffoli_like_gates": simulator.operation_statistics().num_toffoli_like,
        "scope": "One seeded non-prefix error pattern; full FMA schedule, verifier, and submission are not included.",
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
