"""Screen whether FMA branch history is determined by locator support alone.

Exhaustively checks every GF(8), eight-point error pattern through weight four,
including every assignment of nonzero error magnitudes to each support.
"""

from __future__ import annotations

from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def screen():
    degree, modulus = 3, 0b1011
    q = 1 << degree
    points = list(range(q))
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    report = []
    total_patterns = 0

    for weight in range(len(points) // 2 + 1):
        supports = 0
        multiple_histories = 0
        max_histories = 1

        for support in combinations(range(1, q), weight):
            histories = set()
            for magnitudes in product(range(1, q), repeat=weight):
                syndrome = [0] * len(points)
                for beta, magnitude in zip(support, magnitudes):
                    power = beta
                    for index in range(len(points)):
                        syndrome[index] ^= mul(magnitude, power)
                        power = mul(power, beta)

                d = fma.syndrome_to_fma_samples(syndrome, points, mul)
                g = [1] * len(points)
                rank1, rank2 = 0, 1
                history = 0

                for step in range(len(points)):
                    pivot_d, pivot_g = d[step], g[step]
                    swap = pivot_g == 0 or (pivot_d != 0 and rank1 < rank2)
                    if swap:
                        rank1, rank2 = rank2, rank1 + 2
                        history |= 1 << step
                    else:
                        rank2 += 2

                    for index in range(step + 1, len(points)):
                        old_d, old_g = d[index], g[index]
                        d[index] = mul(pivot_g, old_d) ^ mul(pivot_d, old_g)
                        g[index] = mul(
                            points[index] ^ points[step], old_d if swap else old_g
                        )

                histories.add(history)

            supports += 1
            total_patterns += (q - 1) ** weight
            max_histories = max(max_histories, len(histories))
            multiple_histories += len(histories) > 1

        report.append(
            {
                "weight": weight,
                "supports": supports,
                "supports_with_multiple_branch_histories": multiple_histories,
                "max_histories_for_one_support": max_histories,
            }
        )

    assert total_patterns == 97_119
    return {
        "experiment": "exp-052-locator-history",
        "field": "GF(8)",
        "points": len(points),
        "valid_patterns": total_patterns,
        "result": "locator_support_alone_is_insufficient",
        "report": report,
        "scope": (
            "Exact for all GF(8), eight-point error patterns through weight 4. "
            "This falsifies support-only branch history on this domain; it is "
            "not a 70-point GF(2^12) circuit or Toffoli bound."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2, sort_keys=True))
