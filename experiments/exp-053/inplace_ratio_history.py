"""Compile the in-place sample eraser for normalized FMA prefix labels.

Run the gate circuit only in a private Kaggle kernel.  The circuit consumes a
sample word by XORing the sample decoded from the pivot ratios and branch
history; the verifier checks that the input word and all temporary qubits are
zero afterward.
"""

from __future__ import annotations

import importlib.util
import json
from functools import lru_cache
from pathlib import Path
import subprocess
import sys
from random import Random

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FIELD_BITS = 12
FIELD_DEGREE = 12
POINTS = tuple(range(4))
RANK_HISTORY_OFFSET = 3


@lru_cache(maxsize=1)
def load_gate_arithmetic():
    if not Path("/kaggle/working").is_dir():
        raise RuntimeError("Ported gate arithmetic may run only in a private Kaggle kernel")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "kickmix==1.0.0"],
        check=True,
    )
    km = importlib.import_module("kickmix.kickmix")

    sys.modules.setdefault("circ", km)
    if not hasattr(km, "CircuitBuilder"):
        raise RuntimeError("Installed kickmix.kickmix module does not expose CircuitBuilder")
    embedded = sys.modules.get("dqi_inplace_ratio_arithmetic")
    if embedded is not None:
        return km, embedded
    path = Path(__file__).with_name("field.py")
    spec = importlib.util.spec_from_file_location("dqi_inplace_ratio_arithmetic", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return km, module


def bit_columns(values, width):
    values = np.asarray(values, dtype=np.uint32)
    return np.stack([((values >> bit) & 1).astype(np.bool_) for bit in range(width)])


def replayed_ratios(data, field):
    state = list(data)
    branches = []
    ratios = []
    rank1, rank2 = 0, 1
    for pivot, point in enumerate(POINTS):
        d, g = state[pivot], 1
        for previous in range(pivot):
            ratio = ratios[previous]
            delta = point ^ POINTS[previous]
            old_d = d
            if branches[previous]:
                d = field.mul(ratio, old_d) ^ g
                g = field.mul(delta, old_d)
            else:
                d ^= field.mul(ratio, g)
                g = field.mul(delta, g)
        swap = g == 0 or (d != 0 and rank1 < rank2)
        if swap:
            assert d != 0
            ratio = field.mul(g, field.invert(d))
            rank1, rank2 = rank2, rank1 + 2
        else:
            assert g != 0
            ratio = field.mul(d, field.invert(g))
            rank2 += 2
        ratios.append(ratio)
        branches.append(swap)
    return tuple(ratios), tuple(branches)


def sentinel_labels_for(data, field):
    """Return the triangular projective labels for a four-sample vector."""
    ratios, branches = replayed_ratios(data, field)
    labels = list(ratios)
    rank1, rank2 = 0, 1
    for pivot in range(len(POINTS)):
        a, c = 1, 0
        for previous in range(pivot):
            delta = POINTS[pivot] ^ POINTS[previous]
            ratio = ratios[previous]
            old_a = a
            if branches[previous]:
                a = field.mul(ratio, old_a) ^ c
                c = field.mul(delta, old_a)
            else:
                a ^= field.mul(ratio, c)
                c = field.mul(delta, c)

        order = rank1 < rank2
        if a and c:
            sentinel = (
                field.mul(a, field.invert(c))
                if not order
                else field.mul(c, field.invert(a))
            )
            if not branches[pivot] and ratios[pivot] == 0:
                labels[pivot] = sentinel

        if branches[pivot]:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2
    return tuple(labels)


def rank1_after(branches):
    rank1, rank2 = 0, 1
    for branch in branches:
        if branch:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2
    return rank1


def reflect_rank1(builder, rank1, step, branch):
    """Apply the involution r1 <- 2*step+1-r1 modulo eight."""
    for bit in rank1:
        builder.cx(branch, bit)
    increment = 2 * (step + 1) % (1 << len(rank1))
    if increment:
        builder.iadd(increment, target=rank1, control=branch)


def xor_zero_flag(builder, value, target):
    """Toggle target by [value == 0], using and then clearing a ladder."""
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


def xor_rank_order(builder, rank1, step, target):
    """Toggle target by [rank1 < rank2] before this pivot.

    The rank sum before pivot ``step`` is ``2*step + 1``, so the comparison is
    equivalent to ``rank1 <= step``. The expressions below cover all 3-bit
    rank values, including states not reached by the prefix recurrence.
    """
    if step == 0:
        xor_zero_flag(builder, rank1, target)
    elif step == 1:
        xor_zero_flag(builder, rank1[1:], target)
    elif step == 2:
        both_low = builder.alloc_qubits(1)[0]
        builder.init_and(rank1[1], rank1[0], both_low)
        builder.x(rank1[2])
        builder.x(both_low)
        builder.ccx(rank1[2], both_low, target)
        builder.x(both_low)
        builder.x(rank1[2])
        builder.del_and(rank1[1], rank1[0], both_low)
        builder.free([both_low])
    elif step == 3:
        builder.x(target)
        builder.cx(rank1[2], target)
    elif step == 4:
        if len(rank1) < 4:
            raise ValueError("pivot 4 requires a four-bit rank register")
        # Before pivot 4, rank1 + rank2 == 9, so rank1 < rank2 iff rank1 <= 4.
        # Toggle for rank1 < 8, then cancel the values 5, 6, and 7.
        builder.x(target)
        builder.cx(rank1[3], target)
        low_or = builder.alloc_qubits(1)[0]
        builder.cx(rank1[0], low_or)
        builder.cx(rank1[1], low_or)
        builder.init_and(rank1[0], rank1[1], low_or)
        high_and = builder.alloc_qubits(1)[0]
        builder.x(rank1[3])
        builder.init_and(rank1[3], rank1[2], high_and)
        builder.ccx(high_and, low_or, target)
        builder.del_and(rank1[3], rank1[2], high_and)
        builder.x(rank1[3])
        builder.del_and(rank1[0], rank1[1], low_or)
        builder.cx(rank1[1], low_or)
        builder.cx(rank1[0], low_or)
        builder.free([low_or, high_and])
    else:
        raise ValueError("the prefix encoder supports at most five pivots")


def append_branch_bit(builder, pair_d, pair_g, rank1, step, branch):
    """Compute the FMA branch bit from the pivot pair and rank state."""
    g_zero = builder.alloc_qubits(1)[0]
    d_zero = builder.alloc_qubits(1)[0]
    order = builder.alloc_qubits(1)[0]
    both = builder.alloc_qubits(1)[0]
    xor_zero_flag(builder, pair_g, g_zero)
    xor_zero_flag(builder, pair_d, d_zero)
    xor_rank_order(builder, rank1, step, order)

    # swap = (g == 0) OR ((d != 0) AND (rank1 < rank2)). The second term is
    # gated by g != 0 so the two contributions never overlap.
    builder.cx(g_zero, branch)
    builder.x(d_zero)
    builder.init_and(d_zero, order, both)
    builder.x(g_zero)
    builder.ccx(both, g_zero, branch)
    builder.x(g_zero)
    builder.del_and(d_zero, order, both)
    builder.x(d_zero)

    xor_rank_order(builder, rank1, step, order)
    xor_zero_flag(builder, pair_d, d_zero)
    xor_zero_flag(builder, pair_g, g_zero)
    builder.free([g_zero, d_zero, order, both])


def xor_equal_flag(builder, left, right, target):
    """Toggle target by [left == right] and leave both fields unchanged."""
    difference = builder.alloc_qubits(len(left))
    builder.cx(left, difference)
    builder.cx(right, difference)
    xor_zero_flag(builder, difference, target)
    builder.cx(right, difference)
    builder.cx(left, difference)
    builder.free(difference)


def erase_branch_from_label(
    builder, label, branch, matrix_a, matrix_c, sentinel, order
):
    """Uncompute one branch from its injective projective label."""
    zero = builder.alloc_qubits(1)[0]
    equal_sentinel = builder.alloc_qubits(1)[0]
    a_zero = builder.alloc_qubits(1)[0]
    c_zero = builder.alloc_qubits(1)[0]
    has_sentinel = builder.alloc_qubits(1)[0]
    ordinary = builder.alloc_qubits(1)[0]
    zero_branch = builder.alloc_qubits(1)[0]
    decoded_branch = builder.alloc_qubits(1)[0]

    xor_zero_flag(builder, label, zero)
    xor_equal_flag(builder, label, sentinel, equal_sentinel)
    xor_zero_flag(builder, matrix_a, a_zero)
    xor_zero_flag(builder, matrix_c, c_zero)

    # A sentinel exists exactly when both projective coordinates are nonzero.
    builder.x(a_zero)
    builder.x(c_zero)
    builder.init_and(a_zero, c_zero, has_sentinel)
    builder.x(c_zero)
    builder.x(a_zero)

    # Nonzero labels other than the sentinel retain the rank-order branch.
    builder.x(zero)
    builder.x(equal_sentinel)
    builder.init_and(zero, equal_sentinel, ordinary)
    builder.x(equal_sentinel)
    builder.x(zero)

    # A zero label selects the zero-pivot branch when a sentinel exists;
    # without one, the first matrix coordinate decides the zero case.
    builder.ccx(zero, has_sentinel, zero_branch)
    builder.ccx(zero, a_zero, zero_branch)
    builder.ccx(ordinary, order, decoded_branch)
    builder.cx(zero_branch, decoded_branch)
    builder.cx(decoded_branch, branch)

    builder.cx(zero_branch, decoded_branch)
    builder.ccx(ordinary, order, decoded_branch)
    builder.x(zero)
    builder.x(equal_sentinel)
    builder.del_and(zero, equal_sentinel, ordinary)
    builder.x(equal_sentinel)
    builder.x(zero)
    builder.ccx(zero, a_zero, zero_branch)
    builder.ccx(zero, has_sentinel, zero_branch)

    builder.x(a_zero)
    builder.x(c_zero)
    builder.del_and(a_zero, c_zero, has_sentinel)
    builder.x(c_zero)
    builder.x(a_zero)
    xor_zero_flag(builder, matrix_c, c_zero)
    xor_zero_flag(builder, matrix_a, a_zero)
    xor_equal_flag(builder, label, sentinel, equal_sentinel)
    xor_zero_flag(builder, label, zero)
    builder.free(
        [
            zero,
            equal_sentinel,
            a_zero,
            c_zero,
            has_sentinel,
            ordinary,
            zero_branch,
            decoded_branch,
        ]
    )


def erase_first_branch_from_ratio(builder, ratio, branch):
    """At pivot zero, the raw ratio is nonzero exactly on the swap branch."""
    zero = builder.alloc_qubits(1)[0]
    xor_zero_flag(builder, ratio, zero)
    builder.x(zero)
    builder.cx(zero, branch)
    builder.x(zero)
    xor_zero_flag(builder, ratio, zero)
    builder.free([zero])


def xor_prefix_order(builder, branches, pivot, target):
    """Toggle target by the rank-order bit before one of the first four pivots."""
    if pivot in (0, 1):
        builder.x(target)
        return
    if pivot not in (2, 3):
        raise ValueError("the prefix encoder supports four pivots")

    # For pivots 2 and 3, order is respectively b0 | !b1 and b1 | !b2.
    left = branches[pivot - 2]
    right = branches[pivot - 1]
    work = builder.alloc_qubits(1)[0]
    builder.x(left)
    builder.init_and(left, right, work)
    builder.x(work)
    builder.cx(work, target)
    builder.x(work)
    builder.del_and(left, right, work)
    builder.x(left)
    builder.free([work])


def append_sentinel_label(builder, ratios, branches, pivot, ar):
    """Replace the duplicate zero ratio with its omitted projective label."""
    if pivot not in (1, 2, 3):
        return

    matrix_a = builder.alloc_qubits(FIELD_BITS)
    matrix_c = builder.alloc_qubits(FIELD_BITS)
    sentinel = builder.alloc_qubits(FIELD_BITS)
    order = builder.alloc_qubits(1)[0]
    builder.x(matrix_a[0])
    one = ar.field(FIELD_BITS)

    # The first column is enough to form the omitted projective ratio.
    for previous in range(pivot):
        delta = POINTS[pivot] ^ POINTS[previous]
        builder.cswap(branches[previous], matrix_a, matrix_c)
        ar.mul_xor(builder, ratios[previous], matrix_c, matrix_a)
        builder.gf2_imul(delta, target=matrix_c, field=one)

    xor_prefix_order(builder, branches, pivot, order)
    # The sentinel is a/c when order is false and c/a otherwise.
    builder.cswap(order, matrix_a, matrix_c)
    inverse_transcript = ar.inverse_inplace_forward(builder, matrix_c)
    ar.mul_xor0(builder, matrix_a, matrix_c, sentinel)
    ar.inverse_inplace_reverse(builder, matrix_c, inverse_transcript)
    builder.cswap(order, matrix_a, matrix_c)

    # Clear the prefix matrix before doing the output relabeling.
    for previous in reversed(range(pivot)):
        delta = POINTS[pivot] ^ POINTS[previous]
        inverse_delta = ar.field(FIELD_DEGREE).invert(delta)
        builder.gf2_imul(inverse_delta, target=matrix_c, field=one)
        ar.mul_xor(builder, ratios[previous], matrix_c, matrix_a)
        builder.cswap(branches[previous], matrix_a, matrix_c)
    builder.x(matrix_a[0])
    xor_prefix_order(builder, branches, pivot, order)
    builder.free(matrix_a)
    builder.free(matrix_c)
    builder.free(order)

    # On valid FMA outputs, a zero no-swap ratio is the only duplicate label.
    # Keep the flag until it can be uncomputed from the encoded sentinel value.
    zero = builder.alloc_qubits(1)[0]
    exceptional = builder.alloc_qubits(1)[0]
    xor_zero_flag(builder, ratios[pivot], zero)
    builder.x(branches[pivot])
    builder.ccx(zero, branches[pivot], exceptional)
    builder.x(branches[pivot])
    xor_zero_flag(builder, ratios[pivot], zero)
    for bit in range(FIELD_BITS):
        builder.ccx(exceptional, sentinel[bit], ratios[pivot][bit])

    xor_equal_flag(builder, ratios[pivot], sentinel, zero)
    builder.x(branches[pivot])
    builder.ccx(zero, branches[pivot], exceptional)
    builder.x(branches[pivot])
    xor_equal_flag(builder, ratios[pivot], sentinel, zero)
    builder.free([zero, exceptional])

    # Recompute the sentinel into its output register to clear it, then erase
    # the temporary prefix matrix again.
    matrix_a = builder.alloc_qubits(FIELD_BITS)
    matrix_c = builder.alloc_qubits(FIELD_BITS)
    order = builder.alloc_qubits(1)[0]
    builder.x(matrix_a[0])
    for previous in range(pivot):
        delta = POINTS[pivot] ^ POINTS[previous]
        builder.cswap(branches[previous], matrix_a, matrix_c)
        ar.mul_xor(builder, ratios[previous], matrix_c, matrix_a)
        builder.gf2_imul(delta, target=matrix_c, field=one)
    xor_prefix_order(builder, branches, pivot, order)
    builder.cswap(order, matrix_a, matrix_c)
    inverse_transcript = ar.inverse_inplace_forward(builder, matrix_c)
    ar.mul_xor0(builder, matrix_a, matrix_c, sentinel)
    ar.inverse_inplace_reverse(builder, matrix_c, inverse_transcript)
    builder.cswap(order, matrix_a, matrix_c)
    erase_branch_from_label(
        builder, ratios[pivot], branches[pivot],
        matrix_a, matrix_c, sentinel, order
    )
    for previous in reversed(range(pivot)):
        delta = POINTS[pivot] ^ POINTS[previous]
        inverse_delta = ar.field(FIELD_DEGREE).invert(delta)
        builder.gf2_imul(inverse_delta, target=matrix_c, field=one)
        ar.mul_xor(builder, ratios[previous], matrix_c, matrix_a)
        builder.cswap(branches[previous], matrix_a, matrix_c)
    builder.x(matrix_a[0])
    xor_prefix_order(builder, branches, pivot, order)
    builder.free(matrix_a)
    builder.free(matrix_c)
    builder.free(order)
    builder.free(sentinel)


def build_prefix_encoder(
    in_place=False,
    sentinel_labels=False,
    measurement_erase=False,
    measurement_recycle=False,
):
    """Build a short prefix map: samples -> ratios plus branch history."""
    if measurement_erase and (not in_place or sentinel_labels):
        raise ValueError("measurement erasure requires the in-place ratio/history map")
    if measurement_recycle and (
        not in_place or measurement_erase
    ):
        raise ValueError("measurement recycling requires the in-place ratio/history map")
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    if len(POINTS) > 5:
        raise ValueError("the compiled prefix encoder supports at most five pivots")
    payload = builder.alloc_qubits(840)
    rank_bits = max(3, (2 * len(POINTS) - 1).bit_length())
    rank_history = builder.alloc_qubits(rank_bits + len(POINTS) + 1)
    rank1 = list(rank_history[:rank_bits])
    branch_start = rank_bits
    branches = list(rank_history[branch_start : branch_start + len(POINTS)])
    spare_rank_bit = rank_history[branch_start + len(POINTS)]
    ratios = [payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
              for index in range(len(POINTS))]
    samples = (
        ratios
        if in_place
        else [payload[(len(POINTS) + index) * FIELD_BITS :
                      (len(POINTS) + index + 1) * FIELD_BITS]
              for index in range(len(POINTS))]
    )
    ratio_temp = (
        builder.alloc_qubits(FIELD_BITS)
        if in_place and not measurement_recycle
        else None
    )
    one = ar.field(FIELD_BITS)

    for pivot, point in enumerate(POINTS):
        pair_d = builder.alloc_qubits(FIELD_BITS)
        pair_g = builder.alloc_qubits(FIELD_BITS)
        builder.cx(samples[pivot], pair_d)
        builder.x(pair_g[0])

        # Replay the earlier normalized FMA updates on (sample_j, 1).
        for previous in range(pivot):
            delta = point ^ POINTS[previous]
            builder.cswap(branches[previous], pair_d, pair_g)
            ar.mul_xor(builder, ratios[previous], pair_g, pair_d)
            builder.gf2_imul(delta, target=pair_g, field=one)

        measurement_mask = None
        if measurement_recycle:
            source_ids = {str(qubit) for qubit in samples[pivot]}
            measurement_mask = builder.alloc_bits(FIELD_BITS)
            builder.hmr(samples[pivot], measurement_mask)
            builder.free(samples[pivot])
            ratio_slot = list(builder.alloc_qubits(FIELD_BITS))
            if {str(qubit) for qubit in ratio_slot} != source_ids:
                raise RuntimeError("measured sample wires were not reused for the ratio")
            samples[pivot] = ratio_slot

        append_branch_bit(builder, pair_d, pair_g, rank1, pivot, branches[pivot])
        reflect_rank1(builder, rank1, pivot, branches[pivot])

        # Rank1 is determined by the branch prefix. Clear its bits and borrow
        # them, plus the spare rank bit, for the in-place inverse.
        for step in reversed(range(pivot + 1)):
            reflect_rank1(builder, rank1, step, branches[step])
        builder.free(rank1)
        builder.free([spare_rank_bit])

        builder.cswap(branches[pivot], pair_d, pair_g)
        inverse_transcript = ar.inverse_inplace_forward(builder, pair_g)
        ratio_target = (
            samples[pivot]
            if measurement_recycle
            else ratio_temp if in_place else ratios[pivot]
        )
        ar.mul_xor0(
            builder,
            pair_d,
            pair_g,
            ratio_target,
        )
        ar.inverse_inplace_reverse(builder, pair_g, inverse_transcript)
        builder.cswap(branches[pivot], pair_d, pair_g)

        rank1 = list(builder.alloc_qubits(rank_bits))
        spare_rank_bit = builder.alloc_qubits(1)[0]
        for step in range(pivot + 1):
            reflect_rank1(builder, rank1, step, branches[step])

        # Undo the replay and clear this temporary copy of the sample.
        for previous in reversed(range(pivot)):
            delta = point ^ POINTS[previous]
            inverse_delta = ar.field(FIELD_DEGREE).invert(delta)
            builder.gf2_imul(inverse_delta, target=pair_g, field=one)
            ar.mul_xor(builder, ratios[previous], pair_g, pair_d)
            builder.cswap(branches[previous], pair_d, pair_g)
        if measurement_recycle:
            builder.x(pair_g[0])
            builder.free(pair_g)
            ratio_words = ratios[:pivot] + [samples[pivot]]
            clear_mask = builder.alloc_bits(FIELD_BITS)
            builder.hmr(pair_d, clear_mask)
            builder.free(pair_d)
            builder.cx(clear_mask, measurement_mask)
            builder.free(clear_mask)
            append_sample_eraser(
                builder,
                payload,
                rank1,
                branches,
                spare_rank_bit,
                pivot,
                ar,
                ratio_words=ratio_words,
                phase_mask=measurement_mask,
                phase_only=True,
            )
            builder.free(measurement_mask)
        elif in_place:
            builder.cx(samples[pivot], pair_d)
            builder.x(pair_g[0])
            builder.free(pair_d)
            builder.free(pair_g)
            if measurement_erase:
                append_sample_eraser_mbu(
                    builder,
                    payload,
                    rank1,
                    branches,
                    spare_rank_bit,
                    pivot,
                    ar,
                    sample=samples[pivot],
                    ratio_words=ratios[:pivot] + [ratio_temp],
                )
            else:
                append_sample_eraser(
                    builder,
                    payload,
                    rank1,
                    branches,
                    spare_rank_bit,
                    pivot,
                    ar,
                    sample=samples[pivot],
                    ratio_words=ratios[:pivot] + [ratio_temp],
                )
            builder.swap(ratio_temp, samples[pivot])
        else:
            builder.cx(samples[pivot], pair_d)
            builder.x(pair_g[0])
            builder.free(pair_d)
            builder.free(pair_g)
            append_sample_eraser(
                builder, payload, rank1, branches, spare_rank_bit, pivot, ar
            )

    if sentinel_labels:
        # Descending order keeps every earlier ratio in its raw form while its
        # prefix matrix is reconstructed. Each branch is then erased from its
        # injective label and its wire becomes reusable workspace.
        for pivot in reversed(range(1, len(POINTS))):
            append_sentinel_label(builder, ratios, branches, pivot, ar)
            builder.free([branches[pivot]])
        erase_first_branch_from_ratio(builder, ratios[0], branches[0])
        builder.free([branches[0]])
        output_branches = []
    else:
        output_branches = branches

    if ratio_temp is not None:
        builder.free(ratio_temp)
    rank_register = rank1 + output_branches + [spare_rank_bit]
    circuit = builder.finish_circuit()
    return km, circuit, {
        "payload": payload,
        "rank1": rank1,
        "branches": output_branches,
        "spare_rank_bit": spare_rank_bit,
        "rank_register": rank_register,
        "ratios": ratios,
        "samples": samples,
        "sentinel_labels": sentinel_labels,
    }


def build_inplace_prefix_encoder():
    return build_prefix_encoder(in_place=True)


def screen_prefix_encoder(
    case_count=32,
    in_place=False,
    use_sentinel_labels=False,
    measurement_erase=False,
    measurement_recycle=False,
):
    km, circuit, registers = build_prefix_encoder(
        in_place=in_place,
        sentinel_labels=use_sentinel_labels,
        measurement_erase=measurement_erase,
        measurement_recycle=measurement_recycle,
    )
    field = km.GF2Field(FIELD_BITS)
    rng = Random(0xF1A05304)
    cases = [
        tuple(0 for _ in POINTS)
        if index == 0
        else tuple(rng.randrange(1 << FIELD_BITS) for _ in POINTS)
        for index in range(case_count)
    ]
    references = [replayed_ratios(data, field) for data in cases]
    expected_ratios = [ratios for ratios, _ in references]
    expected_branches = [branches for _, branches in references]
    expected_output = expected_ratios
    if use_sentinel_labels:
        expected_output = [sentinel_labels_for(data, field) for data in cases]
    if in_place:
        word_values = [
            [rng.randrange(1 << FIELD_BITS) for _ in cases]
            for _ in range(70)
        ]
        for index, data in enumerate(cases):
            for pivot, value in enumerate(data):
                word_values[pivot][index] = value
        untouched_start = len(POINTS)
    else:
        word_values = [[0] * len(cases) for _ in range(70)]
        for index, data in enumerate(cases):
            for pivot, value in enumerate(data):
                word_values[len(POINTS) + pivot][index] = value
            for word in range(2 * len(POINTS), 70):
                word_values[word][index] = rng.randrange(1 << FIELD_BITS)
        untouched_start = 2 * len(POINTS)

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    for word in range(70):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(word_values[word], FIELD_BITS),
        )
    rank_values = [rank1_after(branches) for branches in expected_branches]
    sim.write_across_shots(
        registers["rank1"],
        bit_columns([0] * len(cases), len(registers["rank1"])),
    )
    for pivot in range(len(registers["branches"])):
        sim.write_across_shots(
            registers["branches"][pivot],
            np.zeros(len(cases), dtype=np.bool_),
        )
    sim.write_across_shots(
        registers["spare_rank_bit"], np.zeros(len(cases), dtype=np.bool_)
    )
    sim.do(circuit)

    output_mismatches = []
    for pivot in range(len(registers["ratios"])):
        actual = sim.read_across_shots(registers["ratios"][pivot])
        expected = bit_columns(
            [words[pivot] for words in expected_output], FIELD_BITS
        )
        bad_shots = np.flatnonzero(np.any(actual != expected, axis=0))
        if len(bad_shots):
            actual_words = np.sum(
                actual.astype(np.uint32)
                * (1 << np.arange(FIELD_BITS, dtype=np.uint32))[:, None],
                axis=0,
            )
            expected_words = np.sum(
                expected.astype(np.uint32)
                * (1 << np.arange(FIELD_BITS, dtype=np.uint32))[:, None],
                axis=0,
            )
            output_mismatches.extend(
                {
                    "pivot": pivot,
                    "shot": int(shot),
                    "actual": int(actual_words[shot]),
                    "expected": int(expected_words[shot]),
                }
                for shot in bad_shots[:8]
            )
        if not in_place:
            assert not np.any(sim.read_across_shots(registers["samples"][pivot]))
        if not use_sentinel_labels:
            actual_branch = sim.read_across_shots(registers["branches"][pivot])
            expected_branch = np.asarray(
                [bool(branches[pivot]) for branches in expected_branches],
                dtype=np.bool_,
            )
            assert np.array_equal(actual_branch, expected_branch), {
                "pivot": pivot,
                "bad_shots": np.flatnonzero(actual_branch != expected_branch)[
                    :8
                ].tolist(),
            }
    for word in range(untouched_start, 70):
        assert np.array_equal(
            sim.read_across_shots(
                registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
            ),
            bit_columns(word_values[word], FIELD_BITS),
        )
    assert np.array_equal(
        sim.read_across_shots(registers["rank1"]),
        bit_columns(rank_values, len(registers["rank1"])),
    )
    assert not np.any(sim.read_across_shots(registers["spare_rank_bit"]))

    live = set(list(registers["payload"]) + registers["rank_register"])
    scratch = [
        km.q(index)
        for index in range(circuit.num_qubits)
        if km.q(index) not in live
    ]
    scratch_state = np.zeros((0, len(cases)), dtype=np.bool_)
    if scratch:
        scratch_state = sim.read_across_shots(km.array(scratch))
    dirty_scratch = [
        str(scratch[index])
        for index in np.flatnonzero(np.any(scratch_state, axis=1))
    ]
    phase_flips = int(np.count_nonzero(sim.read_phase_flipped_across_shots()))
    return {
        "cases": len(cases),
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "output_labels_match_reference": not output_mismatches,
        "output_mismatches": output_mismatches,
        "branch_history_matches_reference": None if use_sentinel_labels else True,
        "branch_registers_erased": use_sentinel_labels,
        "original_ratio_words_overwritten_in_place": in_place,
        "sentinel_labels": use_sentinel_labels,
        "measurement_erase": measurement_erase,
        "measurement_recycle": measurement_recycle,
        "samples_cleared": not in_place,
        "other_payload_preserved": True,
        "scratch_clean": not dirty_scratch,
        "dirty_scratch_qubits": dirty_scratch,
        "phase_flips": phase_flips,
    }


def screen_inplace_prefix_encoder(
    case_count=32,
    use_sentinel_labels=False,
    measurement_erase=False,
    measurement_recycle=False,
    point_count=None,
):
    global POINTS
    original_points = POINTS
    if point_count is not None:
        if not 1 <= point_count <= 5:
            raise ValueError("point_count must be between 1 and 5")
        POINTS = tuple(range(point_count))
    try:
        return screen_prefix_encoder(
            case_count,
            in_place=True,
            use_sentinel_labels=use_sentinel_labels,
            measurement_erase=measurement_erase,
            measurement_recycle=measurement_recycle,
        )
    finally:
        POINTS = original_points


def append_sample_eraser(
    builder,
    payload,
    rank_low,
    branches,
    spare_rank_bit,
    pivot,
    ar,
    *,
    sample=None,
    ratio_words=None,
    phase_mask=None,
    phase_only=False,
):
    """Append sample_j ^= decode(r_0..r_j, b_0..b_j) to an existing circuit."""
    # At the four-point split, rank1 is determined by branch history. Restore
    # its three low bits to zero and borrow them plus the unused high bit as
    # clean arithmetic workspace; rank1 is recomputed before returning.
    for step in range(pivot, -1, -1):
        reflect_rank1(builder, rank_low, step, branches[step])
    builder.free(rank_low)
    builder.free(spare_rank_bit)

    pair_d = builder.alloc_qubits(FIELD_BITS)
    pair_g = builder.alloc_qubits(FIELD_BITS)
    borrowed_rank_ids = {str(qubit) for qubit in rank_low + [spare_rank_bit]}
    pair_ids = {str(qubit) for qubit in list(pair_d) + list(pair_g)}
    if borrowed_rank_ids - pair_ids:
        raise RuntimeError("Kickmix did not reuse the four released rank workspace wires")
    if ratio_words is None:
        ratio_words = [
            payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
            for index in range(pivot + 1)
        ]
    ratios = ratio_words
    branches = branches[: pivot + 1]
    if phase_only and (sample is not None or phase_mask is None):
        raise ValueError("phase-only erasure requires a phase mask and no sample target")
    if sample is None and not phase_only:
        sample = payload[(len(POINTS) + pivot) * FIELD_BITS :
                         (len(POINTS) + pivot + 1) * FIELD_BITS]
    one = ar.field(FIELD_BITS)

    # The branch bit chooses projective coordinates [r:1] or [1:r].
    builder.cx(ratios[pivot], pair_d)
    builder.x(pair_g[0])
    builder.cswap(branches[pivot], pair_d, pair_g)

    # Undo each earlier normalized FMA update in reverse pivot order.
    for previous in range(pivot - 1, -1, -1):
        delta = POINTS[pivot] ^ POINTS[previous]
        inverse_delta = ar.field(FIELD_DEGREE).invert(delta)
        builder.gf2_imul(inverse_delta, target=pair_g, field=one)
        ar.mul_xor(builder, ratios[previous], pair_g, pair_d)
        builder.cswap(branches[previous], pair_d, pair_g)

    inverse_transcript = ar.inverse_inplace_forward(builder, pair_g)
    if phase_mask is not None:
        ar.phase_product(builder, pair_d, pair_g, phase_mask)
    if not phase_only:
        ar.mul_xor0(builder, pair_d, pair_g, sample)
    ar.inverse_inplace_reverse(builder, pair_g, inverse_transcript)

    # Reverse the decoder so its field-pair workspace is clean.
    for previous in range(pivot):
        builder.cswap(branches[previous], pair_d, pair_g)
        ar.mul_xor(builder, ratios[previous], pair_g, pair_d)
        delta = POINTS[pivot] ^ POINTS[previous]
        builder.gf2_imul(delta, target=pair_g, field=one)
    builder.cswap(branches[pivot], pair_d, pair_g)
    builder.x(pair_g[0])
    builder.cx(ratios[pivot], pair_d)

    reusable_pair = [qubit for qubit in list(pair_d) + list(pair_g)
                     if str(qubit) not in borrowed_rank_ids]
    builder.free(reusable_pair)
    for step in range(pivot + 1):
        reflect_rank1(builder, rank_low, step, branches[step])


def append_sample_eraser_mbu(
    builder,
    payload,
    rank_low,
    branches,
    spare_rank_bit,
    pivot,
    ar,
    *,
    sample,
    ratio_words,
):
    """Measure the redundant source sample and correct its phase from ratios."""
    sample_ids = [str(qubit) for qubit in sample]
    mask = builder.alloc_bits(FIELD_BITS)
    builder.hmr(sample, mask)
    builder.free(sample)

    reused = list(builder.alloc_qubits(FIELD_BITS))
    by_id = {str(qubit): qubit for qubit in reused}
    if set(by_id) != set(sample_ids):
        raise RuntimeError("sample measurement did not release its original qubits")
    target = [by_id[qubit_id] for qubit_id in sample_ids]

    # Reconstruct the measured value, apply (-1)^(mask . sample), then clear it.
    append_sample_eraser(
        builder,
        payload,
        rank_low,
        branches,
        spare_rank_bit,
        pivot,
        ar,
        sample=target,
        ratio_words=ratio_words,
    )
    for bit in range(FIELD_BITS):
        builder.cz(target[bit], mask[bit])
    append_sample_eraser(
        builder,
        payload,
        rank_low,
        branches,
        spare_rank_bit,
        pivot,
        ar,
        sample=target,
        ratio_words=ratio_words,
    )
    builder.free(mask)


def build_sample_eraser(pivot):
    """Build sample_j ^= decode(r_0..r_j, b_0..b_j)."""
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(840)
    rank_history = builder.alloc_qubits(8)
    rank_low = list(rank_history[:3])
    branches = [rank_history[RANK_HISTORY_OFFSET + index]
                for index in range(pivot + 1)]
    spare_rank_bit = rank_history[7]
    append_sample_eraser(
        builder, payload, rank_low, branches, spare_rank_bit, pivot, ar
    )
    ratios = [payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
              for index in range(pivot + 1)]
    sample = payload[(4 + pivot) * FIELD_BITS : (5 + pivot) * FIELD_BITS]
    rank_register = list(rank_history)

    circuit = builder.finish_circuit()
    return km, circuit, {
        "payload": payload,
        "rank_low": rank_low,
        "rank_register": rank_register,
        "spare_rank_bit": spare_rank_bit,
        "ratios": ratios,
        "branches": branches,
        "sample": sample,
    }


def screen_pivot(pivot, case_count=32):
    km, circuit, registers = build_sample_eraser(pivot)
    field = km.GF2Field(FIELD_BITS)

    rng = Random(0x4F4E4C59 + pivot)
    cases = []
    for index in range(case_count):
        data = (
            (0, 0, 0, 0)
            if index == 0
            else tuple(rng.randrange(1 << FIELD_BITS) for _ in POINTS)
        )
        ratios, branches = replayed_ratios(data, field)
        cases.append((data, ratios, branches))

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    sim.write_across_shots(
        registers["sample"],
        bit_columns([case[0][pivot] for case in cases], FIELD_BITS),
    )
    rank_values = [rank1_after(case[2][: pivot + 1]) for case in cases]
    sim.write_across_shots(registers["rank_low"], bit_columns(rank_values, 3))
    for word in range(pivot + 1):
        sim.write_across_shots(
            registers["ratios"][word],
            bit_columns([case[1][word] for case in cases], FIELD_BITS),
        )
    for index in range(pivot + 1):
        sim.write_across_shots(
            registers["branches"][index],
            np.asarray([bool(case[2][index]) for case in cases], dtype=np.bool_),
        )
    sim.write_across_shots(
        registers["spare_rank_bit"], np.zeros(len(cases), dtype=np.bool_)
    )
    sim.do(circuit)

    assert not np.any(sim.read_across_shots(registers["sample"]))
    assert np.array_equal(
        sim.read_across_shots(registers["rank_low"]),
        bit_columns(rank_values, 3),
    )
    for word in range(pivot + 1):
        assert np.array_equal(
            sim.read_across_shots(registers["ratios"][word]),
            bit_columns([case[1][word] for case in cases], FIELD_BITS),
        )
    for index in range(pivot + 1):
        assert np.array_equal(
            sim.read_across_shots(registers["branches"][index]),
            np.asarray([bool(case[2][index]) for case in cases], dtype=np.bool_),
        )

    assert not np.any(sim.read_across_shots(registers["spare_rank_bit"]))
    live = set(list(registers["payload"]) + registers["rank_register"])
    scratch = [
        km.q(index)
        for index in range(circuit.num_qubits)
        if km.q(index) not in live
    ]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    assert not np.any(sim.read_phase_flipped_across_shots())

    return {
        "pivot": pivot,
        "cases": len(cases),
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "sample_cleared": True,
        "ratios_and_history_preserved": True,
        "phase_flips": 0,
    }


def run_screen():
    clean_slot_result = screen_prefix_encoder()
    inplace_result = screen_inplace_prefix_encoder()
    sentinel_inplace_result = screen_inplace_prefix_encoder(use_sentinel_labels=True)
    mbu_inplace_result = screen_inplace_prefix_encoder(measurement_erase=True)
    measurement_recycle_result = screen_inplace_prefix_encoder(
        measurement_recycle=True
    )
    five_pivot_measurement_recycle_result = screen_inplace_prefix_encoder(
        measurement_recycle=True,
        point_count=5,
    )
    recycled_sentinel_result = screen_inplace_prefix_encoder(
        use_sentinel_labels=True,
        measurement_recycle=True,
    )
    five_pivot_recycled_sentinel_result = screen_inplace_prefix_encoder(
        use_sentinel_labels=True,
        measurement_recycle=True,
        point_count=5,
    )
    results = (
        clean_slot_result,
        inplace_result,
        sentinel_inplace_result,
        mbu_inplace_result,
        measurement_recycle_result,
        five_pivot_measurement_recycle_result,
        recycled_sentinel_result,
        five_pivot_recycled_sentinel_result,
    )
    return {
        "experiment": "exp-053-inplace-ratio-history-prefix-encoder",
        "result": (
            "PASS"
            if all(
                result["scratch_clean"]
                and result["phase_flips"] == 0
                and result["output_labels_match_reference"]
                for result in results
            )
            else "FAIL"
        ),
        "clean_slot_prefix_encoder": clean_slot_result,
        "full_input_inplace_prefix_encoder": inplace_result,
        "full_input_sentinel_label_encoder": sentinel_inplace_result,
        "full_input_mbu_prefix_encoder": mbu_inplace_result,
        "full_input_measurement_recycle_prefix_encoder": measurement_recycle_result,
        "five_pivot_measurement_recycle_prefix_encoder": (
            five_pivot_measurement_recycle_result
        ),
        "four_pivot_recycled_sentinel_prefix_encoder": recycled_sentinel_result,
        "five_pivot_recycled_sentinel_prefix_encoder": (
            five_pivot_recycled_sentinel_result
        ),
        "scope": (
            "Compiled four- and five-pivot ratio/history prefixes for 32 "
            "arbitrary GF(2^12) inputs. Checks labels, branch history, final "
            "rank, payload, scratch, and phase. Also combines measurement "
            "recycling with sentinel-label branch erasure for four and five "
            "pivots. It does not establish the complete 4+66 schedule."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
