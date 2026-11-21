---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive valid GF(8) shape; 2,048 seeded GF(2^12) cases
direction: D-004
status: local_transition_feasibility
date: 2026-11-21
result: The four-sample map reconstructs all 2,016 valid GF(8) states and 2,048 sampled GF(2^12) states using four live field words; no gate circuit or resource estimate yet.
---

# exp-057: four-word streaming decoder

## Result

For monic quadratic `A(X)=X^2+a1*X+a0` and linear `B(X)=b1*X+b0` with `b1 != 0`, `gcd(A,B)=1`, and `A(x) != 0` at `x in {0,1,2,3}`, the decoder uses the first three samples to keep one coefficient parameter alongside `d0,d1,d2`. The fourth sample recovers that parameter. These conditions cover the valid `G=1`, degree `(2,1)` factorization shape; irreducibility of `A` is not required.

The bounded screen passed:

| Field | Valid cases | Pivot `a0` | Pivot `a1` | Collisions |
|---|---:|---:|---:|---:|
| GF(8), exhaustive | 2,016 | 1,778 | 238 | 0 |
| GF(2^12), seeded sample | 2,048 | 2,047 | 1 | not exhaustively checked |

Run with `python experiments/exp-057/streaming_fixed_shape_decoder.py`. GF(8) exhausts the valid coefficient domain. GF(2^12) rejection-samples the same coprime, finite-denominator domain with seed `0xA466057`; one valid pivot-`a1` case is deliberately included so both inverse branches are exercised. The screen found that sample values need not be pairwise distinct; only the full four-sample vector must distinguish valid coefficient states.

## Boundary

This is not a quantum circuit, a complete DQI schedule, or a submission candidate. It does not measure width, Toffoli count, phase, cleanup, or cover other factorization shapes. The next decision is whether this four-word relation can be realized inside the existing 4+66 schedule within its `Q <= 890` and `T <= 221,529` gates; if not, stop this direction.
