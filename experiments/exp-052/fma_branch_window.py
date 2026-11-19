"""Screen how much local FMA state is needed to recover a branch bit.

The domain is every valid GF(8), eight-point RS error pattern through weight
four. The key contains post-step ranks and a contiguous window of pivot pairs
around the current pivot. This is a small-domain information screen, not a
reversible circuit or a bound for the 70-point DQI instance.
"""

from __future__ import annotations

from itertools import combinations, product
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


def valid_states():
    degree, modulus, points = 3, 0b1011, list(range(8))
    q = 1 << degree
    mul = lambda a, b: fma.gf_mul(a, b, modulus, degree)
    states = []

    for weight in range(len(points) // 2 + 1):
        for betas in combinations(range(1, q), weight):
            for magnitudes in product(range(1, q), repeat=weight):
                syndrome = [0] * len(points)
                for beta, magnitude in zip(betas, magnitudes):
                    power = beta
                    for index in range(len(points)):
                        syndrome[index] ^= mul(magnitude, power)
                        power = mul(power, beta)
                data = fma.syndrome_to_fma_samples(syndrome, points, mul)
                states.append([data, [1] * len(points), 0, 1, 0])

    assert len(states) == 97_119
    return states, points, mul


def screen():
    states, points, mul = valid_states()
    n = len(points)
    results = []

    for step in range(n):
        for state in states:
            d, g, rank1, rank2, history = state
            pivot_d, pivot_g = d[step], g[step]
            swap = pivot_g == 0 or (pivot_d != 0 and rank1 < rank2)
            if swap:
                rank1, rank2 = rank2, rank1 + 2
                history |= 1 << step
            else:
                rank2 += 2

            for index in range(step + 1, n):
                old_d, old_g = d[index], g[index]
                d[index] = mul(pivot_g, old_d) ^ mul(pivot_d, old_g)
                g[index] = mul(points[index] ^ points[step], old_d if swap else old_g)
            state[2:] = [rank1, rank2, history]

        best = None
        for pair_count in range(1, n + 1):
            for previous in range(step + 1):
                future = pair_count - previous - 1
                if future < 0 or future > n - step - 1:
                    continue
                start, stop = step - previous, step + future + 1
                seen = {}
                collision = False
                for d, g, rank1, rank2, history in states:
                    key = (rank1, rank2) + tuple(
                        value
                        for index in range(start, stop)
                        for value in (d[index], g[index])
                    )
                    branch = (history >> step) & 1
                    mask = seen.get(key, 0) | (1 << branch)
                    if mask == 3:
                        collision = True
                        break
                    seen[key] = mask
                if not collision:
                    best = {
                        "pair_values_in_key": pair_count,
                        "previous_pivots": previous,
                        "future_pairs": future,
                        "gf8_feature_bits": 2 * (2 * n + 1).bit_length() + 2 * 3 * pair_count,
                        "gf2_12_70_point_analogue_bits": 2 * (2 * 70 + 1).bit_length() + 2 * 12 * pair_count,
                    }
                    break
            if best is not None:
                break

        if best is None:
            raise AssertionError(f"full state did not recover branch at step {step}")
        results.append({"step_zero_based": step, **best})

    return {
        "experiment": "exp-052-branch-window",
        "field": "GF(8)",
        "points": n,
        "valid_patterns": len(states),
        "result": "PASS",
        "steps": results,
        "scope": (
            "Exact on all valid GF(8) patterns through weight 4. It tests only "
            "contiguous pivot windows and gives no 70-point circuit or Toffoli bound."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(screen(), indent=2, sort_keys=True))
