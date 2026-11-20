"""Compile a private-kernel screen for one four-point factorized-state shape.

The gate arithmetic helper is the unchanged Apache-2.0 port documented in
src/dqi/NOTICE. Run this screen only in a private Kaggle kernel.
"""

from __future__ import annotations

import importlib.util
import json
from functools import reduce
import os
from pathlib import Path
import subprocess
import sys
from random import Random

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FIELD_OVERRIDE = os.environ.get("EXP053_FIELD_PATH")
ARITHMETIC = Path(FIELD_OVERRIDE) if FIELD_OVERRIDE else Path(__file__).with_name("field.py")
if not ARITHMETIC.exists() and not FIELD_OVERRIDE:
    ARITHMETIC = (
        ROOT / "src" / "dqi" / "pro_q2_897" / "exp" / "arithmetic" / "field.py"
    )


def load_gate_arithmetic():
    if not Path("/kaggle/working").is_dir():
        raise RuntimeError("Ported gate arithmetic may run only in a private Kaggle kernel")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "kickmix==1.0.0"],
        check=True,
    )
    import kickmix as km

    sys.modules.setdefault("circ", km)
    spec = importlib.util.spec_from_file_location("dqi_shape_gate_arithmetic", ARITHMETIC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return km, module


def bit_columns(values, width):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack([((values >> bit) & 1).astype(np.bool_) for bit in range(width)])


def toggle_constant(builder, register, value):
    for bit, qubit in enumerate(register):
        if value >> bit & 1:
            builder.x(qubit)


def build_decoder():
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(840)
    rank = builder.alloc_qubits(8)
    branch = builder.alloc_qubits(1)
    outputs = builder.alloc_qubits(48)
    a0, a1, b0, b1 = (payload[index * 12 : (index + 1) * 12] for index in range(4))
    identity = [1 << bit for bit in range(12)]
    field = ar.field(12)

    for index, point in enumerate(range(4)):
        denominator = builder.alloc_qubits(12)
        numerator = builder.alloc_qubits(12)
        point_columns = [field.mul(point, 1 << bit) for bit in range(12)]
        ar.linear_xor(builder, a0, denominator, identity)
        ar.linear_xor(builder, a1, denominator, point_columns)
        toggle_constant(builder, denominator, field.mul(point, point))
        ar.linear_xor(builder, b0, numerator, identity)
        ar.linear_xor(builder, b1, numerator, point_columns)

        reciprocal = ar.inverse(builder, denominator)
        ar.mul_xor0(builder, numerator, reciprocal, outputs[index * 12 : (index + 1) * 12])
        ar.erase_inverse(builder, denominator, reciprocal)
        builder.free(reciprocal)

        ar.linear_xor(builder, b1, numerator, point_columns)
        ar.linear_xor(builder, b0, numerator, identity)
        ar.linear_xor(builder, a1, denominator, point_columns)
        ar.linear_xor(builder, a0, denominator, identity)
        toggle_constant(builder, denominator, field.mul(point, point))
        builder.free(list(numerator) + list(denominator))

    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "branch": branch,
        "outputs": outputs,
    }


def run_screen():
    km, ar, circuit, regs = build_decoder()
    field = ar.field(12)
    rng = Random(0x4D5156)
    # A(X)=X^2+X+c is irreducible when Tr(c)=1, so gcd(A,B)=1
    # for every nonzero linear B and all four public evaluation denominators.
    trace_one = next(
        value
        for value in range(1, 1 << 12)
        if reduce(
            int.__xor__, (field.frobenius(value, power) for power in range(12)), 0
        )
        == 1
    )
    a0, a1 = trace_one, 1
    cases = []
    for _ in range(32):
        b0 = rng.randrange(1 << 12)
        b1 = rng.randrange(1, 1 << 12)
        samples = []
        for point in range(4):
            denominator = field.mul(point, point) ^ field.mul(a1, point) ^ a0
            numerator = field.mul(b1, point) ^ b0
            samples.append(field.mul(numerator, field.pow(denominator, (1 << 12) - 2)))
        cases.append((b0, b1, tuple(samples)))

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    # Each shot has four words; the first two are fixed across the batch.
    coefficient_words = np.array(
        [[a0, a1, case[0], case[1]] for case in cases], dtype=np.uint32
    )
    for word in range(4):
        sim.write_across_shots(
            regs["payload"][word * 12 : (word + 1) * 12],
            bit_columns(coefficient_words[:, word], 12),
        )
    shape_id = 8  # catalog entry (deg G, deg A, deg B) = (0, 2, 1)
    packed_rank = (shape_id << 3) | 3
    sim.write_across_shots(regs["rank"], bit_columns([packed_rank] * len(cases), 8))
    sim.write_across_shots(regs["branch"], bit_columns([0] * len(cases), 1))
    sim.do(circuit)

    expected = np.asarray([case[2] for case in cases], dtype=np.uint32)
    actual = np.stack(
        [
            sim.read_across_shots(regs["outputs"][index * 12 : (index + 1) * 12])
            for index in range(4)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_bits = np.stack(
        [bit_columns(expected[:, index], 12).T for index in range(4)], axis=1
    )
    assert np.array_equal(actual, expected_bits)

    for word, values in enumerate(
        [coefficient_words[:, index] for index in range(4)]
    ):
        assert np.array_equal(
            sim.read_across_shots(regs["payload"][word * 12 : (word + 1) * 12]),
            bit_columns(values, 12),
        )
    for word in range(4, 70):
        assert not np.any(sim.read_across_shots(regs["payload"][word * 12 : (word + 1) * 12]))
    assert np.array_equal(
        sim.read_across_shots(regs["rank"]),
        bit_columns([packed_rank] * len(cases), 8),
    )
    assert not np.any(sim.read_across_shots(regs["branch"]))
    assert not np.any(sim.read_phase_flipped_across_shots())

    live_outputs = set(regs["payload"] + regs["rank"] + regs["branch"] + regs["outputs"])
    scratch = [km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in live_outputs]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    return {
        "shape": {"gcd_degree": 0, "cofactor_a_degree": 2, "cofactor_b_degree": 1},
        "cases": len(cases),
        "round_trip_errors": 0,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_limit": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "Out-of-place fixed-shape sample decoder only; not a full 4+66 schedule.",
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
