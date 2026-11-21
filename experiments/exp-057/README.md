---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8); 2,048 seeded GF(2^12) cases
direction: D-004
status: local_transition_feasibility
date: 2026-11-21
result: The four-sample map reconstructs all 1,568 valid GF(8) states and 2,048 sampled GF(2^12) states using four live field words; no gate circuit or resource estimate yet.
---

# exp-057: four-word streaming decoder

## Result

For a monic irreducible quadratic `A(X)=X^2+a1*X+a0` and linear `B(X)=b1*X+b0` with `b1 != 0`, the decoder uses the first three samples to keep one coefficient parameter alongside `d0,d1,d2`. The fourth sample recovers that parameter. This establishes a classical reversible-state relation for this factorization shape only.

The bounded screen passed:

| Field | Valid cases | Pivot `a0` | Pivot `a1` | Collisions |
|---|---:|---:|---:|---:|
| GF(8), exhaustive | 1,568 | 1,393 | 175 | 0 |
| GF(2^12), seeded sample | 2,048 | 2,047 | 1 | not exhaustively checked |

Run with `python experiments/exp-057/streaming_fixed_shape_decoder.py`. GF(8) exhausts the valid coefficient domain. GF(2^12) uses seed `0xA466057` and the quadratic trace criterion. The screen found that sample values need not be pairwise distinct; only the full four-sample vector must distinguish valid coefficient states.

## Boundary

This is not a quantum circuit, a complete DQI schedule, or a submission candidate. It does not measure width, Toffoli count, phase, cleanup, or cover other factorization shapes. The next decision is whether this four-word relation can be realized inside the existing 4+66 schedule within its `Q <= 890` and `T <= 221,529` gates; if not, stop this direction.
