"""Screen classical recovery work for a compact four-point FMA state.

This counts field-arithmetic calls in the existing classical reconstruction
path over every GF(8) four-sample input. The GF(2^12) Toffoli figure is an
arithmetic-only proxy; it is not a compiled reversible circuit or a bound on
workspace, control, phase, or cleanup costs.
"""

from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
sys.path.insert(0, str(ROOT / "experiments" / "exp-052"))
import fma_state_compression as fma  # noqa: E402
from fma_locator_history import recover_factorized_samples  # noqa: E402


def screen() -> dict[str, object]:
    degree, modulus = 3, 0b1011
    points = list(range(4))
    original_mul = fma.gf_mul
    original_inv = fma.gf_inv
    inverse_body = original_inv.__wrapped__
    counts = {"field_multiply_calls": 0, "inverse_calls": 0}

    def counted_mul(left: int, right: int, mod: int, bits: int) -> int:
        counts["field_multiply_calls"] += 1
        return original_mul(left, right, mod, bits)

    def counted_inv(value: int, mod: int, bits: int) -> int:
        counts["inverse_calls"] += 1
        current_mul = fma.gf_mul
        fma.gf_mul = original_mul
        try:
            return inverse_body(value, mod, bits)
        finally:
            fma.gf_mul = current_mul

    fma.gf_mul = counted_mul
    fma.gf_inv = counted_inv
    mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
    records = []
    max_basis_words = 0
    max_basis_example = None
    try:
        for data in product(range(1 << degree), repeat=len(points)):
            basis = fma.modular_basis(data, points, mul)
            basis_lengths = [
                [len(fma.trim(list(poly))) for poly in row] for row in basis
            ]
            basis_words = sum(map(sum, basis_lengths))
            if basis_words > max_basis_words:
                max_basis_words = basis_words
                max_basis_example = {
                    "input": list(data),
                    "row_polynomial_lengths": basis_lengths,
                }
            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            low_index = min(range(2), key=lambda i: fma.row_rank(basis, i))
            row = [fma.trim(list(poly)) for poly in basis[low_index]]
            pivot = row[0][-1] if row[0] != [0] else row[1][-1]
            scale = fma.gf_inv(pivot, modulus, degree)
            row = tuple(
                tuple(fma.trim([mul(scale, value) for value in poly]))
                for poly in row
            )
            normalize_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            common, _, _ = fma.poly_xgcd(row[0], row[1], mul, modulus, degree)
            cofactor_w, remainder = fma.poly_divmod(
                row[0], common, mul, modulus, degree
            )
            assert remainder == [0]
            cofactor_n, remainder = fma.poly_divmod(
                row[1], common, mul, modulus, degree
            )
            assert remainder == [0]
            root_samples = tuple(
                data[index]
                for index, point in enumerate(points)
                if fma.poly_eval(common, point, mul) == 0
            )
            factorize_operations = dict(counts)
            factorized_words = (
                len(common) - 1
                + (0 if cofactor_w == [0] else len(cofactor_w) - int(cofactor_w[-1] == 1))
                + (0 if cofactor_n == [0] else len(cofactor_n))
                + len(root_samples)
            )
            assert factorized_words <= len(points)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            recovered = recover_factorized_samples(
                common,
                cofactor_w,
                cofactor_n,
                root_samples,
                points,
                mul,
                modulus,
                degree,
            )
            decode_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            low = (
                fma.poly_mul(common, cofactor_w, mul),
                fma.poly_mul(common, cofactor_n, mul),
            )
            row_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            got_low, complement, _ = fma.reconstruct_complementary_row(
                low, recovered, points, mul, modulus, degree
            )
            complement_operations = dict(counts)

            counts["field_multiply_calls"] = 0
            counts["inverse_calls"] = 0
            history = fma.sequential_state(recovered, points, mul)[2]
            branch_operations = dict(counts)
            compact_state_stages = {
                "normalize_low_row": normalize_operations,
                "factorize_low_row": factorize_operations,
                "recover_samples": decode_operations,
                "replay_branch_history": branch_operations,
            }
            compact_state_component_t = {
                name: stage["field_multiply_calls"] * 42
                + stage["inverse_calls"] * 138
                for name, stage in compact_state_stages.items()
            }
            compact_state_proxy_t = sum(compact_state_component_t.values())
            operations = {
                key: sum(
                    stage[key]
                    for stage in (
                        decode_operations,
                        row_operations,
                        complement_operations,
                        branch_operations,
                    )
                )
                for key in counts
            }
            components = {
                "decode_samples": decode_operations,
                "compose_low_row": row_operations,
                "reconstruct_complement": complement_operations,
                "replay_branch_history": branch_operations,
            }
            component_t = {
                name: stage["field_multiply_calls"] * 42
                + stage["inverse_calls"] * 138
                for name, stage in components.items()
            }
            proxy_t = sum(component_t.values())

            assert recovered == list(data)
            assert tuple(tuple(poly) for poly in got_low) == row
            assert history == fma.sequential_state(data, points, mul)[2]
            fma.assert_basis(
                recovered, [1] * len(points), points, [got_low, complement], mul
            )
            ranks = sorted(
                fma.row_rank([got_low, complement], index) for index in range(2)
            )
            assert ranks == sorted(fma.row_rank(basis, index) for index in range(2))
            records.append(
                {
                    "input": list(data),
                    "field_multiply_calls": operations["field_multiply_calls"],
                    "inverse_calls": operations["inverse_calls"],
                    "arithmetic_only_t_proxy": proxy_t,
                    "components": component_t,
                    "factorized_state_words": factorized_words,
                    "compact_history_t_proxy": compact_state_proxy_t,
                    "compact_history_components": compact_state_component_t,
                }
            )
    finally:
        fma.gf_mul = original_mul
        fma.gf_inv = original_inv

    records.sort(key=lambda record: record["arithmetic_only_t_proxy"], reverse=True)
    costs = [record["arithmetic_only_t_proxy"] for record in records]
    compact_history_costs = sorted(
        record["compact_history_t_proxy"] for record in records
    )
    return {
        "field": "GF(8)",
        "four_sample_inputs_checked": len(records),
        "checks": [
            "factorized payload reconstructs all four input samples",
            "reconstructed complementary row satisfies the basis constraints",
            "branch history matches direct replay",
        ],
        "gf12_cost_assumptions": {
            "field_multiply_call_t": 42,
            "inverse_call_t": 138,
        },
        "maximum": records[0],
        "materialized_basis": {
            "maximum_coefficient_words": max_basis_words,
            "example": max_basis_example,
            "extra_qubits_over_four_sample_words": (max_basis_words - 4) * 12,
            "projected_payload_qubits": 840 - 48 + max_basis_words * 12,
            "qubit_limit": 890,
            "over_limit_before_workspace": 840 - 48 + max_basis_words * 12 - 890,
            "scope": "All four-sample GF(8) inputs; direct storage of every polynomial coefficient, without streaming or compression.",
        },
        "maximum_component_arithmetic_only_t_proxy": {
            name: max(record["components"][name] for record in records)
            for name in records[0]["components"]
        },
        "compact_history_round_trip": {
            "description": (
                "Normalize and factor the low row, recover the four samples from "
                "the factorized state, then replay the four-point branch history. "
                "This omits complementary-row reconstruction."
            ),
            "maximum_factorized_state_words": max(
                record["factorized_state_words"] for record in records
            ),
            "maximum_arithmetic_only_t_proxy": max(
                record["compact_history_t_proxy"] for record in records
            ),
            "median_arithmetic_only_t_proxy": compact_history_costs[
                len(compact_history_costs) // 2
            ],
            "maximum_component_t_proxy": {
                name: max(record["compact_history_components"][name] for record in records)
                for name in records[0]["compact_history_components"]
            },
            "scope": (
                "All 4,096 arbitrary GF(8) four-sample inputs. Every counted "
                "multiply call is charged 42T and every inverse 138T, including "
                "constant-coefficient multiplies that can be linear gates. This "
                "is a conservative arithmetic proxy, not a compiled reversible "
                "circuit or full 4+66 schedule."
            ),
        },
        "median_arithmetic_only_t_proxy": costs[len(costs) // 2],
        "scope": (
            "Counts classical arithmetic calls for decode, complementary-row "
            "reconstruction, and four-point branch replay. Every multiply call "
            "is charged 42T, including fixed-coefficient calls. It does not "
            "compile a circuit and excludes control, degree framing, phase, "
            "scratch, and cleanup costs."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2, sort_keys=True))
