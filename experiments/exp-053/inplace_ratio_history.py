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
    ratios = [payload[index * FIELD_BITS : (index + 1) * FIELD_BITS]
              for index in range(pivot + 1)]
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
    results = [screen_pivot(pivot) for pivot in range(4)]
    return {
        "experiment": "exp-053-inplace-ratio-history-decoder",
        "result": "PASS",
        "pivots": results,
        "scope": (
            "Compiled decoder/eraser for each four-point pivot. It verifies the reverse map and clean "
            "workspace; it does not compute the ratio/history labels or establish the full 4+66 schedule."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
