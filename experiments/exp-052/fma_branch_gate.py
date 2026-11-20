"""Compile and count one reversible FMA branch/rank leaf.

The retained bit is a sparse leaf-matrix column selector. Recursive composition
and selector cleanup are outside this local count.
"""

from __future__ import annotations

import json

import kickmix as km
import numpy as np


FIELD_BITS = 12
RANK_BITS = 8
POINTS = 70
REMAINING_TOFFOLIS = 9_788


def increment_two(b, word):
    """In-place add 2, using a high-to-low carry cleanup schedule."""
    carries = b.alloc_qubits(len(word) - 3)
    b.ccx(word[1], word[2], carries[0])
    for index in range(1, len(carries)):
        b.ccx(carries[index - 1], word[index + 2], carries[index])

    for target in reversed(range(3, len(word))):
        carry_index = target - 3
        b.cx(carries[carry_index], word[target])
        left = word[1] if carry_index == 0 else carries[carry_index - 1]
        b.ccx(left, word[target - 1], carries[carry_index])
        b.free(carries[carry_index])

    b.cx(word[1], word[2])
    b.x(word[1])


def add_controlled_constant(b, word, constant, control):
    """Add a controlled even constant modulo 2**len(word), reversibly."""
    assert constant % 2 == 0 and len(word) >= 3
    b.iadd(constant, target=word, control=control)


def controlled_reflect_rank(b, rank, step, branch):
    """When branch is set, replace r by (2*step+1-r) modulo 2**8."""
    for bit in rank:
        b.cx(branch, bit)
    add_controlled_constant(b, rank, 2 * (step + 1), branch)


def controlled_rank_update(b, rank1, rank2, branch):
    # Fredkin = CNOT, CCX, CNOT; then always add 2 to the new rank2.
    for left, right in zip(rank1, rank2):
        b.cx(left, right)
        b.ccx(branch, right, left)
        b.cx(left, right)
    increment_two(b, rank2)


def branch_bit(d_value, g_value, rank1, rank2):
    return g_value == 0 or (d_value != 0 and rank1 < rank2)


def rank_step(rank1, rank2, branch):
    if branch:
        return rank2, (rank1 + 2) & 0xFF
    return rank1, (rank2 + 2) & 0xFF


def increment_two_value(value):
    bits = [(value >> index) & 1 for index in range(RANK_BITS)]
    carries = [0] * (RANK_BITS - 3)
    carries[0] = bits[1] & bits[2]
    for index in range(1, len(carries)):
        carries[index] = carries[index - 1] & bits[index + 2]

    for target in reversed(range(3, RANK_BITS)):
        carry_index = target - 3
        bits[target] ^= carries[carry_index]
        left = bits[1] if carry_index == 0 else carries[carry_index - 1]
        carries[carry_index] ^= left & bits[target - 1]

    bits[2] ^= bits[1]
    bits[1] ^= 1
    assert not any(carries)
    return sum(bit << index for index, bit in enumerate(bits))


def check_small_logic():
    for value in range(1 << RANK_BITS):
        assert increment_two_value(value) == (value + 2) & 0xFF

    for left in range(1 << RANK_BITS):
        for right in range(1 << RANK_BITS):
            borrow = 0
            for index in range(RANK_BITS):
                a, b = (left >> index) & 1, (right >> index) & 1
                equal = int(a == b)
                borrow = ((1 - a) & b) ^ (equal & borrow)
            assert borrow == int(left < right)

            for branch in (False, True):
                out = rank_step(left, right, branch)
                expected = (
                    (right, (left + 2) & 0xFF)
                    if branch
                    else (left, (right + 2) & 0xFF)
                )
                assert out == expected

    for d_nonzero in (False, True):
        for g_nonzero in (False, True):
            for left in range(1 << RANK_BITS):
                for right in range(1 << RANK_BITS):
                    assert branch_bit(
                        int(d_nonzero), int(g_nonzero), left, right
                    ) == (
                        not g_nonzero
                        or (d_nonzero and left < right)
                    )


def bit_columns(values, width):
    return np.stack(
        [((values >> index) & 1).astype(np.bool_) for index in range(width)]
    )


def check_compiled_kernel():
    circuit, regs = build_one_step()
    pairs = np.arange(1 << (2 * RANK_BITS), dtype=np.uint32)
    rank1 = np.tile(pairs >> RANK_BITS, 4)
    rank2 = np.tile(pairs & ((1 << RANK_BITS) - 1), 4)
    zero_class = np.repeat(np.arange(4, dtype=np.uint8), len(pairs))
    d_nonzero = (zero_class >> 1).astype(np.uint32)
    g_nonzero = (zero_class & 1).astype(np.uint32)
    branch = (g_nonzero == 0) | ((d_nonzero != 0) & (rank1 < rank2))
    expected_rank1 = np.where(branch, rank2, rank1)
    expected_rank2 = np.where(
        branch,
        (rank1 + 2) & ((1 << RANK_BITS) - 1),
        (rank2 + 2) & ((1 << RANK_BITS) - 1),
    )

    sim = km.Simulator(batch_size=len(rank1), debug_print=False, seed=0)
    sim.use_same_registers_as(circuit)
    d_bits = bit_columns(d_nonzero, FIELD_BITS)
    g_bits = bit_columns(g_nonzero, FIELD_BITS)
    rank1_bits = bit_columns(rank1, RANK_BITS)
    rank2_bits = bit_columns(rank2, RANK_BITS)
    sim.write_across_shots(regs["d"], d_bits)
    sim.write_across_shots(regs["g"], g_bits)
    sim.write_across_shots(regs["rank1"], rank1_bits)
    sim.write_across_shots(regs["rank2"], rank2_bits)
    sim.do(circuit)

    assert np.array_equal(sim.read_across_shots(regs["d"]), d_bits)
    assert np.array_equal(sim.read_across_shots(regs["g"]), g_bits)
    assert np.array_equal(
        sim.read_across_shots(regs["rank1"]),
        bit_columns(expected_rank1, RANK_BITS),
    )
    assert np.array_equal(
        sim.read_across_shots(regs["rank2"]),
        bit_columns(expected_rank2, RANK_BITS),
    )
    assert np.array_equal(
        sim.read_across_shots(regs["leaf_selector"])[0], branch
    )
    assert not np.any(sim.read_phase_flipped_across_shots())
    output_qubits = (
        list(regs["d"])
        + list(regs["g"])
        + list(regs["rank1"])
        + list(regs["rank2"])
        + list(regs["leaf_selector"])
    )
    outputs = set(output_qubits)
    scratch = [
        km.q(index)
        for index in range(circuit.num_qubits)
        if km.q(index) not in outputs
    ]
    if scratch:
        assert not np.any(sim.read_across_shots(km.array(scratch)))
    return {
        "rank_pairs_per_zero_class": len(pairs),
        "pivot_zero_classes": 4,
        "truth_table_cases": len(rank1),
        "clean_scratch_qubits": len(scratch),
        "phase_flips": 0,
    }


def check_constant_rank_steps():
    total_cases = 0
    total_toffolis = 0
    max_qubits = 0
    scratch_qubits = set()
    step_costs = []

    for step in range(POINTS):
        circuit, regs = build_one_step(step)
        rank1_values = np.arange(2 * step + 2, dtype=np.uint32)
        rank1 = np.tile(rank1_values, 4)
        rank2 = np.tile(2 * step + 1 - rank1_values, 4)
        zero_class = np.repeat(np.arange(4, dtype=np.uint8), len(rank1_values))
        d_nonzero = (zero_class >> 1).astype(np.uint32)
        g_nonzero = (zero_class & 1).astype(np.uint32)
        branch = (g_nonzero == 0) | ((d_nonzero != 0) & (rank1 <= step))
        expected_rank1 = np.where(branch, rank2, rank1)

        sim = km.Simulator(batch_size=len(rank1), debug_print=False, seed=step)
        sim.use_same_registers_as(circuit)
        d_bits = bit_columns(d_nonzero, FIELD_BITS)
        g_bits = bit_columns(g_nonzero, FIELD_BITS)
        rank1_bits = bit_columns(rank1, RANK_BITS)
        sim.write_across_shots(regs["d"], d_bits)
        sim.write_across_shots(regs["g"], g_bits)
        sim.write_across_shots(regs["rank1"], rank1_bits)
        sim.do(circuit)

        assert np.array_equal(sim.read_across_shots(regs["d"]), d_bits)
        assert np.array_equal(sim.read_across_shots(regs["g"]), g_bits)
        assert np.array_equal(
            sim.read_across_shots(regs["rank1"]),
            bit_columns(expected_rank1, RANK_BITS),
        )
        assert np.array_equal(
            sim.read_across_shots(regs["leaf_selector"])[0], branch
        )
        assert not np.any(sim.read_phase_flipped_across_shots())

        output_qubits = (
            list(regs["d"])
            + list(regs["g"])
            + list(regs["rank1"])
            + list(regs["leaf_selector"])
        )
        outputs = set(output_qubits)
        scratch = [
            km.q(index)
            for index in range(circuit.num_qubits)
            if km.q(index) not in outputs
        ]
        if scratch:
            assert not np.any(sim.read_across_shots(km.array(scratch)))
        scratch_qubits.add(len(scratch))

        total_cases += len(rank1)
        total_toffolis += circuit.operation_statistics().num_toffoli_like
        max_qubits = max(max_qubits, circuit.num_qubits)
        step_costs.append(circuit.operation_statistics().num_toffoli_like)

    return {
        "steps": POINTS,
        "valid_rank_zero_class_cases": total_cases,
        "total_toffoli_like_gates": total_toffolis,
        "remaining_from_9788T_after_constant_rank_steps": (
            REMAINING_TOFFOLIS - total_toffolis
        ),
        "toffolis_saved_vs_dynamic_two_register": (
            POINTS * compile_one_step()["toffoli_like_gates"] - total_toffolis
        ),
        "max_qubits_for_one_step": max_qubits,
        "projected_total_qubits_if_pivot_pair_is_inside_840q_payload": (
            840 + max_qubits - 2 * FIELD_BITS
        ),
        "scratch_qubits_per_step": sorted(scratch_qubits),
        "step_toffoli_counts": step_costs,
        "phase_flips": 0,
        "rank_register_qubits": RANK_BITS,
        "scope": (
            "All valid rank pairs r1+r2=2j+1 and all four d/g zero classes "
            "for j=0..69. Only r1 is retained; r2 is derived, and the rank "
            "update reflects r1 to 2j+1-r1 on the swap branch."
        ),
    }


def build_one_step(step=None):
    b = km.CircuitBuilder()
    d = b.alloc_qubits(FIELD_BITS)
    g = b.alloc_qubits(FIELD_BITS)
    rank1 = b.alloc_qubits(RANK_BITS)
    rank2 = b.alloc_qubits(RANK_BITS) if step is None else None
    branch_register = b.alloc_qubits(1)
    branch = branch_register[0]
    d_zero = b.alloc_qubits(1)[0]
    g_zero = b.alloc_qubits(1)[0]
    term = b.alloc_qubits(1)[0]

    # Keep only the two zero flags and one controlled comparison result live.
    # Kickmix's exact comparator cleans its internal scratch before returning.
    b.flip_if_less_than(g, 1, target=g_zero)
    b.flip_if_less_than(d, 1, target=d_zero)
    b.x(d_zero)  # d_nonzero
    if step is None:
        b.flip_if_less_than(rank1, rank2, target=term, control=d_zero)
    else:
        b.flip_if_less_than(rank1, step + 1, target=term, control=d_zero)

    # branch = g_zero OR (d_nonzero AND rank_lt)
    b.cx(g_zero, branch)
    b.cx(term, branch)
    b.ccx(g_zero, term, branch)

    if step is None:
        b.flip_if_less_than(rank1, rank2, target=term, control=d_zero)
    else:
        b.flip_if_less_than(rank1, step + 1, target=term, control=d_zero)
    b.x(d_zero)
    b.flip_if_less_than(d, 1, target=d_zero)
    b.flip_if_less_than(g, 1, target=g_zero)
    b.free(term)
    b.free(g_zero)
    b.free(d_zero)

    if step is None:
        controlled_rank_update(b, rank1, rank2, branch)
    else:
        controlled_reflect_rank(b, rank1, step, branch)

    # Algorithm 6's leaf matrix puts the same fixed nonzero polynomial in one
    # lower-row column or the other. The selector compactly represents that
    # sparse row; the point-dependent polynomial itself is a fixed template.
    registers = {
        "d": d,
        "g": g,
        "rank1": rank1,
        "leaf_selector": branch_register,
    }
    if rank2 is not None:
        registers["rank2"] = rank2
    return b.finish_circuit(), registers


def compile_one_step():
    circuit, _ = build_one_step()
    stats = circuit.operation_statistics()
    return {
        "field_bits": FIELD_BITS,
        "rank_bits_each": RANK_BITS,
        "input_pair_and_ranks_qubits": 2 * FIELD_BITS + 2 * RANK_BITS,
        "leaf_matrix_selector_qubits": 1,
        "compiled_qubits": circuit.num_qubits,
        "toffoli_like_gates": stats.num_toffoli_like,
        "toffolis_for_70_branch_steps": POINTS * stats.num_toffoli_like,
        "margin_left_from_9788T": REMAINING_TOFFOLIS
        - POINTS * stats.num_toffoli_like,
        "projected_total_qubits_if_pivot_pair_is_inside_840q_payload": (
            840 + circuit.num_qubits - 2 * FIELD_BITS
        ),
        "scope": (
            "One branch predicate, rank update, and one sparse leaf-matrix "
            "selector only. "
            "Assumes d/g are already live in the 840-qubit payload and the "
            "selector is retained as the leaf matrix output. Excludes the "
            "FMA tree, generation of d/g, selector liveness across recursive "
            "composition, and all other omitted costs."
        ),
    }


if __name__ == "__main__":
    check_small_logic()
    compiled_checks = check_compiled_kernel()
    result = compile_one_step()
    result["experiment"] = "exp-052-fma-branch-gate"
    result["compiled_kernel_checks"] = compiled_checks
    result["constant_rank_invariant"] = check_constant_rank_steps()
    print(json.dumps(result, indent=2, sort_keys=True))
