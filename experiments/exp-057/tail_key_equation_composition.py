"""Classically compose the v15 four-point basis with its 66-symbol FMA tail."""

from __future__ import annotations

from pathlib import Path
from random import Random
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "experiments" / name) for name in ("exp-049", "exp-057")]

import fma_state_compression as fma
import phase_compatibility as phase
import streaming_fixed_shape_decoder as fixed


CASE_COUNT = 32
SEED = 0xA66063
POINTS = tuple(range(70))


def _normalized_low_row(basis, mul, inv):
    row = min(range(2), key=lambda index: fma.row_rank(basis, index))
    denominator, numerator = (fma.trim(list(poly)) for poly in basis[row])
    scale = inv(denominator[-1])
    return tuple(
        fma.trim([mul(scale, value) for value in poly])
        for poly in (denominator, numerator)
    )


def run_screen(case_count: int = CASE_COUNT, seed: int = SEED) -> dict[str, object]:
    if case_count < 2 or case_count % 2:
        raise ValueError("case_count must be a positive even number")

    mul, inv = phase._field_ops()
    div = lambda left, right: mul(left, inv(right)) if right else 0
    sample_node, sample_quotients = phase._node_polynomials(mul)
    rng = Random(seed)
    powers = [1]
    for _ in range(phase.CODE_POSITIONS - 1):
        powers.append(mul(powers[-1], 2))
    if len(set(powers)) != phase.CODE_POSITIONS or mul(powers[-1], 2) != 1:
        raise AssertionError("field element 2 did not enumerate all nonzero roots")

    results = []
    for case_index in range(case_count):
        weight = 31 if case_index < case_count // 2 else 35
        forced_root = (
            (1, 2, 3)[(case_index // 3) % 3] if case_index % 3 == 0 else None
        )

        for _ in range(10000):
            positions = rng.sample(range(phase.CODE_POSITIONS), weight)
            if forced_root is not None:
                forced_position = powers.index(forced_root)
                if forced_position not in positions:
                    positions[-1] = forced_position
            errors = {
                powers[position]: rng.randrange(1, phase.FIELD_SIZE)
                for position in positions
            }
            samples = phase._syndrome_to_samples(errors, sample_quotients, mul)
            try:
                coefficients = fixed.coefficients_from_samples(samples[:4], mul, div)
                if not fixed.valid_shape(coefficients, mul, div):
                    continue
                state, prefix_pivot = fixed.prefix_state_from_coefficients(
                    coefficients, mul, div
                )
                rows, prefix_samples = fixed.complementary_matrix_from_prefix_state(
                    state, mul, div, 0x1053, 12
                )
                if prefix_samples != samples[:4]:
                    continue
            except (AssertionError, ValueError, ZeroDivisionError):
                continue
            break
        else:
            raise RuntimeError(f"could not sample supported prefix for case {case_index}")

        prefix_ranks = tuple(fma.row_rank(rows, row) for row in range(2))
        if sum(prefix_ranks) != 9:
            raise AssertionError("the canonical four-point basis has the wrong rank sum")

        tail_points = POINTS[4:]
        tail_pairs = [
            fixed.apply_matrix(rows, point, (samples[point], 1), mul)
            for point in tail_points
        ]
        tail_basis = fma.modular_basis(
            [pair[0] for pair in tail_pairs],
            tail_points,
            mul,
            [pair[1] for pair in tail_pairs],
        )
        composed = fma.matrix_mul(tail_basis, rows, mul)
        direct = fma.modular_basis(samples, POINTS, mul)

        locator = phase._error_locator(errors, mul)
        evaluator = phase._error_evaluator(locator, sample_node, errors, mul)
        composed_low = _normalized_low_row(composed, mul, inv)
        direct_low = _normalized_low_row(direct, mul, inv)
        if composed_low != direct_low:
            raise AssertionError("composed low row differs from the direct 70-point basis")
        if composed_low != (locator, evaluator):
            raise AssertionError("composed low row differs from the expected key equation")

        results.append(
            {
                "weight": weight,
                "prefix_pivot": prefix_pivot,
                "forced_prefix_error_root": forced_root,
                "prefix_ranks": prefix_ranks,
                "final_ranks": tuple(fma.row_rank(composed, row) for row in range(2)),
            }
        )

    return {
        "experiment": "exp-057-v15-tail-key-equation-composition",
        "status": "PASS",
        "field": "GF(2^12), modulus 0x1053",
        "seed": hex(seed),
        "cases": case_count,
        "weights": {
            str(weight): sum(result["weight"] == weight for result in results)
            for weight in (31, 35)
        },
        "prefix_node_error_roots": {
            str(root): sum(
                result["forced_prefix_error_root"] == root for result in results
            )
            for root in (1, 2, 3)
        },
        "prefix_pivots": {
            str(pivot): sum(result["prefix_pivot"] == pivot for result in results)
            for pivot in sorted({result["prefix_pivot"] for result in results})
        },
        "tail_symbols_per_case": 66,
        "rank_pairs_by_weight": {
            str(weight): {
                "prefix": sorted(
                    {result["prefix_ranks"] for result in results if result["weight"] == weight}
                ),
                "final": sorted(
                    {result["final_ranks"] for result in results if result["weight"] == weight}
                ),
            }
            for weight in (31, 35)
        },
        "normalized_low_rows_match_direct_basis": True,
        "low_rows_match_error_locator_evaluator": True,
        "scope": "Classical finite-field composition only; no reversible circuit, resource count, cleanup, official verifier, or competition submission.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run_screen(), indent=2, sort_keys=True))
