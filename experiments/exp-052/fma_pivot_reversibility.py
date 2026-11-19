"""Check that each FMA sample update is locally reversible at valid pivots.

The check is a prerequisite for an in-place circuit schedule. It does not
bound the full schedule's branch-history storage or resource cost.
"""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
from random import Random
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def check_sequence(data, points, mul, modulus, degree):
    d, g = list(data), [1] * len(data)
    rank1, rank2 = 0, 1
    inverse_checks = 0

    for j, point in enumerate(points):
        dj, gj = d[j], g[j]
        if not (dj or gj):
            raise AssertionError(f"zero pivot at index {j}")

        swap = gj == 0 or (dj != 0 and rank1 < rank2)
        for i in range(j + 1, len(points)):
            delta = points[i] ^ point
            if delta == 0:
                raise AssertionError("FMA points must be distinct")

            old_d, old_g = d[i], g[i]
            new_d = mul(gj, old_d) ^ mul(dj, old_g)
            new_g = mul(delta, old_d if swap else old_g)

            # Check both ends of every suffix update without storing a history.
            if i == j + 1 or i == len(points) - 1:
                inv_delta = fma.gf_inv(delta, modulus, degree)
                recovered_g_or_d = mul(inv_delta, new_g)
                if swap:
                    recovered_d = recovered_g_or_d
                    recovered_g = mul(
                        fma.gf_inv(dj, modulus, degree),
                        new_d ^ mul(gj, recovered_d),
                    )
                    if (recovered_d, recovered_g) != (old_d, old_g):
                        raise AssertionError("swap update did not invert")
                else:
                    recovered_g = recovered_g_or_d
                    recovered_d = mul(
                        fma.gf_inv(gj, modulus, degree),
                        new_d ^ mul(dj, recovered_g),
                    )
                    if (recovered_d, recovered_g) != (old_d, old_g):
                        raise AssertionError("no-swap update did not invert")
                inverse_checks += 1

            if mul(delta, dj if swap else gj) == 0:
                raise AssertionError(f"singular update at index {j}")
            d[i], g[i] = new_d, new_g

        if swap:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2

    return {"pivots": len(points), "inverse_checks": inverse_checks}


def exhaustive_gf4():
    degree, modulus, points = 2, 0b111, list(range(4))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    cases = 0
    inverses = 0
    for values in product(range(1 << degree), repeat=len(points)):
        result = check_sequence(values, points, mul, modulus, degree)
        cases += 1
        inverses += result["inverse_checks"]
    return {
        "field": "GF(4)",
        "input_domain": "all pristine 4-symbol tuples",
        "cases": cases,
        "pivots": cases * len(points),
        "inverse_checks": inverses,
        "zero_pivots": 0,
    }


def exhaustive_valid_gf8():
    degree, modulus, points = 3, 0b1011, list(range(8))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    cases = 0
    inverses = 0
    q = 1 << degree

    for weight in range(5):
        for positions in combinations(range(1, q), weight):
            for magnitudes in product(range(1, q), repeat=weight):
                syndrome = [0] * len(points)
                for beta, magnitude in zip(positions, magnitudes):
                    power = beta
                    for j in range(len(points)):
                        syndrome[j] ^= mul(magnitude, power)
                        power = mul(power, beta)
                data = fma.syndrome_to_fma_samples(syndrome, points, mul)
                result = check_sequence(data, points, mul, modulus, degree)
                cases += 1
                inverses += result["inverse_checks"]

    return {
        "field": "GF(8)",
        "input_domain": "all valid RS error patterns through weight 4",
        "cases": cases,
        "pivots": cases * len(points),
        "inverse_checks": inverses,
        "zero_pivots": 0,
    }


def sampled_dqi():
    degree, modulus, points = 12, 0x1053, list(range(70))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    rng = Random(0xF1A052)
    cases = 0
    inverses = 0
    for weight in (1, 31, 35):
        for _ in range(64):
            locations = rng.sample(range(1, 1 << degree), weight)
            magnitudes = [rng.randrange(1, 1 << degree) for _ in locations]
            syndrome = [0] * len(points)
            for beta, magnitude in zip(locations, magnitudes):
                power = beta
                for j in range(len(points)):
                    syndrome[j] ^= mul(magnitude, power)
                    power = mul(power, beta)
            data = fma.syndrome_to_fma_samples(syndrome, points, mul)
            result = check_sequence(data, points, mul, modulus, degree)
            cases += 1
            inverses += result["inverse_checks"]

    return {
        "field": "GF(2^12)",
        "input_domain": "seeded valid DQI error patterns, 64 each at weights 1, 31, 35",
        "cases": cases,
        "pivots": cases * len(points),
        "inverse_checks": inverses,
        "zero_pivots": 0,
    }


def main():
    results = [exhaustive_gf4(), exhaustive_valid_gf8(), sampled_dqi()]
    report = {
        "experiment": "exp-052",
        "result": "PASS",
        "checks": results,
        "structural_invariant": (
            "The pre-step FMA basis determinant is a nonzero scalar multiple of "
            "the product of previous point factors. At a distinct next point, "
            "the evaluated basis is invertible, and the pristine input pair "
            "(d, 1) is nonzero. Thus the pivot pair is nonzero. The selected "
            "FMA branch then makes the sample-update determinant nonzero."
        ),
        "scope": (
            "Local data-pair updates are invertible when the branch and pivot "
            "are available. This does not prove branch-history cleanup, the "
            "full reversible liveness schedule, or the score gate."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
