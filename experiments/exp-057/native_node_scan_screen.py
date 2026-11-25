"""Measure whether the FMA-native node polynomial can replace CONVERT."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(ROOT / "experiments" / "exp-049"),
    str(ROOT / "experiments" / "exp-057"),
    str(ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "decoder"),
    str(ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "scan"),
    str(ROOT / "src" / "dqi" / "pro_q2_897"),
    str(ROOT.parents[1] / ".venv" / "Lib" / "site-packages"),
]

import kickmix as km

sys.modules.setdefault("circ", km)
sys.modules.setdefault("kickmix.kickmix", km)

import numpy as np
import fma_state_compression as fma
import phase_compatibility as phase
import convert_bridge_screen as bridge
from extract import constants as scan_constants
from scan import scan


def bit_columns(values):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack(
        [((values >> bit) & 1).astype(bool) for bit in range(phase.DEGREE)],
        axis=0,
    )


def run_screen():
    mul, inv = phase._field_ops()
    sample_node, sample_quotients = phase._node_polynomials(mul)
    _, kappas, _, _ = scan_constants(35)

    powers = [1]
    for _ in range(phase.CODE_POSITIONS - 1):
        powers.append(mul(powers[-1], 2))
    position_by_root = {root: index for index, root in enumerate(powers)}
    sample_node_positions = {
        index for index, root in enumerate(powers) if 1 <= root <= 69
    }
    skip_points = frozenset(set(range(70)) | sample_node_positions)
    allowed_positions = sorted(set(range(phase.CODE_POSITIONS)) - skip_points)

    cases = []
    for seed, weight in ((0xA66060, 31), (0xA66061, 35)):
        rng = random.Random(seed)
        error_positions = rng.sample(allowed_positions, weight)
        errors = {
            powers[index]: rng.randrange(1, phase.FIELD_SIZE)
            for index in error_positions
        }
        samples = phase._syndrome_to_samples(errors, sample_quotients, mul)
        basis = fma.modular_basis(samples, list(range(70)), mul)
        row = min(range(2), key=lambda index: fma.row_rank(basis, index))
        denominator, numerator = basis[row]
        factor = inv(denominator[-1])
        denominator = [mul(value, factor) for value in denominator]
        numerator = [mul(value, factor) for value in numerator]
        locator = phase._error_locator(errors, mul)
        evaluator = phase._error_evaluator(locator, sample_node, errors, mul)
        if denominator != locator or numerator != evaluator:
            raise AssertionError("FMA pair does not match its sample-node evaluator")

        pair = bridge._padded_pair(numerator, denominator, weight, kappas, mul)
        masks = [rng.randrange(phase.FIELD_SIZE) for _ in range(phase.CODE_POSITIONS)]
        residual = bridge._residual_masks(masks, powers, mul)
        expected = sum(
            (value & residual[position_by_root[root]]).bit_count()
            for root, value in errors.items()
        ) & 1
        cases.append(
            {"pair": pair, "residual": residual, "expected": expected, "weight": weight}
        )

    builder = km.CircuitBuilder()
    numerator_words = [builder.alloc_qubits(phase.DEGREE) for _ in range(35)]
    denominator_words = [builder.alloc_qubits(phase.DEGREE) for _ in range(35)]
    mask_words = [builder.alloc_bits(phase.DEGREE) for _ in range(phase.CODE_POSITIONS)]
    scan(
        builder,
        numerator_words,
        denominator_words,
        mask_words,
        skip_points=skip_points,
        node_polynomial=sample_node,
    )
    circuit = builder.finish_circuit()

    simulator = km.Simulator(
        batch_size=len(cases), debug_print=False, counting_operations=True, seed=0
    )
    simulator.use_same_registers_as(circuit)
    for index, register in enumerate(numerator_words):
        simulator.write_across_shots(
            register, bit_columns([case["pair"][0][index] for case in cases])
        )
    for index, register in enumerate(denominator_words):
        simulator.write_across_shots(
            register, bit_columns([case["pair"][1][index] for case in cases])
        )

    mask_matrix = np.asarray([case["residual"] for case in cases], dtype=np.uint32).T
    mask_bits = np.stack(
        [((mask_matrix >> bit) & 1).astype(bool) for bit in range(phase.DEGREE)],
        axis=1,
    ).reshape(-1, len(cases))
    all_masks = km.array([bit for word in mask_words for bit in word])
    simulator.write_across_shots(all_masks, mask_bits)
    simulator.do(circuit)

    observed = simulator.read_phase_flipped_across_shots().astype(int).tolist()
    expected = [case["expected"] for case in cases]
    restore_errors = 0
    for index, register in enumerate(numerator_words):
        restore_errors += not np.array_equal(
            simulator.read_across_shots(register),
            bit_columns([case["pair"][0][index] for case in cases]),
        )
    for index, register in enumerate(denominator_words):
        restore_errors += not np.array_equal(
            simulator.read_across_shots(register),
            bit_columns([case["pair"][1][index] for case in cases]),
        )
    restore_errors += not np.array_equal(simulator.read_across_shots(all_masks), mask_bits)

    live = set().union(*(set(register) for register in numerator_words + denominator_words))
    scratch = [
        km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in live
    ]
    scratch_clean = not scratch or not np.any(
        simulator.read_across_shots(km.array(scratch))
    )
    phase_errors = sum(actual != wanted for actual, wanted in zip(observed, expected))

    source_path = Path(__file__)
    return {
        "date": "2026-11-24",
        "experiment": "exp-057-fma-native-node-scan",
        "status": "FAIL_PHASE" if phase_errors else "PASS_PHASE",
        "source": {
            "git_head_before_run": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "script": source_path.relative_to(ROOT).as_posix(),
            "script_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        },
        "method": {
            "weights": [case["weight"] for case in cases],
            "error_roots_excluded_at_sample_nodes": True,
            "sample_node_root_positions": len(sample_node_positions),
            "skipped_scan_positions": len(skip_points),
            "scanner_node_polynomial": "the GF(2^12) product over sample points 0 through 69",
        },
        "checks": {
            "expected_phase": expected,
            "observed_phase": observed,
            "phase_errors": phase_errors,
            "input_restore_errors": int(restore_errors),
            "clean_scratch_qubits": len(scratch),
            "scratch_clean": bool(scratch_clean),
        },
        "resources": {
            "compiled_qubits": circuit.num_qubits,
            "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
            "simulated_toffoli_like_gates": simulator.operation_statistics().num_toffoli_like,
        },
        "scope": "FMA-native-node scan only. The two cases exclude sample-node errors; the full FMA schedule, required sample-node phase, cleanup, and official verifier are omitted.",
        "decision": "Reject this direct scan shortcut because the phase screen fails.",
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
