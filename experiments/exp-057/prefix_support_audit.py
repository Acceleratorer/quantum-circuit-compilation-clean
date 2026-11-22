"""Measure four-point prefix support under the official DQI error distribution."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
FIELD_BITS = 12
FIELD_ORDER = (1 << FIELD_BITS) - 1
MODULUS = 0x1053
PREFIX_ORIGINS = tuple(range(0, 68, 4))
SHOTS_PER_SEED = 8192
SEEDS = (20261123, 20261124, 20261125)


def load_local_modules(verifier_dir: Path):
    sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
    sys.path.insert(0, str(verifier_dir))
    import fma_state_compression as fma
    import verify_submission_dqi as verifier

    path = ROOT / "experiments" / "exp-057" / "streaming_prefix_kernel.py"
    spec = importlib.util.spec_from_file_location("exp057_prefix_screen", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return fma, verifier, module


class Field:
    def mul(self, left: int, right: int) -> int:
        return fma_gf_mul(left, right)

    def invert(self, value: int) -> int:
        return fma_gf_inv(value)


fma_gf_mul = None
fma_gf_inv = None


def field_tables(fma):
    global fma_gf_mul, fma_gf_inv
    fma_gf_mul = lambda a, b: fma.gf_mul(int(a), int(b), MODULUS, FIELD_BITS)
    fma_gf_inv = lambda a: fma.gf_inv(int(a), MODULUS, FIELD_BITS)

    exp = np.empty(FIELD_ORDER * 2, dtype=np.uint16)
    log = np.full(1 << FIELD_BITS, -1, dtype=np.int32)
    value = 1
    for index in range(FIELD_ORDER):
        exp[index] = value
        log[value] = index
        value = fma_gf_mul(value, 2)
    if value != 1 or np.count_nonzero(log >= 0) != FIELD_ORDER:
        raise ValueError("GF(2^12) primitive-element table is invalid")
    exp[FIELD_ORDER:] = exp[:FIELD_ORDER]

    def multiply(left, right):
        left, right = np.broadcast_arrays(
            np.asarray(left, dtype=np.uint16),
            np.asarray(right, dtype=np.uint16),
        )
        output = np.zeros(left.shape, dtype=np.uint16)
        nonzero = (left != 0) & (right != 0)
        output[nonzero] = exp[
            (log[left[nonzero]] + log[right[nonzero]]) % FIELD_ORDER
        ]
        return output

    def inverse(values):
        values = np.asarray(values, dtype=np.uint16)
        output = np.zeros(values.shape, dtype=np.uint16)
        nonzero = values != 0
        output[nonzero] = exp[(FIELD_ORDER - log[values[nonzero]]) % FIELD_ORDER]
        return output

    return multiply, inverse


def fma_error_coefficients(multiply, field):
    """Return beta*Q_i(beta), the exact error-to-FMA-sample coefficients."""
    beta = np.arange(1 << FIELD_BITS, dtype=np.uint16)
    points = np.arange(70, dtype=np.uint16)
    node = np.ones(1 << FIELD_BITS, dtype=np.uint16)
    for point in points:
        node = multiply(node, beta ^ point)

    coefficients = np.empty((1 << FIELD_BITS, 70), dtype=np.uint16)
    for index, point in enumerate(points):
        denominator = beta ^ point
        quotient = np.zeros(1 << FIELD_BITS, dtype=np.uint16)
        nonzero = denominator != 0
        quotient[nonzero] = multiply(
            node[nonzero], field.inverse(denominator[nonzero])
        )
        special = 1
        for other in points:
            if other != point:
                special = fma_gf_mul(special, int(point) ^ int(other))
        quotient[int(point)] = special
        coefficients[:, index] = multiply(beta, quotient)
    return coefficients


def check_fma_map(fma, coefficients, multiply):
    locations = np.asarray([1, 17, 233, 2049], dtype=np.uint16)
    magnitudes = np.asarray([5, 19, 43, 777], dtype=np.uint16)
    syndrome = [0] * 70
    for location, magnitude in zip(locations, magnitudes):
        power = int(location)
        for index in range(70):
            syndrome[index] ^= fma_gf_mul(int(magnitude), power)
            power = fma_gf_mul(power, int(location))
    direct = np.bitwise_xor.reduce(
        multiply(magnitudes[:, None], coefficients[locations]), axis=0
    )
    reference = fma.syndrome_to_fma_samples(
        syndrome, range(70), fma_gf_mul
    )
    if tuple(map(int, direct)) != tuple(reference):
        raise AssertionError("the direct error-to-FMA map differs from the reference")


def verifier_samples(coefficients, field, verifier, seed: int):
    probabilities = verifier.optimal_dqi_weights(4095, 35, 12, 2016) ** 2
    rng = np.random.default_rng(seed)
    weights = rng.choice(36, size=SHOTS_PER_SEED, p=probabilities)
    samples = np.zeros((SHOTS_PER_SEED, 70), dtype=np.uint16)
    for shot, weight in enumerate(weights):
        weight = int(weight)
        if weight == 0:
            continue
        locations = rng.choice(FIELD_ORDER, size=weight, replace=False) + 1
        magnitudes = rng.integers(1, 1 << FIELD_BITS, size=weight, dtype=np.uint16)
        samples[shot] = np.bitwise_xor.reduce(
            field.multiply(magnitudes[:, None], coefficients[locations]), axis=0
        )
    return samples, weights, probabilities


def classify_prefix(samples, origin: int, multiply, inverse):
    """Vectorized form of the current four-sample coefficient decoder."""
    d0, d1, d2, d3 = (samples[:, origin + offset] for offset in range(4))
    mul = multiply
    div = lambda numerator, denominator: mul(numerator, inverse(denominator))

    c0 = d2 ^ mul(d1, 2) ^ mul(d0, 3)
    c1 = mul(d2 ^ d1, 2)
    constant = mul(d2, 4) ^ mul(d1, 2)
    pivot0 = c0 != 0
    pivot1 = (~pivot0) & (c1 != 0)
    no_pivot = ~(pivot0 | pivot1)

    alpha = np.where(pivot0, div(constant, c0), div(constant, c1))
    beta = div(c1, c0)
    x2 = mul(np.full(len(samples), 3, dtype=np.uint16), 3)
    denominator0 = np.where(pivot0, x2 ^ alpha, x2 ^ mul(alpha, 3))
    denominator1 = np.where(pivot0, np.uint16(3) ^ beta, np.uint16(1))
    d0d1 = d0 ^ d1
    numerator0 = np.where(
        pivot0,
        mul(d0, alpha) ^ mul(3, d1 ^ mul(d0d1, alpha)),
        mul(3, d1 ^ mul(d1, alpha)),
    )
    numerator1 = np.where(
        pivot0,
        mul(d0, beta) ^ mul(3, mul(d0d1, beta) ^ d1),
        d0 ^ mul(3, d0d1),
    )
    remainder_denominator = numerator1 ^ mul(d3, denominator1)
    remainder_numerator = numerator0 ^ mul(d3, denominator0)
    zero_division = (~no_pivot) & (remainder_denominator == 0)
    remaining = div(remainder_numerator, remainder_denominator)

    a1 = np.where(pivot0, remaining, div(constant, c1))
    a0 = np.where(pivot0, div(constant ^ mul(c1, a1), c0), remaining)
    b0 = mul(d0, a0)
    b1 = d1 ^ mul(d0 ^ d1, a0) ^ mul(d1, a1)
    b1_zero = b1 == 0

    prefix_root = np.zeros(len(samples), dtype=np.bool_)
    for point in range(4):
        prefix_root |= (
            mul(point, point) ^ mul(a1, point) ^ a0
        ) == 0
    root_b = div(b0, b1)
    gcd_failure = (mul(root_b, root_b) ^ mul(a1, root_b) ^ a0) == 0
    unsupported = no_pivot | zero_division | b1_zero | prefix_root | gcd_failure
    return {
        "unsupported": unsupported,
        "no_pivot": no_pivot,
        "zero_division": zero_division,
        "b1_zero": b1_zero,
        "prefix_root": prefix_root,
        "gcd_failure": gcd_failure,
        "pivot0": pivot0,
        "pivot1": pivot1,
    }


def scalar_crosscheck(samples, origin, expected, kernel, field):
    for shot in range(min(40, len(samples))):
        prefix = tuple(map(int, samples[shot, origin : origin + 4]))
        try:
            coefficients = kernel.coefficients_from_four_samples(prefix, field)
            supported = kernel.coefficients_have_supported_shape(coefficients, field)
        except (ValueError, ZeroDivisionError):
            supported = False
        if supported == bool(expected[shot]):
            raise AssertionError(f"scalar/vector mismatch at origin={origin}, shot={shot}")


def run_seed(seed, coefficients, field, verifier, kernel):
    samples, weights, probabilities = verifier_samples(
        coefficients, field, verifier, seed
    )
    results = []
    for origin in PREFIX_ORIGINS:
        classes = classify_prefix(samples, origin, field.multiply, field.inverse)
        scalar_crosscheck(samples, origin, classes["unsupported"], kernel, Field())
        results.append(
            {
                "prefix_origin": origin,
                "unsupported": int(classes["unsupported"].sum()),
                "unsupported_by_reason": {
                    name: int(classes[name].sum())
                    for name in ("no_pivot", "zero_division", "b1_zero", "prefix_root", "gcd_failure")
                },
                "pivot_counts": {
                    "a0": int(classes["pivot0"].sum()),
                    "a1": int(classes["pivot1"].sum()),
                },
                "empirical_rate": float(classes["unsupported"].mean()),
                "plug_in_repetition_overhead": verifier.repetition_overhead(
                    float(classes["unsupported"].mean())
                ),
            }
        )
    return {
        "seed": seed,
        "shots": len(weights),
        "weight_counts": {
            str(weight): int(np.count_nonzero(weights == weight))
            for weight in range(36)
            if np.any(weights == weight)
        },
        "probability_mass_weights_29_35": float(probabilities[29:36].sum()),
        "prefix_origins": results,
        "best_origin": min(results, key=lambda result: result["unsupported"])["prefix_origin"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verifier-dir",
        type=Path,
        default=ROOT.parent / "official_dqi_source" / "verifiers" / "dqi",
    )
    args = parser.parse_args()
    fma, verifier, kernel = load_local_modules(args.verifier_dir.resolve())
    field = type(
        "GF12",
        (),
        {
            "mul": staticmethod(lambda a, b: fma.gf_mul(int(a), int(b), MODULUS, FIELD_BITS)),
            "invert": staticmethod(lambda a: fma.gf_inv(int(a), MODULUS, FIELD_BITS)),
        },
    )()
    multiply, inverse = field_tables(fma)
    field.multiply, field.inverse = multiply, inverse
    coefficients = fma_error_coefficients(multiply, field)
    check_fma_map(fma, coefficients, multiply)
    seed_results = [
        run_seed(seed, coefficients, field, verifier, kernel) for seed in SEEDS
    ]
    total_shots = SHOTS_PER_SEED * len(SEEDS)
    aggregated_origins = []
    for origin in PREFIX_ORIGINS:
        rows = [
            next(
                row
                for row in seed_result["prefix_origins"]
                if row["prefix_origin"] == origin
            )
            for seed_result in seed_results
        ]
        unsupported = sum(row["unsupported"] for row in rows)
        aggregated_origins.append(
            {
                "prefix_origin": origin,
                "unsupported": unsupported,
                "per_seed_unsupported": [row["unsupported"] for row in rows],
                "unsupported_rate": unsupported / total_shots,
                "plug_in_repetition_overhead": verifier.repetition_overhead(
                    unsupported / total_shots
                ),
                "unsupported_by_reason": {
                    name: sum(row["unsupported_by_reason"][name] for row in rows)
                    for name in rows[0]["unsupported_by_reason"]
                },
                "pivot_counts": {
                    "a0": sum(row["pivot_counts"]["a0"] for row in rows),
                    "a1": sum(row["pivot_counts"]["a1"] for row in rows),
                },
            }
        )
    weight_counts = {
        str(weight): sum(
            int(seed_result["weight_counts"].get(str(weight), 0))
            for seed_result in seed_results
        )
        for weight in range(36)
        if any(str(weight) in seed_result["weight_counts"] for seed_result in seed_results)
    }
    output = {
        "experiment": "exp-057-translated-prefix-support-audit",
        "field": "GF(2^12), modulus 0x1053, primitive element 2",
        "seeds": list(SEEDS),
        "shots_per_seed": SHOTS_PER_SEED,
        "total_shots": total_shots,
        "distribution": "Exact official DQI weight probabilities; positions and nonzero magnitudes are uniform, with beta values sampled uniformly from GF(2^12)^*.",
        "direct_fma_map_crosscheck": "PASS",
        "scalar_crosschecks_per_origin_per_seed": 40,
        "probability_mass_weights_29_35": seed_results[0]["probability_mass_weights_29_35"],
        "weight_counts": weight_counts,
        "best_origin_by_seed": [seed_result["best_origin"] for seed_result in seed_results],
        "prefix_origins": aggregated_origins,
        "best_origin": min(
            aggregated_origins, key=lambda result: result["unsupported"]
        )["prefix_origin"],
        "scope": "Classical prefix-shape support audit only; it does not run a quantum circuit or official verifier.",
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
