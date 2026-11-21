---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8); 2,048 seeded GF(2^12); 32-case private gate screen
direction: D-004
status: width_gate_failed
date: 2026-11-21
result: The current direct-erasure edit passes a 32-case local screen at Q=905 and T=6,993, but remains 15 qubits over the 890-qubit gate; no submission.
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

## Gate screen

The current direct-erasure edit compiled and passed its bounded local screen on
32 seeded GF(2^12) states, including both pivot paths. It reconstructed all
four words, restored the rank tag, left 56 scratch qubits clean, and produced
no phase flips. The local run measured `Q=905` and `T=6,993`.

The last private Kaggle run was version 2 of the earlier source and measured
`Q=909` and `T=7,125`; the current edit has not been run on Kaggle.

This is only the four-word prefix-state cell, not the integrated 4+66 DQI
schedule. The current edit still misses the 890-qubit width gate by 15 qubits,
so it is not ready to integrate or submit. The private Kaggle receipt is in
[`evals/2026-11-21-exp057-gate-screen.json`](../../evals/2026-11-21-exp057-gate-screen.json).
The local direct-erasure screen is in
[`evals/2026-11-21-exp057-local-direct-erasure.json`](../../evals/2026-11-21-exp057-local-direct-erasure.json).
