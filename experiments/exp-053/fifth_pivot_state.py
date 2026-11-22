"""Screen branch-history compression after five normalized FMA pivots."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-053"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))

import normalized_fma as nf
import fma_state_compression as fma


def low_row_key(basis, multiply, modulus, degree):
    return tuple(
        tuple(poly)
        for poly in nf.normalized_low_row(basis, multiply, modulus, degree)
    )


def history_graph_coloring(edges):
    adjacency = defaultdict(set)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    colors = {}
    for start in adjacency:
        if start in colors:
            continue
        colors[start] = 0
        pending = [start]
        while pending:
            current = pending.pop()
            for neighbor in adjacency[current]:
                if neighbor not in colors:
                    colors[neighbor] = 1 - colors[current]
                    pending.append(neighbor)
                elif colors[neighbor] == colors[current]:
                    return None
    return colors


def history_tag(history):
    return ((history >> 1) & 1) & (1 - ((history >> 4) & 1))


def ranks_for_history(history, point_count):
    rank1, rank2 = 0, 1
    for pivot in range(point_count):
        if (history >> pivot) & 1:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2
    return rank1, rank2


def histories_for_rank_tag(ranks, tag, point_count):
    return tuple(
        history
        for history in range(1 << point_count)
        if ranks_for_history(history, point_count) == ranks
        and history_tag(history) == tag
    )


def rank_tag_candidate_summary(point_count):
    counts = defaultdict(int)
    for history in range(1 << point_count):
        signature = (ranks_for_history(history, point_count), history_tag(history))
        counts[signature] += 1
    distribution = defaultdict(int)
    for candidate_count in counts.values():
        distribution[candidate_count] += 1
    return {
        "signatures": len(counts),
        "max_histories_per_signature": max(counts.values()),
        "candidate_count_distribution": {
            str(size): distribution[size] for size in sorted(distribution)
        },
    }


def basis_for_history(ratios, history, points, multiply):
    basis = [[[1], [0]], [[0], [1]]]
    rank1, rank2 = 0, 1
    for pivot, point in enumerate(points):
        ratio = ratios[pivot]
        if (history >> pivot) & 1:
            step = [[[ratio], [1]], [[point, 1], [0]]]
            rank1, rank2 = rank2, rank1 + 2
        else:
            step = [[[1], [ratio]], [[0], [point, 1]]]
            rank2 += 2
        basis = fma.matrix_mul(step, basis, multiply)
    return basis, (rank1, rank2)


def decode_compact_state(ratios, low_row, ranks, tag, points, multiply, modulus, degree):
    """Recover samples by searching the 32 possible five-pivot histories."""
    if len(points) != 5:
        raise ValueError("the compact tag decoder is defined for five pivots")

    matches = []
    for history in histories_for_rank_tag(ranks, tag, len(points)):
        basis, candidate_ranks = basis_for_history(
            ratios, history, points, multiply
        )
        assert candidate_ranks == ranks
        if low_row_key(basis, multiply, modulus, degree) == low_row:
            branches = tuple(bool(history >> pivot & 1) for pivot in range(len(points)))
            try:
                samples = nf.decode_replayed_samples(
                    ratios, branches, points, modulus, degree
                )
            except ValueError:
                continue
            state = nf.normalized_state(
                samples, points, multiply, modulus, degree
            )
            if (
                state[2] == history
                and state[5] == ratios
                and state[6] == ranks
                and low_row_key(state[4], multiply, modulus, degree) == low_row
            ):
                matches.append((history, samples))

    if len(matches) != 1:
        raise ValueError(f"compact state has {len(matches)} matching histories")
    return matches[0]


def screen_gf8():
    degree, modulus = 3, 0b1011
    points = tuple(range(5))
    multiply = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    fibers = defaultdict(set)
    max_rank1 = 0
    for data in product(range(1 << degree), repeat=len(points)):
        result = nf.normalized_state(data, points, multiply, modulus, degree)
        history, basis, ratios, ranks = result[2], result[4], result[5], result[6]
        max_rank1 = max(max_rank1, ranks[0])
        key = (ratios, low_row_key(basis, multiply, modulus, degree), ranks)
        fibers[key].add((data, history))

    ambiguous = []
    conflict_edges = set()
    for inputs in fibers.values():
        histories = {history for _, history in inputs}
        if len(histories) > 1:
            ambiguous.append(inputs)
            conflict_edges.update(
                tuple(sorted(pair)) for pair in combinations(histories, 2)
            )
    history_colors = history_graph_coloring(conflict_edges)
    tagged_fibers = defaultdict(set)
    decoder_cases = 0
    for key, inputs in fibers.items():
        for data, history in inputs:
            tag = history_tag(history)
            tagged_fibers[(key, tag)].add(data)
        if len(inputs) > 1:
            ratios, low_row, ranks = key
            for data, history in inputs:
                decoded_history, decoded_data = decode_compact_state(
                    ratios,
                    low_row,
                    ranks,
                    history_tag(history),
                    points,
                    multiply,
                    modulus,
                    degree,
                )
                assert decoded_history == history
                assert decoded_data == data
                decoder_cases += 1

    single_branch_bits = [
        bit
        for bit in range(5)
        if all(
            len({(history >> bit) & 1 for _, history in inputs}) == len(
                {history for _, history in inputs}
            )
            for inputs in ambiguous
        )
    ]
    single_parities = [
        mask
        for mask in range(1, 1 << 5)
        if all(
            len(
                {
                    (history & mask).bit_count() & 1
                    for _, history in inputs
                }
            )
            == len({history for _, history in inputs})
            for inputs in ambiguous
        )
    ]
    return {
        "field": "GF(8)",
        "input_vectors": 8 ** 5,
        "compact_state_labels": len(fibers),
        "collision_groups": sum(len(inputs) > 1 for inputs in fibers.values()),
        "max_inputs_per_label": max(map(len, fibers.values())),
        "max_rank1_after_five_pivots": max_rank1,
        "rank1_bits_observed": max_rank1.bit_length(),
        "rank_plus_one_tag_bits": max_rank1.bit_length() + 1,
        "existing_rank_history_register_bits": 8,
        "rank_tag_candidate_bound": rank_tag_candidate_summary(len(points)),
        "ambiguous_history_groups": len(ambiguous),
        "history_conflict_edges": len(conflict_edges),
        "history_graph_bipartite": history_colors is not None,
        "classical_inverse_cases": decoder_cases,
        "classical_inverse_pass": decoder_cases == 92,
        "one_bit_history_tag": "branch[1] AND NOT branch[4] (zero-based pivots)",
        "single_branch_bits_that_resolve_all": single_branch_bits,
        "single_fixed_parity_masks_that_resolve_all": [
            format(mask, "05b") for mask in single_parities
        ],
        "labels_after_one_history_tag": len(tagged_fibers),
        "collisions_after_one_history_tag": sum(
            len(inputs) > 1 for inputs in tagged_fibers.values()
        ),
        "max_inputs_after_one_history_tag": max(
            map(len, tagged_fibers.values())
        ),
        "scope": "Exhaustive classical information check over all five-word GF(8) inputs.",
    }


def first_five_samples(syndrome, points, multiply):
    node = [1]
    for point in points:
        node = fma.poly_mul(node, [point, 1], multiply)

    samples = []
    for point in points[:5]:
        quotient = [0] * len(points)
        quotient[-1] = node[-1]
        for index in range(len(points) - 2, -1, -1):
            quotient[index] = node[index + 1] ^ multiply(
                point, quotient[index + 1]
            )
        value = 0
        for coefficient, syndrome_value in zip(quotient, syndrome):
            value ^= multiply(coefficient, syndrome_value)
        samples.append(value)
    return tuple(samples)


def screen_gf12_dqi_samples(per_weight=32):
    degree, modulus = 12, 0x1053
    points = tuple(range(70))
    multiply = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    rng = Random(0x5A7E5)
    results = {}

    for weight in (31, 35):
        fibers = defaultdict(set)
        decoder_cases = 0
        for sample_index in range(per_weight):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(points)
            for beta, magnitude in zip(locations, magnitudes):
                power = beta
                for index in range(len(points)):
                    syndrome[index] ^= multiply(magnitude, power)
                    power = multiply(power, beta)

            data = first_five_samples(syndrome, points, multiply)
            if sample_index == 0:
                reference = fma.syndrome_to_fma_samples(
                    syndrome, points, multiply
                )[:5]
                assert data == tuple(reference)

            state = nf.normalized_state(
                data, points[:5], multiply, modulus, degree
            )
            key = (
                state[5],
                low_row_key(state[4], multiply, modulus, degree),
                state[6],
            )
            fibers[key].add((data, state[2]))
            decoded_history, decoded_data = decode_compact_state(
                key[0],
                key[1],
                key[2],
                history_tag(state[2]),
                points[:5],
                multiply,
                modulus,
                degree,
            )
            assert decoded_history == state[2]
            assert decoded_data == data
            decoder_cases += 1

        results[str(weight)] = {
            "samples": per_weight,
            "classical_inverse_cases": decoder_cases,
            "classical_inverse_pass": decoder_cases == per_weight,
            "distinct_compact_states": len(fibers),
            "noninjective_state_keys": sum(
                len(inputs) > 1 for inputs in fibers.values()
            ),
            "ambiguous_history_keys": sum(
                len({history for _, history in inputs}) > 1
                for inputs in fibers.values()
            ),
        }

    return {
        "field": "GF(2^12)",
        "seed": "0x5A7E5",
        "per_weight": results,
        "scope": (
            "64 sampled valid error patterns at weights 31 and 35; "
            "compatibility evidence only, not a full-domain proof."
        ),
    }


def run_screen():
    gf8 = screen_gf8()
    assert gf8["input_vectors"] == 32768
    assert gf8["collision_groups"] == 46
    assert gf8["max_inputs_per_label"] == 2
    assert gf8["history_graph_bipartite"]
    assert gf8["single_branch_bits_that_resolve_all"] == []
    assert gf8["single_fixed_parity_masks_that_resolve_all"] == []
    assert gf8["labels_after_one_history_tag"] == 32768
    assert gf8["collisions_after_one_history_tag"] == 0
    assert gf8["classical_inverse_pass"]
    assert gf8["classical_inverse_cases"] == 92
    assert gf8["rank_tag_candidate_bound"] == {
        "signatures": 14,
        "max_histories_per_signature": 4,
        "candidate_count_distribution": {"1": 4, "2": 6, "4": 4},
    }
    return {
        "experiment": "exp-053-fifth-pivot-state",
        "gf8_exhaustive": gf8,
        "gf12_dqi_sample": screen_gf12_dqi_samples(),
        "decision": (
            "The one-bit tag resolves the GF(8) compact-state collisions, and "
            "the final ranks plus tag reduce 32 histories to at most four "
            "candidates. A classical five-pivot inverse decodes all collision "
            "cases plus the sampled GF(2^12) cases. This remains classical "
            "evidence; no reversible eraser, resource schedule, or official "
            "verifier result is established."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_screen(), indent=2, sort_keys=True))
