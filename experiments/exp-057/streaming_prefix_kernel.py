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
import tempfile
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


def load_width_helpers(km):
    """Load the zero-aware inverse and pivoted inverse eraser."""
    sys.modules.setdefault("circ", km)
    local_root = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "dqi"
        / "pro_q2_897"
    )
    helper_root = (
        local_root
        if local_root.is_dir()
        else Path(tempfile.gettempdir()) / "exp057_helpers"
    )
    if not helper_root.is_dir():
        archive = globals().get("HELPER_ARCHIVE_B64")
        if archive is None:
            raise RuntimeError("Missing bundled DQI arithmetic helpers")
        import base64
        from io import BytesIO
        from zipfile import ZipFile

        helper_root.mkdir(parents=True, exist_ok=True)
        with ZipFile(BytesIO(base64.b64decode(archive))) as bundle:
            members = [Path(name) for name in bundle.namelist()]
            if any(path.is_absolute() or ".." in path.parts for path in members):
                raise RuntimeError("Invalid path in bundled DQI arithmetic helpers")
            bundle.extractall(helper_root)
    if not (helper_root / "exp").is_dir():
        raise RuntimeError(f"Missing bundled DQI arithmetic helpers: {helper_root}")
    if str(helper_root) not in sys.path:
        sys.path.insert(0, str(helper_root))
    arithmetic_root = helper_root / "exp" / "arithmetic"
    if str(arithmetic_root) not in sys.path:
        sys.path.insert(0, str(arithmetic_root))
    inverse_zero = importlib.import_module(
        "exp.inverse12_escape.zero1"
    ).inverse_zero
    phase_inverse36_zero = importlib.import_module(
        "exp.safe_scalar.phase"
    ).phase_inverse36_zero
    phase_inverse36_pivot = importlib.import_module(
        "exp.mul99.phase36"
    ).phase_inverse36_pivot
    return inverse_zero, phase_inverse36_zero, phase_inverse36_pivot


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


class BorrowedScratchBuilder:
    """Route temporary allocations through known-clean qubits first."""

    def __init__(self, builder, borrowed, km):
        self.base = builder
        self.array = km.array
        self.borrowed = set(borrowed)
        self.available = list(borrowed)
        self.in_use = set()

    def alloc_qubits(self, count):
        take = min(count, len(self.available))
        qubits = self.available[:take]
        del self.available[:take]
        self.in_use.update(qubits)
        if take < count:
            qubits.extend(list(self.base.alloc_qubits(count - take)))
        return self.array(qubits)

    def free(self, qubits):
        try:
            items = list(qubits)
        except TypeError:
            items = [qubits]
        owned = []
        for qubit in items:
            if qubit in self.borrowed:
                if qubit not in self.in_use:
                    raise RuntimeError(f"Invalid borrowed-qubit free: {qubit}")
                self.in_use.remove(qubit)
                self.available.append(qubit)
            else:
                owned.append(qubit)
        if owned:
            self.base.free(self.array(owned))

    def assert_released(self):
        if self.in_use:
            raise RuntimeError(f"Borrowed workspace leaked: {self.in_use}")

    def __getattr__(self, name):
        return getattr(self.base, name)


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


def controlled_inverse_inplace(
    controlled,
    value,
    borrowed,
    inverse_zero,
    phase_inverse36_zero,
    phase_inverse36_pivot,
    km,
):
    """Replace one field word and clean its inverse using borrowed zeros."""
    builder = controlled.base
    workspace = BorrowedScratchBuilder(
        builder, list(borrowed) + [controlled.and_scratch], km
    )
    encoded_inverse, zero_flag = inverse_zero(workspace, value)
    controlled.swap(value, encoded_inverse)
    mask = workspace.alloc_bits(FIELD_BITS)
    zero_mask = workspace.alloc_bits(1)
    workspace.hmr(encoded_inverse, mask)
    workspace.hmr(zero_flag, zero_mask[0])
    workspace.free(encoded_inverse)
    workspace.free(zero_flag)
    phase_inverse36_zero(workspace, value, mask, zero_mask[0])
    workspace.free(mask)
    workspace.free(zero_mask)
    workspace.assert_released()


def scale_inplace(builder, value, factor, inverse_factor, borrowed, ar):
    extra = builder.alloc_qubits(FIELD_BITS - len(borrowed))
    target = list(borrowed) + list(extra)
    ar.mul_xor0(builder, value, factor, target)
    builder.swap(value, target)
    ar.mul_xor0(builder, value, inverse_factor, target)
    builder.free(extra)


def divide_inplace(
    builder, numerator, denominator, borrowed, pivot, ar, phase_inverse36_pivot, km
):
    reciprocal = builder.alloc_qubits(FIELD_BITS)
    workspace = BorrowedScratchBuilder(builder, list(borrowed) + [pivot], km)
    ar.inverse(workspace, denominator, target=reciprocal)
    workspace.assert_released()
    scale_inplace(builder, numerator, reciprocal, denominator, borrowed, ar)
    mask = workspace.alloc_bits(FIELD_BITS)
    workspace.hmr(reciprocal, mask)
    phase_inverse36_pivot(workspace, denominator, mask)
    workspace.free(mask)
    workspace.assert_released()
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
    inverse_zero, phase_inverse36_zero, phase_inverse36_pivot = load_width_helpers(km)
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

    divide_inplace(
        builder, b0, a0, borrowed, pivot_one, ar, phase_inverse36_pivot, km
    )

    ar.mul_xor0(builder, b0, a0, b1)
    denominator1 = builder.alloc_qubits(FIELD_BITS)
    ar.linear_xor(builder, a0, denominator1, columns[1])
    ar.linear_xor(builder, a1, denominator1, columns[1])
    xor_constant(builder, denominator1, 1)
    divide_inplace(
        builder,
        b1,
        denominator1,
        borrowed,
        pivot_one,
        ar,
        phase_inverse36_pivot,
        km,
    )
    ar.linear_xor(builder, a0, denominator1, columns[1])
    ar.linear_xor(builder, a1, denominator1, columns[1])
    xor_constant(builder, denominator1, 1)
    builder.free(denominator1)

    delta = builder.alloc_qubits(FIELD_BITS)
    toggle_delta0(builder, b0, b1, a1, delta, ar, columns, inverse_columns)
    xor_zero_flag(builder, delta, pivot_one)
    toggle_delta0(builder, b0, b1, a1, delta, ar, columns, inverse_columns)
    builder.free(delta)

    # Invert a0 first; delta0 does not depend on a0, so its factors can be
    # allocated after the inverse cleanup's peak-width phase.
    def prepare_a0(controlled):
        ar.linear_xor(controlled, a1, a0, columns[2])
        xor_constant(controlled, a0, 4)
        controlled_inverse_inplace(
            controlled,
            a0,
            borrowed,
            inverse_zero,
            phase_inverse36_zero,
            phase_inverse36_pivot,
            km,
        )

    apply_controlled(builder, pivot_one, False, prepare_a0)

    determinant0 = builder.alloc_qubits(FIELD_BITS)
    inverse_determinant0 = builder.alloc_qubits(FIELD_BITS)
    toggle_delta0(
        builder, b0, b1, a1, determinant0, ar, columns, inverse_columns
    )
    determinant_workspace = BorrowedScratchBuilder(builder, borrowed, km)
    ar.inverse(determinant_workspace, determinant0, target=inverse_determinant0)
    determinant_workspace.assert_released()

    def finish_a0(controlled):
        scale_inplace(
            controlled, a0, determinant0, inverse_determinant0, borrowed, ar
        )
        ar.linear_xor(controlled, b1, a0, columns[2])
        ar.linear_xor(controlled, b0, a0, columns[3])

    apply_controlled(builder, pivot_one, False, finish_a0)

    # Branch zero changes a0 but leaves the inputs to delta1 alone. Compute
    # delta1 only after branch zero has had a chance to run, then clean it before
    # any later operation changes its inputs.
    determinant_workspace = BorrowedScratchBuilder(builder, borrowed, km)
    ar.erase_inverse(determinant_workspace, determinant0, inverse_determinant0)
    determinant_workspace.assert_released()
    toggle_delta0(
        builder, b0, b1, a1, determinant0, ar, columns, inverse_columns
    )
    builder.free(determinant0)
    builder.free(inverse_determinant0)

    def prepare_a1(controlled):
        ar.linear_inplace(controlled, a1, columns[2])
        ar.linear_xor(controlled, a0, a1, columns[1])
        xor_constant(controlled, a1, 4)
        controlled_inverse_inplace(
            controlled,
            a1,
            borrowed,
            inverse_zero,
            phase_inverse36_zero,
            phase_inverse36_pivot,
            km,
        )

    apply_controlled(builder, pivot_one, True, prepare_a1)

    determinant1 = builder.alloc_qubits(FIELD_BITS)
    inverse_scale1 = builder.alloc_qubits(FIELD_BITS)
    toggle_delta1(
        builder, b0, b1, a0, determinant1, ar, columns, inverse_columns
    )
    ar.linear_inplace(builder, determinant1, inverse_columns[2])
    determinant_workspace = BorrowedScratchBuilder(builder, borrowed, km)
    ar.inverse(determinant_workspace, determinant1, target=inverse_scale1)
    determinant_workspace.assert_released()

    def finish_a1(controlled):
        scale_inplace(
            controlled, a1, determinant1, inverse_scale1, borrowed, ar
        )
        ar.linear_xor(controlled, b1, a1, columns[1])

    apply_controlled(builder, pivot_one, True, finish_a1)

    # Branch one changes a1 but leaves the inputs to delta1 alone.
    determinant_workspace = BorrowedScratchBuilder(builder, borrowed, km)
    ar.erase_inverse(determinant_workspace, determinant1, inverse_scale1)
    determinant_workspace.assert_released()
    ar.linear_inplace(builder, determinant1, columns[2])
    toggle_delta1(
        builder, b0, b1, a0, determinant1, ar, columns, inverse_columns
    )
    builder.free(determinant1)
    builder.free(inverse_scale1)

    apply_controlled(
        builder,
        pivot_one,
        True,
        lambda controlled: controlled.swap(a0, a1),
    )

    xor_constant(builder, rank, RANK_TAG)
    builder.swap(a0, b0)
    builder.swap(a1, b1)
    toggle_pivot_zero(builder, a0, a1, b0, pivot_one, ar, columns)

    circuit = builder.finish_circuit()
    return km, ar, circuit, {"payload": payload, "rank": rank, "pivot": pivot_one}


def build_tail_matrix_action(km=None, ar=None):
    """Compute one tail pair from four precomputed matrix evaluations."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)
    outputs = builder.alloc_qubits(2 * FIELD_BITS)

    a, b, c, d, sample = [
        payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
        for index in range(5)
    ]
    first, second = outputs[:FIELD_BITS], outputs[FIELD_BITS:]
    identity = [1 << bit for bit in range(FIELD_BITS)]

    ar.mul_xor0(builder, a, sample, first)
    ar.linear_xor(builder, b, first, identity)
    ar.mul_xor0(builder, c, sample, second)
    ar.linear_xor(builder, d, second, identity)

    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "pivot": pivot[0],
        "outputs": outputs,
    }


def run_tail_matrix_action_screen(case_count=64, km=None, ar=None):
    """Measure the reversible, out-of-place matrix action for one tail symbol."""
    km, ar, circuit, registers = build_tail_matrix_action(km, ar)
    field = ar.field(FIELD_BITS)
    rng = Random(0xA466058)
    input_words = np.asarray(
        [
            [rng.randrange(1 << FIELD_BITS) for _ in range(70)]
            for _ in range(case_count)
        ],
        dtype=np.uint32,
    )
    determinants = []
    for shot in range(case_count):
        while True:
            matrix = [rng.randrange(1 << FIELD_BITS) for _ in range(4)]
            a, b, c, d = matrix
            determinant = field.mul(a, d) ^ field.mul(b, c)
            if determinant:
                break
        input_words[shot, :4] = matrix
        determinants.append(determinant)

    samples = input_words[:, 4].copy()
    expected = np.asarray(
        [
            (
                field.mul(int(input_words[shot, 0]), int(samples[shot]))
                ^ int(input_words[shot, 1]),
                field.mul(int(input_words[shot, 2]), int(samples[shot]))
                ^ int(input_words[shot, 3]),
            )
            for shot in range(case_count)
        ],
        dtype=np.uint32,
    )
    rank_values = np.asarray(
        [rng.randrange(1 << 8) for _ in range(case_count)], dtype=np.uint32
    )
    pivot_values = np.asarray(
        [rng.randrange(2) for _ in range(case_count)], dtype=np.uint32
    )

    sim = km.Simulator(batch_size=case_count, debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    for word in range(70):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(input_words[:, word], FIELD_BITS),
        )
    sim.write_across_shots(registers["rank"], bit_columns(rank_values, 8))
    sim.write_across_shots(registers["pivot"], bit_columns(pivot_values, 1)[0])
    sim.do(circuit)

    actual = np.stack(
        [
            sim.read_across_shots(
                registers["outputs"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(2)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_bits = np.stack(
        [bit_columns(expected[:, index], FIELD_BITS).T for index in range(2)],
        axis=1,
    )
    assert np.array_equal(actual, expected_bits)

    for word in range(70):
        actual_word = sim.read_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
        )
        assert np.array_equal(actual_word, bit_columns(input_words[:, word], FIELD_BITS))
    assert np.array_equal(
        sim.read_across_shots(registers["rank"]), bit_columns(rank_values, 8)
    )
    assert np.array_equal(
        sim.read_across_shots(registers["pivot"]), bit_columns(pivot_values, 1)[0]
    )

    live = (
        set(registers["payload"])
        | set(registers["rank"])
        | {registers["pivot"]}
        | set(registers["outputs"])
    )
    scratch = [km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in live]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())
    return {
        "cases": case_count,
        "invertible_matrices": len(determinants),
        "zero_determinants": 0,
        "output_errors": 0,
        "preserved_payload_words": 70,
        "preserved_rank_and_pivot": True,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "Out-of-place one-symbol action with precomputed matrix entries; matrix generation and 66-symbol integration are not included.",
    }


def build_bezout_tail_action(km=None, ar=None, point=4):
    """Generate the Bezout tail action from a quadratic/linear row."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)
    outputs = builder.alloc_qubits(2 * FIELD_BITS)
    xor_constant(builder, rank, RANK_TAG)
    scratch_pool = builder.alloc_qubits(16)
    borrowed = list(rank) + [pivot[0]] + list(scratch_pool)
    workspace = BorrowedScratchBuilder(builder, borrowed, km)

    a0, a1, b0, b1, sample = [
        payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
        for index in range(5)
    ]
    first, second = outputs[:FIELD_BITS], outputs[FIELD_BITS:]
    field = ar.field(FIELD_BITS)
    identity = [1 << bit for bit in range(FIELD_BITS)]
    square = [field.mul(value, value) for value in identity]
    point_columns = [field.mul(point, value) for value in identity]
    first, second = outputs[:FIELD_BITS], outputs[FIELD_BITS:]

    # D = a0*b1^2 + a1*b0*b1 + b0^2 is nonzero for a coprime row.
    b1_square = workspace.alloc_qubits(FIELD_BITS)
    ar.linear_xor(workspace, b1, b1_square, square)
    b0b1 = workspace.alloc_qubits(FIELD_BITS)
    ar.mul_xor0(workspace, b0, b1, b0b1)
    ar.mul_xor0(workspace, a0, b1_square, first)
    ar.mul_xor0(workspace, a1, b0b1, first)
    ar.linear_xor(workspace, b0, first, square)
    ar.mul_xor0(workspace, b0, b1, b0b1)
    workspace.free(b0b1)
    ar.linear_xor(workspace, b1, b1_square, square)
    workspace.free(b1_square)
    _, _, phase_inverse36_pivot = load_width_helpers(km)
    ar.inverse(workspace, first, target=second)

    def toggle_quotient_numerator(target):
        ar.mul_xor0(workspace, a1, b1, target)
        ar.linear_xor(workspace, b1, target, point_columns)
        ar.linear_xor(workspace, b0, target, identity)

    quotient_numerator = workspace.alloc_qubits(FIELD_BITS)
    toggle_quotient_numerator(quotient_numerator)
    high_numerator = workspace.alloc_qubits(FIELD_BITS)
    ar.mul_xor0(workspace, quotient_numerator, sample, high_numerator)
    ar.linear_xor(workspace, b1, high_numerator, square)
    toggle_quotient_numerator(quotient_numerator)
    workspace.free(quotient_numerator)

    node_value = 1
    for prefix_point in POINTS:
        node_value = field.mul(node_value, point ^ prefix_point)
    node_columns = [field.mul(node_value, value) for value in identity]
    product_target = workspace.alloc_qubits(FIELD_BITS)
    ar.mul_xor0(workspace, high_numerator, second, product_target)
    workspace.swap(high_numerator, product_target)
    ar.mul_xor0(workspace, high_numerator, first, product_target)
    workspace.free(product_target)
    ar.linear_inplace(builder, high_numerator, node_columns)

    mask = workspace.alloc_bits(FIELD_BITS)
    workspace.hmr(second, mask)
    phase_inverse36_pivot(workspace, first, mask)
    workspace.free(mask)
    builder.swap(second, high_numerator)
    workspace.free(high_numerator)

    b1_square = workspace.alloc_qubits(FIELD_BITS)
    ar.linear_xor(workspace, b1, b1_square, square)
    b0b1 = workspace.alloc_qubits(FIELD_BITS)
    ar.mul_xor0(workspace, b0, b1, b0b1)
    ar.linear_xor(workspace, b0, first, square)
    ar.mul_xor0(workspace, a1, b0b1, first)
    ar.mul_xor0(workspace, a0, b1_square, first)
    ar.mul_xor0(workspace, b0, b1, b0b1)
    ar.linear_xor(workspace, b1, b1_square, square)
    workspace.free(b0b1)
    workspace.free(b1_square)

    low_denominator = workspace.alloc_qubits(FIELD_BITS)
    ar.linear_xor(workspace, a1, low_denominator, point_columns)
    ar.linear_xor(workspace, a0, low_denominator, identity)
    xor_constant(builder, low_denominator, field.mul(point, point))
    ar.linear_xor(workspace, b1, first, point_columns)
    ar.linear_xor(workspace, b0, first, identity)
    ar.mul_xor0(workspace, low_denominator, sample, first)
    xor_constant(builder, low_denominator, field.mul(point, point))
    ar.linear_xor(workspace, a0, low_denominator, identity)
    ar.linear_xor(workspace, a1, low_denominator, point_columns)
    workspace.free(low_denominator)

    workspace.assert_released()
    xor_constant(builder, rank, RANK_TAG)

    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "pivot": pivot[0],
        "outputs": outputs,
    }


def run_bezout_tail_action_screen(case_count=64, point=4, km=None, ar=None):
    """Measure one tail action whose entries are generated from the FMA row."""
    km, ar, circuit, registers = build_bezout_tail_action(km, ar, point)
    field = ar.field(FIELD_BITS)
    rng = Random(0xA466059)
    input_words = np.asarray(
        [
            [rng.randrange(1 << FIELD_BITS) for _ in range(70)]
            for _ in range(case_count)
        ],
        dtype=np.uint32,
    )
    expected = np.zeros((case_count, 2), dtype=np.uint32)
    for shot in range(case_count):
        coefficients, _, _ = sample_coefficients(field, rng)
        a0, a1, b0, b1 = coefficients
        input_words[shot, :4] = coefficients
        sample = int(input_words[shot, 4])
        inverse_b1 = field.invert(b1)
        q0 = field.mul(inverse_b1, a1 ^ field.mul(inverse_b1, b0))
        gcd = a0 ^ field.mul(q0, b0)
        assert gcd
        inverse_gcd = field.invert(gcd)
        w = field.mul(point, point) ^ field.mul(a1, point) ^ a0
        n = field.mul(b1, point) ^ b0
        p = 1
        for prefix_point in POINTS:
            p = field.mul(p, point ^ prefix_point)
        scale = field.mul(p, inverse_gcd)
        q_at_point = q0 ^ field.mul(inverse_b1, point)
        expected[shot, 0] = field.mul(w, sample) ^ n
        expected[shot, 1] = field.mul(
            scale, field.mul(q_at_point, sample) ^ 1
        )

    rank_values = np.full(case_count, RANK_TAG, dtype=np.uint32)
    pivot_values = np.zeros(case_count, dtype=np.uint32)
    sim = km.Simulator(batch_size=case_count, debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    for word in range(70):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(input_words[:, word], FIELD_BITS),
        )
    sim.write_across_shots(registers["rank"], bit_columns(rank_values, 8))
    sim.write_across_shots(registers["pivot"], bit_columns(pivot_values, 1)[0])
    sim.do(circuit)

    actual = np.stack(
        [
            sim.read_across_shots(
                registers["outputs"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(2)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_bits = np.stack(
        [bit_columns(expected[:, index], FIELD_BITS).T for index in range(2)],
        axis=1,
    )
    assert np.array_equal(actual, expected_bits)
    for word in range(70):
        actual_word = sim.read_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
        )
        assert np.array_equal(actual_word, bit_columns(input_words[:, word], FIELD_BITS))
    assert np.array_equal(
        sim.read_across_shots(registers["rank"]), bit_columns(rank_values, 8)
    )
    assert np.array_equal(
        sim.read_across_shots(registers["pivot"]), bit_columns(pivot_values, 1)[0]
    )
    live = (
        set(registers["payload"])
        | set(registers["rank"])
        | {registers["pivot"]}
        | set(registers["outputs"])
    )
    scratch = [km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in live]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())
    return {
        "cases": case_count,
        "point": point,
        "output_errors": 0,
        "preserved_payload_words": 70,
        "preserved_rank_and_pivot": True,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "One tail action from four polynomial coefficients; it does not accept the compact prefix state or implement a 66-symbol schedule.",
    }


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


def sample_zero_a1_case(field, rng):
    while True:
        a0 = rng.randrange(1 << FIELD_BITS)
        a1 = 0
        b0 = rng.randrange(1 << FIELD_BITS)
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
        if c0 == 0:
            continue
        return coefficients, (d0, d1, d2, a1), 0


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
    cases[0] = sample_zero_a1_case(field, Random(0xA466058))
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
    spectator_rng = Random(0xA466066)
    spectators = np.asarray(
        [
            [spectator_rng.randrange(1 << FIELD_BITS) for _ in range(66)]
            for _ in cases
        ],
        dtype=np.uint32,
    )
    for word in range(4):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(inputs[:, word], FIELD_BITS),
        )
    for word in range(66):
        offset = (word + 4) * FIELD_BITS
        sim.write_across_shots(
            registers["payload"][offset : offset + FIELD_BITS],
            bit_columns(spectators[:, word], FIELD_BITS),
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
    for word in range(66):
        offset = (word + 4) * FIELD_BITS
        actual = sim.read_across_shots(
            registers["payload"][offset : offset + FIELD_BITS]
        )
        assert np.array_equal(actual, bit_columns(spectators[:, word], FIELD_BITS))
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
        "preserved_spectator_words": 66,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "In-place four-word coefficient-to-prefix-state map only; not an integrated 4+66 schedule.",
        "tail_matrix_action": run_tail_matrix_action_screen(km=km, ar=ar),
        "tail_matrix_from_coefficients": run_bezout_tail_action_screen(km=km, ar=ar),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
