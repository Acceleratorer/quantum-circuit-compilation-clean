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


def apply_controlled(builder, control, when_one, operation, and_scratch=None):
    if not when_one:
        builder.x(control)
    owns_scratch = and_scratch is None
    if owns_scratch:
        and_scratch = builder.alloc_qubits(1)[0]
    operation(QubitControlledBuilder(builder, control, and_scratch))
    if owns_scratch:
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


def controlled_divide_inplace(
    builder,
    numerator,
    denominator,
    borrowed,
    control,
    when_one,
    ar,
    phase_inverse36_pivot,
    km,
):
    """Conditionally divide by a denominator that is nonzero in both branches."""
    reciprocal = builder.alloc_qubits(FIELD_BITS)
    extra = builder.alloc_qubits(FIELD_BITS - len(borrowed))
    workspace = BorrowedScratchBuilder(builder, list(borrowed) + list(extra), km)
    ar.inverse(workspace, denominator, target=reciprocal)
    workspace.assert_released()
    apply_controlled(
        builder,
        control,
        when_one,
        lambda controlled: scale_inplace(
            controlled, numerator, reciprocal, denominator, list(borrowed) + list(extra), ar
        ),
    )
    mask = workspace.alloc_bits(FIELD_BITS)
    workspace.hmr(reciprocal, mask)
    phase_inverse36_pivot(workspace, denominator, mask)
    workspace.free(mask)
    workspace.assert_released()
    builder.free(reciprocal)
    builder.free(extra)


def prefix_to_coefficients_inplace(
    builder, words, rank, pivot, ar, phase_inverse36_pivot, km
):
    """Decode (d0,d1,d2,remaining) into (a0,a1,b0,b1) in place."""
    d0, d1, d2, remaining = words
    field = ar.field(FIELD_BITS)
    identity = [1 << bit for bit in range(FIELD_BITS)]
    columns = {
        constant: [field.mul(constant, value) for value in identity]
        for constant in (1, 2, 3, 6)
    }
    two_thirds = field.mul(2, field.invert(3))
    two_thirds_columns = [field.mul(two_thirds, value) for value in identity]
    borrowed = list(rank)
    xor_constant(builder, rank, RANK_TAG)

    # Form c0 = 3*d0 + 2*d1 + d2, c1 = 2*(d1+d2), and
    # K = 2*d1 + 4*d2 so K = c0*a0 + c1*a1.
    ar.linear_xor(builder, d2, d1, identity)
    ar.linear_xor(builder, d2, d0, identity)
    ar.linear_inplace(builder, d2, columns[6])
    ar.linear_xor(builder, d1, d2, columns[2])
    ar.linear_xor(builder, d1, d0, two_thirds_columns)
    ar.linear_inplace(builder, d1, columns[2])
    ar.linear_inplace(builder, d0, columns[3])

    xor_zero_flag(builder, d0, pivot)

    # Pivot zero means c0 != 0; pivot one means c0 == 0 and c1 != 0.
    apply_controlled(builder, pivot, True, lambda controlled: xor_constant(controlled, d0, 1))
    apply_controlled(
        builder,
        pivot,
        False,
        lambda controlled: ar.mul_xor0(controlled, d1, remaining, d2),
    )
    controlled_divide_inplace(
        builder,
        d2,
        d0,
        borrowed,
        pivot,
        False,
        ar,
        phase_inverse36_pivot,
        km,
    )
    apply_controlled(builder, pivot, True, lambda controlled: xor_constant(controlled, d0, 1))

    apply_controlled(builder, pivot, False, lambda controlled: xor_constant(controlled, d1, 1))
    controlled_divide_inplace(
        builder,
        d2,
        d1,
        borrowed,
        pivot,
        True,
        ar,
        phase_inverse36_pivot,
        km,
    )
    apply_controlled(builder, pivot, False, lambda controlled: xor_constant(controlled, d1, 1))
    apply_controlled(builder, pivot, True, lambda controlled: controlled.swap(d2, remaining))

    xor_zero_flag(builder, d0, pivot)
    xor_constant(builder, rank, RANK_TAG)
    tail_b_pair_map_inplace_factored(
        builder, words, rank, pivot, ar, phase_inverse36_pivot, km
    )


def tail_b_pair_map_inplace(
    builder, words, rank, pivot, ar, phase_inverse36_pivot, km
):
    """Map the two prefix invariants to (b0,b1) with an invertible 2x2 map."""
    c0, c1, a0, a1 = words
    field = ar.field(FIELD_BITS)
    identity = [1 << bit for bit in range(FIELD_BITS)]
    constants = {
        value: [field.mul(value, bit) for bit in identity]
        for value in (1, 2, 3, 4, 6)
    }
    inverse_six = field.invert(6)
    inverse_six_columns = [field.mul(inverse_six, bit) for bit in identity]
    inverse_three_columns = [
        field.mul(field.invert(3), bit) for bit in identity
    ]
    xor_constant(builder, rank, RANK_TAG)


    first = builder.alloc_qubits(FIELD_BITS)
    temp = builder.alloc_qubits(FIELD_BITS)

    def xor_p(target, scratch, gate_builder=builder):
        ar.linear_xor(gate_builder, a0, scratch, identity)
        xor_constant(gate_builder, scratch, 2)
        ar.mul_xor0(gate_builder, a0, scratch, target)
        ar.linear_inplace(gate_builder, target, inverse_six_columns)
        ar.linear_xor(gate_builder, a0, scratch, identity)
        xor_constant(gate_builder, scratch, 2)

    def xor_q(target, scratch, gate_builder=builder):
        ar.linear_xor(gate_builder, a1, scratch, identity)
        xor_constant(gate_builder, scratch, 3)
        ar.mul_xor0(gate_builder, a0, scratch, target)
        ar.linear_inplace(gate_builder, target, inverse_six_columns)
        ar.linear_xor(gate_builder, a1, scratch, identity)
        xor_constant(gate_builder, scratch, 3)

    def unxor_p(target, scratch, gate_builder=builder):
        ar.linear_xor(gate_builder, a0, scratch, identity)
        xor_constant(gate_builder, scratch, 2)
        ar.linear_inplace(gate_builder, target, constants[6])
        ar.mul_xor0(gate_builder, a0, scratch, target)
        ar.linear_xor(gate_builder, a0, scratch, identity)
        xor_constant(gate_builder, scratch, 2)

    def unxor_q(target, scratch, gate_builder=builder):
        ar.linear_xor(gate_builder, a1, scratch, identity)
        xor_constant(gate_builder, scratch, 3)
        ar.linear_inplace(gate_builder, target, constants[6])
        ar.mul_xor0(gate_builder, a0, scratch, target)
        ar.linear_xor(gate_builder, a1, scratch, identity)
        xor_constant(gate_builder, scratch, 3)

    xor_p(first, temp)
    xor_zero_flag(builder, first, pivot)
    builder.cx(pivot, rank[0])
    builder.cx(rank[0], pivot)
    control = rank[0]

    second = builder.alloc_qubits(FIELD_BITS)
    apply_controlled(
        builder,
        control,
        True,
        lambda controlled: xor_q(second, temp, controlled),
        and_scratch=pivot,
    )
    apply_controlled(
        builder,
        control,
        True,
        lambda controlled: controlled.swap(first, second),
        and_scratch=pivot,
    )
    apply_controlled(
        builder,
        control,
        True,
        lambda controlled: controlled.swap(c0, c1),
        and_scratch=pivot,
    )

    inverse_borrowed = list(rank[1:]) + [pivot] + list(second)
    inverse_workspace = BorrowedScratchBuilder(builder, inverse_borrowed, km)

    def erase_inverse(workspace, value, inverse):
        mask = workspace.alloc_bits(FIELD_BITS)
        workspace.hmr(inverse, mask)
        phase_inverse36_pivot(workspace, value, mask)
        workspace.free(mask)
        workspace.assert_released()

    def divide_first_by_second_using_clean_temp():
        inverse_workspace = BorrowedScratchBuilder(
            builder, borrowed + list(temp), km
        )
        inverse = ar.inverse(inverse_workspace, second)
        scale_scratch = list(inverse_workspace.available)
        assert len(scale_scratch) >= FIELD_BITS
        scale_inplace(
            builder, first, inverse, second, scale_scratch[:FIELD_BITS], ar
        )
        return inverse_workspace, inverse, scale_scratch[:FIELD_BITS]

    def erase_borrowed_inverse(workspace, value, inverse):
        mask = workspace.alloc_bits(FIELD_BITS)
        workspace.hmr(inverse, mask)
        phase_inverse36_pivot(workspace, value, mask)
        workspace.free(mask)
        workspace.free(inverse)
        workspace.assert_released()

    ar.inverse(inverse_workspace, first, target=temp)
    inverse_workspace.assert_released()
    scale_borrowed = list(rank[1:]) + [pivot] + list(second[: FIELD_BITS - 8])
    scale_inplace(builder, c0, first, temp, scale_borrowed, ar)
    erase_inverse(inverse_workspace, first, temp)

    apply_controlled(
        builder,
        control,
        False,
        lambda controlled: xor_q(second, temp, controlled),
        and_scratch=pivot,
    )
    ar.mul_xor0(builder, c1, second, c0)
    apply_controlled(
        builder,
        control,
        False,
        lambda controlled: unxor_q(second, temp, controlled),
        and_scratch=pivot,
    )
    apply_controlled(
        builder,
        control,
        True,
        lambda controlled: unxor_q(first, temp, controlled),
        and_scratch=pivot,
    )
    apply_controlled(
        builder,
        control,
        False,
        lambda controlled: unxor_p(first, temp, controlled),
        and_scratch=pivot,
    )

    borrowed_base = list(rank[1:]) + [pivot]

    def xor_det_over_p_numerator_direct():
        def add_q(controlled):
            ar.linear_xor(controlled, a1, second, identity)
            xor_constant(controlled, second, 3)
            ar.mul_xor0(controlled, a0, second, first)
            ar.linear_inplace(controlled, first, inverse_six_columns)
            ar.linear_xor(controlled, a1, second, identity)
            xor_constant(controlled, second, 3)

        def add_a1a2_over_six(controlled):
            ar.linear_xor(controlled, a1, a0, identity)
            ar.linear_inplace(controlled, a1, constants[3])
            ar.linear_xor(controlled, a0, a1, identity)
            xor_constant(controlled, a0, 1)
            xor_constant(controlled, a1, 4)
            ar.mul_xor0(controlled, a0, a1, first)
            ar.linear_inplace(controlled, first, inverse_six_columns)
            xor_constant(controlled, a1, 4)
            xor_constant(controlled, a0, 1)
            ar.linear_xor(controlled, a0, a1, identity)
            ar.linear_inplace(controlled, a1, inverse_three_columns)
            ar.linear_xor(controlled, a1, a0, identity)

        apply_controlled(builder, control, True, add_q, and_scratch=pivot)
        apply_controlled(
            builder, control, False, add_a1a2_over_six, and_scratch=pivot
        )

    def unxor_det_over_p_numerator():
        def erase_q(controlled):
            ar.linear_xor(controlled, a1, temp, identity)
            xor_constant(controlled, temp, 3)
            ar.linear_inplace(controlled, first, constants[6])
            ar.mul_xor0(controlled, a0, temp, first)
            ar.linear_xor(controlled, a1, temp, identity)
            xor_constant(controlled, temp, 3)

        def erase_a1a2_over_six(controlled):
            ar.linear_xor(controlled, a0, second, identity)
            ar.linear_xor(controlled, a1, second, identity)
            xor_constant(controlled, second, 1)
            ar.linear_xor(controlled, a0, temp, identity)
            ar.linear_xor(controlled, a1, temp, constants[2])
            xor_constant(controlled, temp, 4)
            ar.linear_inplace(controlled, first, constants[6])
            ar.mul_xor0(controlled, second, temp, first)
            ar.linear_xor(controlled, a0, temp, identity)
            ar.linear_xor(controlled, a1, temp, constants[2])
            xor_constant(controlled, temp, 4)
            ar.linear_xor(controlled, a0, second, identity)
            ar.linear_xor(controlled, a1, second, identity)
            xor_constant(controlled, second, 1)

        apply_controlled(builder, control, True, erase_q, and_scratch=pivot)
        apply_controlled(
            builder, control, False, erase_a1a2_over_six, and_scratch=pivot
        )

    def xor_det_over_p_denominator():
        ar.linear_xor(builder, a0, second, identity)
        xor_constant(builder, second, 2)
        apply_controlled(
            builder,
            control,
            True,
            lambda controlled: xor_constant(controlled, second, 1),
            and_scratch=pivot,
        )

    xor_det_over_p_denominator()
    det_workspace = BorrowedScratchBuilder(
        builder, borrowed_base + list(first), km
    )
    ar.inverse(det_workspace, second, target=temp)
    det_workspace.assert_released()
    xor_det_over_p_denominator()
    xor_det_over_p_numerator_direct()
    extra = builder.alloc_qubits(FIELD_BITS - len(borrowed_base))
    borrowed = borrowed_base + list(extra)
    workspace = BorrowedScratchBuilder(builder, borrowed, km)
    xor_det_over_p_denominator()
    scale_inplace(builder, first, temp, second, borrowed, ar)
    xor_det_over_p_denominator()
    inverse_t_workspace = BorrowedScratchBuilder(
        builder, borrowed + list(second), km
    )
    inverse_t = ar.inverse(inverse_t_workspace, first)
    scale_inplace(
        builder, c1, first, inverse_t, inverse_t_workspace.available, ar
    )
    inverse_t_mask = inverse_t_workspace.alloc_bits(FIELD_BITS)
    inverse_t_workspace.hmr(inverse_t, inverse_t_mask)
    inverse_t_workspace.free(inverse_t)
    phase_inverse36_pivot(inverse_t_workspace, first, inverse_t_mask)
    inverse_t_workspace.free(inverse_t_mask)
    inverse_t_workspace.assert_released()

    xor_det_over_p_denominator()
    scale_inplace(builder, first, second, temp, borrowed, ar)
    erase_inverse(workspace, second, temp)
    xor_det_over_p_denominator()
    unxor_det_over_p_numerator()

    def xor_row_ratio_numerator():
        ar.linear_xor(builder, a1, first, identity)
        xor_constant(builder, first, 3)
        apply_controlled(
            builder,
            control,
            True,
            lambda controlled: xor_constant(controlled, first, 3),
            and_scratch=pivot,
        )

    def xor_row_ratio_denominator():
        ar.linear_xor(builder, a0, second, identity)
        xor_constant(builder, second, 2)
        apply_controlled(
            builder,
            control,
            True,
            lambda controlled: xor_constant(controlled, second, 2),
            and_scratch=pivot,
        )

    xor_row_ratio_numerator()
    xor_row_ratio_denominator()
    ratio_workspace, ratio_inverse, ratio_scratch = (
        divide_first_by_second_using_clean_temp()
    )
    ar.mul_xor0(builder, c0, first, c1)
    scale_inplace(
        builder, first, second, ratio_inverse, ratio_scratch, ar
    )
    erase_borrowed_inverse(ratio_workspace, second, ratio_inverse)
    xor_row_ratio_denominator()
    xor_row_ratio_numerator()

    builder.swap(c0, a0)
    builder.swap(c1, a1)
    builder.free(extra)
    builder.free(second)
    builder.free(temp)

    # Recompute the pivot after the matrix transform and erase its control tag.
    temp = builder.alloc_qubits(FIELD_BITS)
    xor_p(first, temp)
    xor_zero_flag(builder, first, rank[0])
    unxor_p(first, temp)
    builder.free(temp)
    builder.free(first)
    xor_constant(builder, rank, RANK_TAG)


def tail_b_pair_map_inplace_factored(
    builder, words, rank, pivot, ar, phase_inverse36_pivot, km
):
    """Use a fixed nonzero pivot to apply the 2x2 inverse matrix branchlessly."""
    c0, c1, a0, a1 = words
    field = ar.field(FIELD_BITS)
    identity = [1 << bit for bit in range(FIELD_BITS)]

    def columns(value):
        return [field.mul(value, bit) for bit in identity]

    scale_u = field.mul(6, field.invert(20))
    inverse_scale_u = field.invert(scale_u)
    inverse_six_columns = columns(field.invert(6))
    inverse_twenty_columns = columns(field.invert(20))
    twenty_columns = columns(20)
    six_columns = columns(6)
    ten_columns = columns(10)
    square_six_columns = [
        field.mul(6, field.mul(bit, bit)) for bit in identity
    ]

    xor_constant(builder, rank, RANK_TAG)
    extra = builder.alloc_qubits(3)
    borrowed = list(rank) + [pivot] + list(extra)

    def toggle_w1(target):
        ar.linear_xor(builder, a0, target, identity)
        ar.linear_xor(builder, a1, target, identity)
        xor_constant(builder, target, 1)

    def toggle_w2(target):
        ar.linear_xor(builder, a0, target, identity)
        ar.linear_xor(builder, a1, target, columns(2))
        xor_constant(builder, target, 4)

    def compute_inverse(value, target, extra_workspace=()):
        workspace = BorrowedScratchBuilder(
            builder, borrowed + list(extra_workspace), km
        )
        ar.inverse(workspace, value, target=target)
        workspace.assert_released()

    def erase_inverse(value, inverse, extra_workspace=()):
        mask = builder.alloc_bits(FIELD_BITS)
        workspace = BorrowedScratchBuilder(
            builder, borrowed + list(extra_workspace), km
        )
        workspace.hmr(inverse, mask)
        workspace.free(inverse)
        phase_inverse36_pivot(workspace, value, mask)
        workspace.free(mask)
        workspace.assert_released()

    def toggle_n01(target):
        ar.linear_xor(builder, a1, borrowed, six_columns)
        xor_constant(builder, borrowed, 10)
        ar.mul_xor0(builder, a0, borrowed, target)
        ar.linear_xor(builder, a1, borrowed, six_columns)
        xor_constant(builder, borrowed, 10)

    def toggle_n11(target):
        ar.linear_xor(builder, a0, target, six_columns)
        ar.linear_xor(builder, a1, target, square_six_columns)
        ar.linear_xor(builder, a1, target, ten_columns)
        xor_constant(builder, target, 12)

    def build_u(target):
        toggle_w1(borrowed)
        ar.mul_xor0(builder, a0, borrowed, target)
        ar.linear_inplace(builder, target, columns(scale_u))
        toggle_w1(borrowed)

    def unbuild_u(target):
        ar.linear_inplace(builder, target, columns(inverse_scale_u))
        toggle_w1(borrowed)
        ar.mul_xor0(builder, a0, borrowed, target)
        toggle_w1(borrowed)

    # First apply the upper row factor. q=(6*a1+10)/(6*W1).
    u = builder.alloc_qubits(FIELD_BITS)
    inverse_u = builder.alloc_qubits(FIELD_BITS)
    q = builder.alloc_qubits(FIELD_BITS)
    build_u(u)
    compute_inverse(u, inverse_u, q)
    builder.cx(c0, c1)
    ar.linear_xor(builder, a1, borrowed, six_columns)
    xor_constant(builder, borrowed, 10)
    ar.mul_xor0(builder, a0, borrowed, q)
    ar.linear_xor(builder, a1, borrowed, six_columns)
    xor_constant(builder, borrowed, 10)
    scale_inplace(builder, q, inverse_u, u, borrowed, ar)
    ar.linear_inplace(builder, q, inverse_twenty_columns)
    ar.mul_xor0(builder, q, c1, c0)
    ar.linear_inplace(builder, q, twenty_columns)
    scale_inplace(builder, q, u, inverse_u, borrowed, ar)
    ar.linear_xor(builder, a1, borrowed, six_columns)
    xor_constant(builder, borrowed, 10)
    ar.mul_xor0(builder, a0, borrowed, q)
    ar.linear_xor(builder, a1, borrowed, six_columns)
    xor_constant(builder, borrowed, 10)
    erase_inverse(u, inverse_u, q)
    unbuild_u(u)
    builder.free(u)
    builder.free(q)

    # Reorder the lower factor through D: r'=z/d, where
    # z=(N01+N11)/20, d=W2/6, and N11=6*a0+6*a1^2+10*a1+12.
    d = builder.alloc_qubits(FIELD_BITS)
    inverse_d = builder.alloc_qubits(FIELD_BITS)
    r = builder.alloc_qubits(FIELD_BITS)
    toggle_w2(d)
    ar.linear_inplace(builder, d, inverse_six_columns)
    compute_inverse(d, inverse_d, r)
    toggle_n01(r)
    toggle_n11(r)
    scale_inplace(builder, r, inverse_d, d, borrowed, ar)
    ar.linear_inplace(builder, r, inverse_twenty_columns)
    ar.mul_xor0(builder, r, c0, c1)
    ar.linear_inplace(builder, r, twenty_columns)
    scale_inplace(builder, r, d, inverse_d, borrowed, ar)
    toggle_n11(r)
    toggle_n01(r)
    scale_inplace(builder, c1, d, inverse_d, borrowed, ar)
    erase_inverse(d, inverse_d, r)
    ar.linear_inplace(builder, d, six_columns)
    toggle_w2(d)
    builder.free(d)

    # Apply the first diagonal factor after both row factors.
    u = builder.alloc_qubits(FIELD_BITS)
    inverse_u = builder.alloc_qubits(FIELD_BITS)
    build_u(u)
    compute_inverse(u, inverse_u, r)
    scale_inplace(builder, c0, u, inverse_u, borrowed, ar)
    erase_inverse(u, inverse_u, r)
    unbuild_u(u)
    builder.free(u)
    builder.free(r)

    builder.swap(c0, a0)
    builder.swap(c1, a1)
    builder.free(extra)
    xor_constant(builder, rank, RANK_TAG)

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


def build_prefix_coefficient_state(km=None, ar=None):
    """Build an in-place compact-prefix-to-coefficient reversible cell."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    _, _, phase_inverse36_pivot = load_width_helpers(km)
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)[0]
    words = [
        payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
        for index in range(4)
    ]
    prefix_to_coefficients_inplace(
        builder, words, rank, pivot, ar, phase_inverse36_pivot, km
    )
    circuit = builder.finish_circuit()
    return km, ar, circuit, {"payload": payload, "rank": rank, "pivot": pivot}


def run_prefix_coefficient_screen(km=None, ar=None):
    """Measure compact prefix decoding, including the complementary pivot."""
    km, ar, circuit, registers = build_prefix_coefficient_state(km, ar)
    field = ar.field(FIELD_BITS)
    cases = generate_cases(field)
    assert {case[2] for case in cases} == {0, 1}
    inputs = np.asarray([case[1] for case in cases], dtype=np.uint32)
    expected = np.asarray([case[0] for case in cases], dtype=np.uint32)
    spectator_rng = Random(0xA46605B)
    spectators = np.asarray(
        [
            [spectator_rng.randrange(1 << FIELD_BITS) for _ in range(66)]
            for _ in cases
        ],
        dtype=np.uint32,
    )
    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
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
    rank_values = np.full(len(cases), RANK_TAG, dtype=np.uint32)
    sim.write_across_shots(registers["rank"], bit_columns(rank_values, 8))
    sim.write_across_shots(
        registers["pivot"], bit_columns(np.zeros(len(cases), dtype=np.uint32), 1)[0]
    )
    sim.do(circuit)

    actual = np.stack(
        [
            sim.read_across_shots(
                registers["payload"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(4)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_bits = np.stack(
        [bit_columns(expected[:, index], FIELD_BITS).T for index in range(4)],
        axis=1,
    )
    mismatches = np.argwhere(actual != expected_bits)
    if len(mismatches):
        shot, word, bit = map(int, mismatches[0])
        actual_words = [
            sum(int(value) << index for index, value in enumerate(actual[shot, i]))
            for i in range(4)
        ]
        raise AssertionError(
            "prefix coefficient mismatch: "
            f"shot={shot}, word={word}, bit={bit}, "
            f"input={inputs[shot].tolist()}, "
            f"actual={actual_words}, expected={expected[shot].tolist()}, "
            f"pivot={cases[shot][2]}"
        )
    for word in range(66):
        offset = (word + 4) * FIELD_BITS
        actual_word = sim.read_across_shots(
            registers["payload"][offset : offset + FIELD_BITS]
        )
        assert np.array_equal(actual_word, bit_columns(spectators[:, word], FIELD_BITS))
    assert np.array_equal(
        sim.read_across_shots(registers["rank"]), bit_columns(rank_values, 8)
    )
    assert not np.any(sim.read_across_shots(registers["pivot"]))

    live = set(registers["payload"]) | set(registers["rank"]) | {registers["pivot"]}
    scratch = [km.q(i) for i in range(circuit.num_qubits) if km.q(i) not in live]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())
    return {
        "cases": len(cases),
        "pivot_coverage": {
            "c0_nonzero": sum(not case[2] for case in cases),
            "c0_zero": sum(case[2] for case in cases),
        },
        "coefficient_errors": 0,
        "preserved_spectator_words": 66,
        "preserved_rank_and_pivot": True,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "Compact prefix to four coefficients only; matrix setup and 66-symbol circuit are not included.",
    }


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


def build_bezout_matrix_state(km=None, ar=None, point=4):
    """Replace four coefficients with their tail matrix and retain b1."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)
    outputs = builder.alloc_qubits(2 * FIELD_BITS)
    scratch_pool = builder.alloc_qubits(16)
    b1_tag = scratch_pool[:FIELD_BITS]
    square_b1 = b1_tag
    borrowed = list(rank) + [pivot[0]] + list(scratch_pool)
    workspace = BorrowedScratchBuilder(builder, borrowed, km)
    first = outputs[:FIELD_BITS]
    second = outputs[FIELD_BITS:]

    a0, a1, b0, b1 = [
        payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
        for index in range(4)
    ]
    field = ar.field(FIELD_BITS)
    identity = [1 << bit for bit in range(FIELD_BITS)]
    point_columns = [field.mul(point, value) for value in identity]
    square = [field.mul(value, value) for value in identity]
    node_value = 1
    for prefix_point in POINTS:
        node_value = field.mul(node_value, point ^ prefix_point)
    node_columns = [field.mul(node_value, value) for value in identity]
    inverse_node_columns = [
        field.mul(field.invert(node_value), value) for value in identity
    ]

    xor_constant(builder, rank, RANK_TAG)
    ar.linear_xor(builder, a1, a0, point_columns)
    xor_constant(builder, a0, field.mul(point, point))
    ar.linear_xor(builder, b1, b0, point_columns)

    ar.inverse(workspace, b1, target=first)
    workspace.assert_released()
    ar.linear_xor(builder, first, square_b1, square)
    ar.mul_xor0(builder, a1, first, second)
    ar.mul_xor0(builder, b0, square_b1, second)
    ar.linear_xor(builder, first, square_b1, square)
    builder.swap(a1, second)
    ar.mul_xor0(builder, a1, b1, second)
    ar.mul_xor0(builder, b0, first, second)
    ar.erase_inverse(workspace, b1, first)
    workspace.assert_released()

    for bit in range(FIELD_BITS):
        builder.cx(b1[bit], b1_tag[bit])
        builder.cx(b1_tag[bit], b1[bit])
    ar.mul_xor0(builder, a1, b0, b1)
    ar.linear_xor(builder, a0, b1, identity)

    matrix_workspace = BorrowedScratchBuilder(
        builder,
        list(rank) + [pivot[0]] + list(scratch_pool[FIELD_BITS:]) + list(first),
        km,
    )
    ar.inverse(matrix_workspace, b1, target=second)
    matrix_workspace.assert_released()
    ar.linear_inplace(builder, second, node_columns)
    ar.linear_xor(builder, b1, first, inverse_node_columns)
    builder.swap(b1, second)
    ar.mul_xor0(builder, a1, b0, second)
    ar.linear_xor(builder, a0, second, identity)

    ar.mul_xor0(builder, a1, b1, second)
    builder.swap(a1, second)
    ar.mul_xor0(builder, a1, first, second)
    determinant_workspace = BorrowedScratchBuilder(
        builder,
        list(rank) + [pivot[0]] + list(scratch_pool[FIELD_BITS:]) + list(second),
        km,
    )
    ar.erase_inverse(determinant_workspace, b1, first)
    determinant_workspace.assert_released()

    builder.swap(a1, b0)
    xor_constant(builder, rank, RANK_TAG)
    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "pivot": pivot[0],
        "b1_tag": b1_tag,
        "outputs": outputs,
        "scratch": scratch_pool[FIELD_BITS:],
    }


def run_bezout_matrix_state_screen(case_count=64, point=4, km=None, ar=None):
    """Measure reversible in-place coefficient-to-matrix setup and cleanup."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    km, ar, circuit, registers = build_bezout_matrix_state(km, ar, point)
    field = ar.field(FIELD_BITS)
    rng = Random(0xA46605A)
    input_words = np.asarray(
        [
            [rng.randrange(1 << FIELD_BITS) for _ in range(70)]
            for _ in range(case_count)
        ],
        dtype=np.uint32,
    )
    expected = np.zeros((case_count, 4), dtype=np.uint32)
    for shot in range(case_count):
        coefficients, _, _ = sample_coefficients(field, rng)
        a0, a1, b0, b1 = coefficients
        input_words[shot, :4] = coefficients
        inverse_b1 = field.invert(b1)
        q0 = field.mul(inverse_b1, a1 ^ field.mul(inverse_b1, b0))
        gcd = a0 ^ field.mul(q0, b0)
        assert gcd
        node = 1
        for prefix_point in POINTS:
            node = field.mul(node, point ^ prefix_point)
        scale = field.mul(node, field.invert(gcd))
        q_at_point = q0 ^ field.mul(inverse_b1, point)
        expected[shot] = (
            field.mul(point, point) ^ field.mul(a1, point) ^ a0,
            field.mul(b1, point) ^ b0,
            field.mul(scale, q_at_point),
            scale,
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
                registers["payload"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(4)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_bits = np.stack(
        [bit_columns(expected[:, index], FIELD_BITS).T for index in range(4)],
        axis=1,
    )
    assert np.array_equal(actual, expected_bits)
    for word in range(4, 70):
        actual_word = sim.read_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
        )
        assert np.array_equal(actual_word, bit_columns(input_words[:, word], FIELD_BITS))
    assert np.array_equal(
        sim.read_across_shots(registers["b1_tag"]),
        bit_columns(input_words[:, 3], FIELD_BITS),
    )
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
        | set(registers["b1_tag"])
    )
    scratch = [km.q(index) for index in range(circuit.num_qubits) if km.q(index) not in live]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())
    return {
        "cases": case_count,
        "point": point,
        "matrix_errors": 0,
        "preserved_payload_words": 66,
        "b1_tag_errors": 0,
        "preserved_rank_and_pivot": True,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "In-place one-time matrix setup from four supplied coefficients, retaining b1 for reversible recovery; no compact prefix input or 66-symbol reuse.",
    }


def append_bezout_tail_action(builder, payload, rank, pivot, outputs, ar, km, point):
    """Append one coefficient-derived Bezout action to an existing builder."""
    xor_constant(builder, rank, RANK_TAG)
    scratch_pool = builder.alloc_qubits(16)
    borrowed = list(rank) + [pivot] + list(scratch_pool)
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
    return scratch_pool


def build_bezout_tail_action(km=None, ar=None, point=4):
    """Generate the Bezout tail action from a quadratic/linear row."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)
    outputs = builder.alloc_qubits(2 * FIELD_BITS)
    append_bezout_tail_action(
        builder, payload, rank, pivot[0], outputs, ar, km, point
    )
    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "pivot": pivot[0],
        "outputs": outputs,
    }


def build_compact_prefix_tail_action(km=None, ar=None, point=4):
    """Decode the compact prefix and apply one tail action in the same circuit."""
    if km is None or ar is None:
        km, ar = load_gate_arithmetic()
    _, _, phase_inverse36_pivot = load_width_helpers(km)
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(70 * FIELD_BITS)
    rank = builder.alloc_qubits(8)
    pivot = builder.alloc_qubits(1)[0]
    words = [
        payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
        for index in range(4)
    ]
    prefix_to_coefficients_inplace(
        builder, words, rank, pivot, ar, phase_inverse36_pivot, km
    )
    outputs = builder.alloc_qubits(2 * FIELD_BITS)
    append_bezout_tail_action(
        builder, payload, rank, pivot, outputs, ar, km, point
    )
    circuit = builder.finish_circuit()
    return km, ar, circuit, {
        "payload": payload,
        "rank": rank,
        "pivot": pivot,
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


def run_compact_prefix_tail_action_screen(case_count=32, point=4, km=None, ar=None):
    """Measure the compact-prefix decoder and one coefficient-derived tail action together."""
    km, ar, circuit, registers = build_compact_prefix_tail_action(km, ar, point)
    field = ar.field(FIELD_BITS)
    cases = generate_cases(field, case_count)
    rng = Random(0xA6605C)
    input_words = np.asarray(
        [[rng.randrange(1 << FIELD_BITS) for _ in range(70)] for _ in cases],
        dtype=np.uint32,
    )
    expected_coefficients = np.zeros((case_count, 4), dtype=np.uint32)
    expected_outputs = np.zeros((case_count, 2), dtype=np.uint32)

    for shot, (coefficients, prefix_state, _) in enumerate(cases):
        a0, a1, b0, b1 = coefficients
        input_words[shot, :4] = prefix_state
        sample = int(input_words[shot, 4])
        expected_coefficients[shot] = coefficients

        inverse_b1 = field.invert(b1)
        q0 = field.mul(inverse_b1, a1 ^ field.mul(inverse_b1, b0))
        gcd = a0 ^ field.mul(q0, b0)
        inverse_gcd = field.invert(gcd)
        node = 1
        for prefix_point in POINTS:
            node = field.mul(node, point ^ prefix_point)
        scale = field.mul(node, inverse_gcd)
        q_at_point = q0 ^ field.mul(inverse_b1, point)
        denominator = field.mul(point, point) ^ field.mul(a1, point) ^ a0
        numerator = field.mul(b1, point) ^ b0
        expected_outputs[shot] = (
            field.mul(denominator, sample) ^ numerator,
            field.mul(scale, field.mul(q_at_point, sample) ^ 1),
        )

    rank_values = np.full(case_count, RANK_TAG, dtype=np.uint32)
    sim = km.Simulator(batch_size=case_count, debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    for word in range(70):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(input_words[:, word], FIELD_BITS),
        )
    sim.write_across_shots(registers["rank"], bit_columns(rank_values, 8))
    sim.write_across_shots(
        registers["pivot"], bit_columns(np.zeros(case_count, dtype=np.uint32), 1)[0]
    )
    sim.do(circuit)

    actual_coefficients = np.stack(
        [
            sim.read_across_shots(
                registers["payload"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(4)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_coefficient_bits = np.stack(
        [bit_columns(expected_coefficients[:, index], FIELD_BITS).T for index in range(4)],
        axis=1,
    )
    assert np.array_equal(actual_coefficients, expected_coefficient_bits)

    actual_outputs = np.stack(
        [
            sim.read_across_shots(
                registers["outputs"][index * FIELD_BITS : (index + 1) * FIELD_BITS]
            )
            for index in range(2)
        ],
        axis=0,
    ).transpose(2, 0, 1)
    expected_output_bits = np.stack(
        [bit_columns(expected_outputs[:, index], FIELD_BITS).T for index in range(2)],
        axis=1,
    )
    assert np.array_equal(actual_outputs, expected_output_bits)

    for word in range(4, 70):
        actual_word = sim.read_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
        )
        assert np.array_equal(actual_word, bit_columns(input_words[:, word], FIELD_BITS))
    assert np.array_equal(
        sim.read_across_shots(registers["rank"]), bit_columns(rank_values, 8)
    )
    assert not np.any(sim.read_across_shots(registers["pivot"]))

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
        "point": point,
        "prefix_pivot_coverage": {
            "a0": sum(not case[2] for case in cases),
            "a1": sum(case[2] for case in cases),
        },
        "coefficient_errors": 0,
        "tail_output_errors": 0,
        "preserved_tail_words": 66,
        "preserved_rank_and_pivot": True,
        "compiled_qubits": circuit.num_qubits,
        "qubits_over_890": circuit.num_qubits - 890,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
        "scope": "Compact-prefix-to-coefficients plus one coefficient-derived tail action; the integrated 66-symbol schedule remains open.",
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
        "prefix_coefficient_state": run_prefix_coefficient_screen(km=km, ar=ar),
        "tail_matrix_action": run_tail_matrix_action_screen(km=km, ar=ar),
        "tail_matrix_from_coefficients": run_bezout_tail_action_screen(km=km, ar=ar),
        "prefix_to_one_tail_action": run_compact_prefix_tail_action_screen(km=km, ar=ar),
        "tail_matrix_state_encoding": run_bezout_matrix_state_screen(km=km, ar=ar),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
