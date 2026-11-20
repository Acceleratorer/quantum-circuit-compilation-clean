"""Compile the in-place sample eraser for four pivot ratio/history labels.

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
    else:
        raise ValueError("the prefix encoder supports four pivots")


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


def build_prefix_encoder(in_place=False):
    """Build the four-pivot map: four samples -> ratios plus branch history."""
    km, ar = load_gate_arithmetic()
    builder = km.CircuitBuilder()
    payload = builder.alloc_qubits(840)
    rank_history = builder.alloc_qubits(8)
    rank1 = list(rank_history[:3])
    branches = list(rank_history[RANK_HISTORY_OFFSET : RANK_HISTORY_OFFSET + 4])
    spare_rank_bit = rank_history[7]
    ratios = [payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
              for index in range(4)]
    samples = (
        ratios
        if in_place
        else [payload[(4 + index) * FIELD_BITS : (5 + index) * FIELD_BITS]
              for index in range(4)]
    )
    ratio_temp = builder.alloc_qubits(FIELD_BITS) if in_place else None
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

        append_branch_bit(builder, pair_d, pair_g, rank1, pivot, branches[pivot])
        reflect_rank1(builder, rank1, pivot, branches[pivot])

        # Rank1 is determined by the branch prefix. Clear its three bits and
        # borrow them, plus the unused high bit, for the in-place inverse.
        for step in reversed(range(pivot + 1)):
            reflect_rank1(builder, rank1, step, branches[step])
        builder.free(rank1)
        builder.free([spare_rank_bit])

        builder.cswap(branches[pivot], pair_d, pair_g)
        inverse_transcript = ar.inverse_inplace_forward(builder, pair_g)
        ar.mul_xor0(
            builder,
            pair_d,
            pair_g,
            ratio_temp if in_place else ratios[pivot],
        )
        ar.inverse_inplace_reverse(builder, pair_g, inverse_transcript)
        builder.cswap(branches[pivot], pair_d, pair_g)

        rank1 = list(builder.alloc_qubits(3))
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
        builder.cx(samples[pivot], pair_d)
        builder.x(pair_g[0])
        builder.free(pair_d)
        builder.free(pair_g)
        if in_place:
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
            append_sample_eraser(
                builder, payload, rank1, branches, spare_rank_bit, pivot, ar
            )

    if in_place:
        builder.free(ratio_temp)
    rank_register = rank1 + branches + [spare_rank_bit]
    circuit = builder.finish_circuit()
    return km, circuit, {
        "payload": payload,
        "rank1": rank1,
        "branches": branches,
        "spare_rank_bit": spare_rank_bit,
        "rank_register": rank_register,
        "ratios": ratios,
        "samples": samples,
    }


def build_inplace_prefix_encoder():
    return build_prefix_encoder(in_place=True)


def screen_prefix_encoder(case_count=32, in_place=False):
    km, circuit, registers = build_prefix_encoder(in_place=in_place)
    field = km.GF2Field(FIELD_BITS)
    rng = Random(0xF1A05304)
    cases = [
        (0, 0, 0, 0)
        if index == 0
        else tuple(rng.randrange(1 << FIELD_BITS) for _ in POINTS)
        for index in range(case_count)
    ]
    labels = [replayed_ratios(data, field) for data in cases]
    if in_place:
        word_values = [
            [rng.randrange(1 << FIELD_BITS) for _ in cases]
            for _ in range(70)
        ]
        for index, data in enumerate(cases):
            for pivot, value in enumerate(data):
                word_values[pivot][index] = value
        untouched_start = 4
    else:
        word_values = [[0] * len(cases) for _ in range(70)]
        for index, data in enumerate(cases):
            for pivot, value in enumerate(data):
                word_values[4 + pivot][index] = value
            for word in range(8, 70):
                word_values[word][index] = rng.randrange(1 << FIELD_BITS)
        untouched_start = 8

    sim = km.Simulator(batch_size=len(cases), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    for word in range(70):
        sim.write_across_shots(
            registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS],
            bit_columns(word_values[word], FIELD_BITS),
        )
    rank_values = [rank1_after(branches) for _, branches in labels]
    sim.write_across_shots(
        registers["rank1"], bit_columns([0] * len(cases), 3)
    )
    for pivot in range(4):
        sim.write_across_shots(
            registers["branches"][pivot],
            np.zeros(len(cases), dtype=np.bool_),
        )
    sim.write_across_shots(
        registers["spare_rank_bit"], np.zeros(len(cases), dtype=np.bool_)
    )
    sim.do(circuit)

    for pivot in range(4):
        assert np.array_equal(
            sim.read_across_shots(registers["ratios"][pivot]),
            bit_columns([ratios[pivot] for ratios, _ in labels], FIELD_BITS),
        )
        if not in_place:
            assert not np.any(sim.read_across_shots(registers["samples"][pivot]))
        assert np.array_equal(
            sim.read_across_shots(registers["branches"][pivot]),
            np.asarray([bool(branches[pivot]) for _, branches in labels], dtype=np.bool_),
        )
    for word in range(untouched_start, 70):
        assert np.array_equal(
            sim.read_across_shots(
                registers["payload"][word * FIELD_BITS : (word + 1) * FIELD_BITS]
            ),
            bit_columns(word_values[word], FIELD_BITS),
        )
    assert np.array_equal(
        sim.read_across_shots(registers["rank1"]),
        bit_columns(rank_values, 3),
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
        "cases": len(cases),
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": circuit.operation_statistics().num_toffoli_like,
        "clean_scratch_qubits": len(scratch),
        "ratios_match_reference": True,
        "branch_history_matches_reference": True,
        "original_ratio_words_overwritten_in_place": in_place,
        "samples_cleared": not in_place,
        "other_payload_preserved": True,
        "phase_flips": 0,
    }


def screen_inplace_prefix_encoder(case_count=32):
    return screen_prefix_encoder(case_count, in_place=True)


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
    if sample is None:
        sample = payload[(4 + pivot) * FIELD_BITS : (5 + pivot) * FIELD_BITS]
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
    return {
        "experiment": "exp-053-inplace-ratio-history-prefix-encoder",
        "result": "PASS",
        "clean_slot_prefix_encoder": clean_slot_result,
        "full_input_inplace_prefix_encoder": inplace_result,
        "scope": (
            "Compiled both four-pivot encoders for 32 arbitrary GF(2^12) "
            "four-sample inputs. The in-place variant accepts arbitrary values "
            "in all 70 payload words, writes ratios into the original first four "
            "sample words, and checks preservation of the other 66 words, branch "
            "history, phase, and scratch. It does not establish the complete "
            "4+66 schedule."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
