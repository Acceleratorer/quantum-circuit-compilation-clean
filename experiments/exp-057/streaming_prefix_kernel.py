"""Private-kernel gate screen for the four-word FMA prefix state.

The gate arithmetic helper is the unchanged Apache-2.0 port documented in
src/dqi/NOTICE. Run this module only inside a private Kaggle kernel.
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import subprocess
import sys
from random import Random

import numpy as np


ARITHMETIC = None
FIELD_BITS = 12
RANK_TAG = 67
POINTS = (0, 1, 2, 3)


def load_gate_arithmetic():
    if not Path("/kaggle/working").is_dir():
        raise RuntimeError("Gate arithmetic may run only in a private Kaggle kernel")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "kickmix==1.0.0"],
        check=True,
    )
    km = importlib.import_module("kickmix.kickmix")
    sys.modules.setdefault("circ", km)
    if ARITHMETIC is None:
        raise RuntimeError("The private-kernel bundle did not embed field.py")
    return km, ARITHMETIC


def bit_columns(values, width):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack([((values >> bit) & 1).astype(np.bool_) for bit in range(width)])


def xor_constant(builder, register, value):
    for bit, qubit in enumerate(register):
        if value >> bit & 1:
            builder.x(qubit)


class QubitControlledBuilder:
    """Add one coherent qubit control to the field helper's X/CX/CCX gates."""

    def __init__(self, builder, control, and_scratch):
        self.base = builder
        self.control = control
        self.and_scratch = and_scratch

    def alloc_qubits(self, count):
        return self.base.alloc_qubits(count)

    def free(self, qubits):
        self.base.free(qubits)

    def x(self, target):
        self.base.cx(self.control, target)

    def cx(self, control, target):
        self.base.ccx(self.control, control, target)

    def ccx(self, left, right, target):
        scratch = self.and_scratch
        self.base.ccx(self.control, left, scratch)
        self.base.ccx(scratch, right, target)
        self.base.ccx(self.control, left, scratch)

    def init_and(self, left, right, target):
        self.ccx(left, right, target)

    def del_and(self, left, right, target):
        self.ccx(left, right, target)

    def swap(self, left, right):
        self.base.cx(left, right)
        self.cx(right, left)
        self.base.cx(left, right)


def apply_controlled(builder, control, when_one, operation):
    if not when_one:
        builder.x(control)
    and_scratch = builder.alloc_qubits(1)[0]
    operation(QubitControlledBuilder(builder, control, and_scratch))
    builder.free(and_scratch)
    if not when_one:
        builder.x(control)


def xor_zero_flag(builder, value, target):
    builder.x(value)
    ladder = builder.alloc_qubits(len(value) - 1)
    builder.init_and(value[0], value[1], ladder[0])
    for index in range(1, len(value) - 1):
        builder.init_and(ladder[index - 1], value[index + 1], ladder[index])
    builder.cx(ladder[-1], target)
    for index in reversed(range(1, len(value) - 1)):
        builder.del_and(ladder[index - 1], value[index + 1], ladder[index])
    builder.del_and(value[0], value[1], ladder[0])
    builder.x(value)
    builder.free(ladder)


def controlled_inverse_inplace(controlled, value, ar):
    """Replace one field word conditionally and erase the inverse scratch."""
    builder = controlled.base
    encoded_inverse = builder.alloc_qubits(FIELD_BITS)
    ar.inverse(builder, value, target=encoded_inverse)
    controlled.swap(value, encoded_inverse)

    # On either control branch, encoded_inverse equals inverse(value) after
    # the swap, so erase it directly without a second inverse output register.
    ar.erase_inverse(builder, value, encoded_inverse)
    builder.free(encoded_inverse)


def scale_inplace(builder, value, factor, inverse_factor, borrowed, ar):
    extra = builder.alloc_qubits(FIELD_BITS - len(borrowed))
    target = list(borrowed) + list(extra)
    ar.mul_xor0(builder, value, factor, target)
    builder.swap(value, target)
    ar.mul_xor0(builder, value, inverse_factor, target)
    builder.free(extra)


def divide_inplace(builder, numerator, denominator, borrowed, ar):
    reciprocal = builder.alloc_qubits(FIELD_BITS)
    ar.inverse(builder, denominator, target=reciprocal)
    scale_inplace(builder, numerator, reciprocal, denominator, borrowed, ar)
    ar.erase_inverse(builder, denominator, reciprocal)
    builder.free(reciprocal)


def toggle_delta0(builder, d0, d1, a1, target, ar, columns, inverse_columns):
    ar.linear_xor(builder, d1, target, columns[10])
    ar.linear_xor(builder, d0, target, columns[12])
    mix = builder.alloc_qubits(FIELD_BITS)
    ar.linear_xor(builder, d0, mix, columns[1])
    ar.linear_xor(builder, d1, mix, columns[1])
    ar.linear_inplace(builder, mix, columns[6])
    ar.mul_xor0(builder, mix, a1, target)
    ar.linear_inplace(builder, mix, inverse_columns[6])
    ar.linear_xor(builder, d0, mix, columns[1])
    ar.linear_xor(builder, d1, mix, columns[1])
    builder.free(mix)


def toggle_delta1(builder, d0, d1, a0, target, ar, columns, inverse_columns):
    ar.linear_xor(builder, d1, target, columns[12])
    mix = builder.alloc_qubits(FIELD_BITS)
    ar.linear_xor(builder, d0, mix, columns[1])
    ar.linear_xor(builder, d1, mix, columns[1])
    ar.linear_inplace(builder, mix, columns[6])
    ar.mul_xor0(builder, mix, a0, target)
    ar.linear_inplace(builder, mix, inverse_columns[6])
    ar.linear_xor(builder, d0, mix, columns[1])
    ar.linear_xor(builder, d1, mix, columns[1])
    builder.free(mix)


def toggle_pivot_zero(builder, d0, d1, d2, target, ar, columns):
    value = builder.alloc_qubits(FIELD_BITS)
    ar.linear_xor(builder, d2, value, columns[1])
    ar.linear_xor(builder, d1, value, columns[2])
    ar.linear_xor(builder, d0, value, columns[3])
    xor_zero_flag(builder, value, target)
    ar.linear_xor(builder, d2, value, columns[1])
    ar.linear_xor(builder, d1, value, columns[2])
    ar.linear_xor(builder, d0, value, columns[3])
    builder.free(value)


def build_decoder():
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot_one = builder.alloc_qubits(1)[0]
    words = [payload[index * FIELD_BITS : (index + 1) * FIELD_BITS] for index in range(4)]
    a0, a1, b0, b1 = words
    field = ar.field(FIELD_BITS)
    columns = {
        constant: [field.mul(constant, 1 << bit) for bit in range(FIELD_BITS)]
        for constant in (1, 2, 3, 4, 6, 10, 12)
    }
    inverse_columns = {constant: ar.inverse_columns(cols) for constant, cols in columns.items()}
    borrowed = list(rank)

    # The first-block rank/tag word is known at this point and is borrowed as
    # clean arithmetic space, then restored before the circuit returns.
    xor_constant(builder, rank, RANK_TAG)

    divide_inplace(builder, b0, a0, borrowed, ar)

    ar.mul_xor0(builder, b0, a0, b1)
    denominator1 = builder.alloc_qubits(FIELD_BITS)
    ar.linear_xor(builder, a0, denominator1, columns[1])
    ar.linear_xor(builder, a1, denominator1, columns[1])
    xor_constant(builder, denominator1, 1)
    divide_inplace(builder, b1, denominator1, borrowed, ar)
    ar.linear_xor(builder, a0, denominator1, columns[1])
    ar.linear_xor(builder, a1, denominator1, columns[1])
    xor_constant(builder, denominator1, 1)
    builder.free(denominator1)

    delta = builder.alloc_qubits(FIELD_BITS)
    toggle_delta0(builder, b0, b1, a1, delta, ar, columns, inverse_columns)
    xor_zero_flag(builder, delta, pivot_one)
    toggle_delta0(builder, b0, b1, a1, delta, ar, columns, inverse_columns)
    builder.free(delta)

    # Compute branch zero's factor before its update. Its in-place inverse uses
    # clean out-of-place inverse/erase operations around a controlled swap.
    determinant0 = builder.alloc_qubits(FIELD_BITS)
    inverse_determinant0 = builder.alloc_qubits(FIELD_BITS)
    toggle_delta0(
        builder, b0, b1, a1, determinant0, ar, columns, inverse_columns
    )
    ar.inverse(builder, determinant0, target=inverse_determinant0)

    def update_a0(controlled):
        ar.linear_xor(controlled, a1, a0, columns[2])
        xor_constant(controlled, a0, 4)
        controlled_inverse_inplace(controlled, a0, ar)
        scale_inplace(
            controlled, a0, determinant0, inverse_determinant0, borrowed, ar
        )
        ar.linear_xor(controlled, b1, a0, columns[2])
        ar.linear_xor(controlled, b0, a0, columns[3])

    apply_controlled(builder, pivot_one, False, update_a0)

    # Branch zero changes a0 but leaves the inputs to delta1 alone. Compute
    # delta1 only after branch zero has had a chance to run, then clean it before
    # any later operation changes its inputs.
    ar.erase_inverse(builder, determinant0, inverse_determinant0)
    toggle_delta0(
        builder, b0, b1, a1, determinant0, ar, columns, inverse_columns
    )
    builder.free(determinant0)
    builder.free(inverse_determinant0)

    determinant1 = builder.alloc_qubits(FIELD_BITS)
    inverse_scale1 = builder.alloc_qubits(FIELD_BITS)
    toggle_delta1(
        builder, b0, b1, a0, determinant1, ar, columns, inverse_columns
    )
    ar.linear_inplace(builder, determinant1, inverse_columns[2])
    ar.inverse(builder, determinant1, target=inverse_scale1)

    def update_a1(controlled):
        ar.linear_inplace(controlled, a1, columns[2])
        ar.linear_xor(controlled, a0, a1, columns[1])
        xor_constant(controlled, a1, 4)
        controlled_inverse_inplace(controlled, a1, ar)
        scale_inplace(
            controlled, a1, determinant1, inverse_scale1, borrowed, ar
        )
        ar.linear_xor(controlled, b1, a1, columns[1])

    apply_controlled(builder, pivot_one, True, update_a1)

    # Branch one changes a1 but leaves the inputs to delta1 alone.
    ar.erase_inverse(builder, determinant1, inverse_scale1)
    ar.linear_inplace(builder, determinant1, columns[2])
    toggle_delta1(
        builder, b0, b1, a0, determinant1, ar, columns, inverse_columns
    )
    builder.free(determinant1)
    builder.free(inverse_scale1)

    apply_controlled(builder, pivot_one, True, lambda controlled: controlled.swap(a0, a1))

    xor_constant(builder, rank, RANK_TAG)
    builder.swap(a0, b0)
    builder.swap(a1, b1)
    toggle_pivot_zero(builder, a0, a1, b0, pivot_one, ar, columns)

    circuit = builder.finish_circuit()
    return km, ar, circuit, {"payload": payload, "rank": rank, "pivot": pivot_one}


def sample_coefficients(field, rng):
    while True:
        a0, a1, b0 = (rng.randrange(1 << FIELD_BITS) for _ in range(3))
        b1 = rng.randrange(1, 1 << FIELD_BITS)

        def denominator(point):
            return field.mul(point, point) ^ field.mul(a1, point) ^ a0

        if any(denominator(point) == 0 for point in POINTS):
            continue
        root_b = field.mul(b0, field.invert(b1))
        if denominator(root_b) == 0:
            continue
        coefficients = (a0, a1, b0, b1)
        samples = tuple(
            field.mul(
                field.mul(b1, point) ^ b0,
                field.invert(denominator(point)),
            )
            for point in POINTS
        )
        d0, d1, d2, _ = samples
        c0 = d2 ^ field.mul(2, d1) ^ field.mul(3, d0)
        remaining = a1 if c0 else a0
        return coefficients, (d0, d1, d2, remaining), int(c0 == 0)


def generate_cases(field, count=32):
    rng = Random(0xA466057)
    cases = []
    pivot_one = None
    while len(cases) < count - 1 or pivot_one is None:
        case = sample_coefficients(field, rng)
        if case[2] and pivot_one is None:
            pivot_one = case
            continue
        if len(cases) < count - 1:
            cases.append(case)
    cases.append(pivot_one)
    return cases


def run_screen():
    km, ar, circuit, registers = build_decoder()
    field = ar.field(FIELD_BITS)
    cases = generate_cases(field)
    assert {case[2] for case in cases} == {0, 1}

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    inputs = np.asarray([case[0] for case in cases], dtype=np.uint32)
    expected = np.asarray([case[1] for case in cases], dtype=np.uint32)
    for word in range(4):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(inputs[:, word], FIELD_BITS),
        )
    rank_value = np.full(len(cases), RANK_TAG, dtype=np.uint32)
    sim.write_across_shots(registers["rank"], bit_columns(rank_value, 8))
    sim.write_across_shots(
        registers["pivot"], bit_columns([0] * len(cases), 1)[0]
    )
    sim.do(circuit)

    for word in range(4):
        actual = sim.read_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
        )
        assert np.array_equal(actual, bit_columns(expected[:, word], FIELD_BITS))
    assert not np.any(sim.read_across_shots(registers["payload"][4 * FIELD_BITS :]))
    assert np.array_equal(
        sim.read_across_shots(registers["rank"]), bit_columns(rank_value, 8)
    )
    assert not np.any(sim.read_across_shots(registers["pivot"]))

    live = set(registers["payload"]) | set(registers["rank"]) | {registers["pivot"]}
    scratch = [km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in live]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())
    return {
        "experiment": "exp-057-streaming-prefix-state",
        "shape": "G=1, deg(A)=2, deg(B)=1, gcd(A,B)=1",
        "cases": len(cases),
        "pivot_coverage": {"a0": sum(not case[2] for case in cases), "a1": sum(case[2] for case in cases)},
        "round_trip_errors": 0,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "In-place four-word coefficient-to-prefix-state map only; not an integrated 4+66 schedule.",
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
