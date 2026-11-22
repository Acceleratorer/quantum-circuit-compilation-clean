---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8) prefix and tail state and matrix encoding; 2,048 seeded GF(2^12); 32-case private prefix gate screen including a1=0; 32 verifier-form prefix and tail cases; 64-case private precomputed-matrix action; 64-case coefficient-derived tail action; 64-case in-place matrix setup
direction: D-004
status: coefficient-to-matrix-b1-setup-gate-passed_compact-prefix-and-66-symbol-schedule-pending
date: 2026-11-22
result: Prefix gate passes at Q=885 and T=7,483; precomputed-matrix action at Q=873 and T=84; coefficient-derived one-symbol action at Q=889 and T=822; in-place matrix setup at Q=889 and T=558. The GF(8) matrix-only encoding has 1,572 collisions; adding b1 distinguishes all GF(8) states and reconstructs 32 seeded GF(2^12) cases. Compact-prefix input, 66-symbol integration, and the official verifier remain open.
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
weight-0 case was unsupported and the weight-1 case hit zero division. This is
one case per weight, not exhaustive coverage. Under the official default DQI
sampler, the corresponding weight probabilities are `2.78e-26` and
`3.22e-24` (`m=4095`, `n=70`, `degree=12`, `r=2016`), or about `3.32e-19`
combined expected draws in 102,400 shots. The edge cases are not the current
optimization bottleneck; integrating and measuring the full decoder comes
first.

## One-symbol tail transition

The four-word compact state reconstructs the normalized low row of the
four-point FMA basis. For the next symbol, the screen reconstructs the
canonical complementary row, applies the resulting 2x2 polynomial matrix at
point 4, and checks that the matrix determinant is the four-point node
polynomial. Both rows annihilate the original four samples, the tail-point
matrix is invertible, and its inverse recovers the input pair.

The transition passed all 2,016 supported GF(8) coefficient states and 32
seeded verifier-form GF(2^12) cases (16 each at error weights 31 and 35).
The GF(2^12) sample used the `a0` pivot in all 32 cases; the `a1` pivot is
covered exhaustively by GF(8). Reproduction:
`python experiments/exp-057/streaming_fixed_shape_decoder.py` and
`python -m pytest tests/test_exp057_tail_transition.py`.

This is a classical algebra gate only. It does not compile matrix generation
from the prefix state, cover all 66 later symbols, or pass the official
verifier. The separate precomputed-matrix Kickmix action screen is recorded
below.

## Precomputed-matrix action gate

Private Kaggle kernel version 5 compiles the out-of-place action
`(u,v) -> (a*u+b,c*u+d)` for one tail symbol. Across 64 invertible matrices,
all outputs matched; the 70-word payload, rank, and pivot were preserved, with
no phase flips and no dirty scratch. The cell measured `Q=873`, `T=84`.
Receipt: [`exp-057 tail matrix action`](../../evals/2026-11-22-exp057-tail-matrix-gate.json).

The four matrix entries are independent precomputed inputs in this screen. It
does not generate them from the compact prefix state, erase generation
workspace, implement an in-place 66-symbol schedule, or run the official DQI
verifier. The 66-symbol `84T` multiplication is only a sensitivity estimate;
it may overlap with the existing `202,075T` FMA projection. The next gate is a
reversible prefix-state-to-matrix cell, measured together with its cleanup and
the existing prefix cell before extending the schedule.

## Coefficient-derived tail action gate

Private Kaggle kernel version 6 derives and applies the one-symbol action from
four supplied polynomial coefficients. Across 64 cases at point 4, it passed
at `Q=889`, `T=822`; the 70-word payload, rank, and pivot were preserved, all
16 scratch qubits were clean, and there were no output errors or phase flips.
The run also repeated the prefix and precomputed-matrix gates. Receipt:
[`exp-057 coefficient-derived tail action`](../../evals/2026-11-22-exp057-tail-bezout-action.json).

The coefficients are still direct inputs, so this is not yet a compact-state
to-action circuit or a 66-symbol schedule. The next gate is to isolate and
retain coefficient-dependent setup once, measure its generation from the
compact prefix state with clean workspace, and then account for reuse across
the remaining symbols. The one-symbol `822T` result is not a full-schedule
cost estimate.

## Tail-matrix state encoding screen

The four evaluated matrix entries are not a reversible replacement for the
four-word coefficient state: the exhaustive GF(8) screen maps 2,016 supported
states to 444 matrix keys, with 1,572 collisions and a maximum fiber of 7.
Retaining the full `b1` field word removes all collisions and reconstructs the
coefficients in this domain. The same formula reconstructs 32 seeded GF(2^12)
verifier-form cases (16 each at error weights 31 and 35). Receipt:
[`exp-057 tail-matrix encoding`](../../evals/2026-11-22-exp057-tail-matrix-encoding.json).

This is not a compact-prefix input or an exhaustive GF(2^12) injectivity
result. Next, feed the compact prefix state into the measured `b1`-tagged
setup, then test reuse across the tail schedule.

## In-place coefficient-to-matrix setup gate

Private Kaggle kernel version 7 now maps the four supplied coefficient words
in place to `(A(x), B(x), C(x), D(x))` and retains `b1` for reversible
recovery. The point-4 screen passed 64 cases at `Q=889`, `T=558`; it preserved
the other 66 payload words and rank/pivot, left 28 scratch qubits clean, and
had no matrix errors, tag errors, or phase flips. The same counts passed a
local 64-case point-69 screen. Receipt:
[`exp-057 tail-matrix state gate`](../../evals/2026-11-22-exp057-tail-matrix-state-gate.json).

The setup still starts from four coefficients. Next, connect it to the compact
prefix representation and measure reuse over the actual 66-symbol schedule,
then run the official verifier as the final correctness gate.
