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


def zero_tree(b, word):
    for bit in word:
        b.x(bit)
    chain = b.alloc_qubits(len(word) - 1)
    b.ccx(word[0], word[1], chain[0])
    for index in range(2, len(word)):
        b.ccx(chain[index - 2], word[index], chain[index - 1])
    return chain


def undo_zero_tree(b, word, chain):
    for index in reversed(range(len(chain))):
        left = word[0] if index == 0 else chain[index - 1]
        right = word[index + 1]
        b.ccx(left, right, chain[index])
        b.free(chain[index])
    for bit in word:
        b.x(bit)


def compare_borrow_chain(b, left, right, borrows, eq, undo=False):
    if not undo:
        b.x(left[0])
        b.ccx(left[0], right[0], borrows[0])
        b.x(left[0])
        for index in range(1, len(left)):
            b.x(eq)
            b.cx(left[index], eq)
            b.cx(right[index], eq)  # eq = not (left[index] xor right[index])
            b.x(left[index])
            b.ccx(left[index], right[index], borrows[index])
            b.x(left[index])
            b.ccx(eq, borrows[index - 1], borrows[index])
            b.cx(right[index], eq)
            b.cx(left[index], eq)
            b.x(eq)
    else:
        for index in reversed(range(1, len(left))):
            b.x(eq)
            b.cx(left[index], eq)
            b.cx(right[index], eq)
            b.ccx(eq, borrows[index - 1], borrows[index])
            b.x(left[index])
            b.ccx(left[index], right[index], borrows[index])
            b.x(left[index])
            b.cx(right[index], eq)
            b.cx(left[index], eq)
            b.x(eq)
        b.x(left[0])
        b.ccx(left[0], right[0], borrows[0])
        b.x(left[0])


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


def build_one_step():
    b = km.CircuitBuilder()
    d = b.alloc_qubits(FIELD_BITS)
    g = b.alloc_qubits(FIELD_BITS)
    rank1 = b.alloc_qubits(RANK_BITS)
    rank2 = b.alloc_qubits(RANK_BITS)
    branch = b.alloc_qubits(1)[0]

    d_zero = zero_tree(b, d)
    g_zero = zero_tree(b, g)
    borrows = b.alloc_qubits(RANK_BITS)
    eq = b.alloc_qubits(1)[0]
    compare_borrow_chain(b, rank1, rank2, borrows, eq)

    temp = b.alloc_qubits(1)[0]
    b.x(d_zero[-1])
    b.ccx(d_zero[-1], borrows[-1], temp)
    b.x(d_zero[-1])
    b.cx(g_zero[-1], branch)
    b.cx(temp, branch)
    b.ccx(g_zero[-1], temp, branch)  # OR correction when both terms are true
    b.x(d_zero[-1])
    b.ccx(d_zero[-1], borrows[-1], temp)
    b.x(d_zero[-1])
    b.free(temp)

    compare_borrow_chain(b, rank1, rank2, borrows, eq, undo=True)
    b.free(borrows)
    b.free(eq)
    undo_zero_tree(b, g, g_zero)
    undo_zero_tree(b, d, d_zero)

    controlled_rank_update(b, rank1, rank2, branch)

    # Algorithm 6's leaf matrix puts the same fixed nonzero polynomial in one
    # lower-row column or the other. The selector compactly represents that
    # sparse row; the point-dependent polynomial itself is a fixed template.
    selector_register = b.alloc_qubits(1)
    selector = selector_register[0]
    b.cx(branch, selector)
    b.cx(selector, branch)
    b.free(branch)

    return b.finish_circuit(), {
        "d": d,
        "g": g,
        "rank1": rank1,
        "rank2": rank2,
        "leaf_selector": selector_register,
    }


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
    result["compiled_kernel_checks"] = compiled_checks
    print(json.dumps(result, indent=2, sort_keys=True))
