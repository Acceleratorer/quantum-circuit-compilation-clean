---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8); 2,048 seeded GF(2^12); 32-case private gate screen including a1=0; 32 verifier-form prefix-shape cases; one verifier-form case per weight 0..35
direction: D-004
status: prefix_cell_width_gate_passed_integration_pending
date: 2026-11-22
result: Local and private Kaggle screens pass at Q=885 and T=7,483; this is not the integrated 4+66 decoder and was not submitted.
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

The current source passes the 32-case local Kickmix screen and private Kaggle
kernel version 4 at `Q=885`, `T=7,483`: five qubits under the cell's 890-qubit
gate. Both pivot paths are covered, including a valid `a1=0` case where the
`a1` update branch is inactive. All four output words round-trip, the rank tag
is restored, all 66 arbitrary spectator words are preserved, 36 scratch
qubits are clean, and there are no phase flips.

The private-kernel builder embeds the helper source with its Apache `LICENSE`
and `NOTICE`; the exact kernel source hash and run receipt are in
[`evals/2026-11-22-exp057-private-gate-screen.json`](../../evals/2026-11-22-exp057-private-gate-screen.json).

This proves only the in-place four-word prefix-state cell. The 66 spectator
words are checked for preservation; this cell does not decode them and is not
the integrated 4+66 schedule. No competition submission was made. The full
schedule and official verifier remain required before a candidate can be
considered.

A seeded local spot-check generated 32 valid verifier-form GF(2^12) inputs
(16 each at error weights 31 and 35), mapped all 70 syndromes to FMA samples,
and checked that the first four samples decode to the cell's supported
`G=1, deg(A)=2, deg(B)=1` shape. All 32 reconstructed exactly with no zero
division. Seed: `0x4A66057`. This only checks sampled classical input
compatibility; it does not implement the reversible sample-to-coefficient map
or cover the full verifier input distribution.

A second seeded screen tried one valid error pattern at each weight from 0 to
35. The supported shape held for the sampled weights 2 through 35; the
weight-0 case was unsupported and the weight-1 case hit zero division. These
are real missing branches, so this cell cannot serve as the only prefix path.
This is one case per weight, not exhaustive coverage.
