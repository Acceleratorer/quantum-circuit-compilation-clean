---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8) prefix and tail state and matrix encoding; 2,048 seeded GF(2^12); 256 seeded GF(2^12) tail-matrix factorization cases; 32-case private coefficient-to-prefix and prefix-to-coefficient screens including a1=0; 32-case private integrated prefix-plus-tail action across both pivots; 32-case private 66-symbol matrix-stream checksum across both pivots; 32-case private compact-prefix-to-matrix 66-symbol checksum v15; 32 verifier-form prefix and tail cases; 32-case sequential FMA pair update across both pivots; 64-case private precomputed-matrix action; 64-case coefficient-derived tail action; 64-case in-place matrix setup
direction: D-004
status: coefficient-prefix-component-gates-passed_classical-66-tail-schedule-passed_branchless-prefix-inverse-v11-passed_integrated-prefix-plus-one-tail-v13-passed_precomputed-state-66-symbol-matrix-stream-checksum-v14-passed_compact-prefix-matrix-66-stream-v15-passed_sequential-fma-pair-update-component-passed_dqi-output-cleanup-and-official-verifier-pending
date: 2026-11-23
result: Coefficient-to-prefix gate passes at Q=885 and T=7,483; branchless inverse prefix-to-coefficient gate passes at Q=888 and T=9,262; integrated compact-prefix decode plus one coefficient-derived tail action passes at Q=889 and T=10,084; precomputed-state 66-symbol matrix stream checksum passes at Q=888 and T=5,544; precomputed-matrix action at Q=873 and T=84; coefficient-derived one-symbol action at Q=889 and T=822; in-place matrix setup at Q=889 and T=558; integrated v15 compact-prefix, matrix setup, and 66-action checksum passes at Q=889 and T=19,004; one sequential FMA pair update passes both pivot branches at Q=108 and T=210 with 48 clean scratch qubits. DQI output/phase, reversible cleanup, and the official verifier remain open.
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

The coefficient-to-compact-prefix decoder passes the 32-case screen in
private Kaggle kernel version 10 at `Q=885`, `T=7,483`. Both pivot paths are
covered, including a valid `a1=0` inactive-branch case. All four output words
round-trip, the rank tag is restored, all 66 arbitrary spectator words are
preserved, 36 scratch qubits are clean, and there are no phase flips.

The private-kernel builder embeds the helper source with its Apache `LICENSE`
and `NOTICE`; the exact kernel source hash and run receipt are in
[`evals/2026-11-22-exp057-private-gate-screen.json`](../../evals/2026-11-22-exp057-private-gate-screen.json).

The inverse compact-prefix-to-coefficient cell first passed in private kernel
version 10 at `Q=889`, `T=22,954`. Version 11 replaces its pivoted 2x2 map
with a branchless factorization and passes at `Q=888`, `T=9,262`, two qubits
under the width gate. Across 32 cases, it reconstructs all four coefficients,
preserves the rank/pivot and 66 arbitrary spectator words, leaves 39 scratch
qubits clean, and has zero phase flips. The v10 baseline receipt is
[`exp-057 prefix-to-coefficient v10`](../../evals/2026-11-23-exp057-prefix-coefficient-v10.json);
the v11 result is
[`exp-057 prefix-to-coefficient v11`](../../evals/2026-11-23-exp057-prefix-coefficient-v11.json).

For `W0=a0`, `W1=a0+a1+1`, and `W2=a0+2a1+4`, the checked inverse matrix is
`N/20`, where `N00=6a0^2+12a0`, `N01=a0(6a1+10)`, and
`N11=6a0+6a1^2+10a1+12`. The factorization uses
`u=(N00+N01)/20=6a0*W1/20`, which is nonzero on the supported domain because
`A(0)` and `A(1)` are nonzero. A seeded local screen checked the determinant
and factorization on 256 GF(2^12) cases; the unit test is
[`test_exp057_tail_map_factorization.py`](../../tests/test_exp057_tail_map_factorization.py).

This is still a four-word component screen. It does not implement the
integrated 4+66 schedule or run the official DQI verifier. The complete v11
receipt and run log record that scope explicitly.

Private kernel version 13 composes this decoder with one tail action in the
same circuit. It passes 32 cases covering both prefix pivots at `Q=889`,
`T=10,084`, with all 66 tail words and rank/pivot preserved, 16 clean scratch
qubits, and zero phase flips. This is a measured 4+1 composition. The full
66-symbol schedule remains open; see the
[`v13 receipt`](../../evals/2026-11-23-exp057-prefix-tail-v13.json),
[`run log`](../../log/2026-11-23-exp057-prefix-tail-v13.md), and
[`milestone`](../../milestone/2026-11-23-exp057-prefix-tail-v13.md).

The earlier component screens check that 66 spectator words are preserved.
Version 13 adds one action at point 4, but it still does not decode all 66
tail symbols. No competition submission was made. The integrated 4+66
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

## Full 66-symbol tail algebra

The four-word compact state reconstructs the normalized low row of the
four-point FMA basis and canonical complementary row. For each later symbol,
the screen evaluates the 2x2 polynomial matrix and checks coefficient
reconstruction from its entries plus `b1`, as well as invertibility and pair
round-trip.

The screen passed all 2,016 supported GF(8) states at the four distinct tail
points 4–7, plus 32 seeded verifier-form GF(2^12) cases (16 each at error
weights 31 and 35) across all 66 tail points 4–69. That is 8,064 GF(8) and
2,112 GF(2^12) matrix/tag reconstructions and pair round-trips with zero
errors. The GF(2^12) sample used the `a0` pivot in all 32 cases; exhaustive
GF(8) includes both pivots. Reproduction:
`python experiments/exp-057/streaming_fixed_shape_decoder.py` and
`python -m unittest discover -s tests -p test_exp057_tail_transition.py -v`.

The first row's sample coefficient vanishes at 700 of the 8,064 GF(8) tail
cases and one of the 2,112 GF(2^12) tail cases. The second row's coefficient
was nonzero in every such case, as the nonzero matrix determinant requires.
The in-place 66-symbol circuit therefore needs a dynamic row pivot.

This receipt verifies classical algebra only. The integrated private gate
passed later in v15; DQI output/cleanup and the official verifier remain open.
See the [v15 screen](../../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json).
Receipt:
[`exp-057 full tail transition`](../../evals/2026-11-22-exp057-tail-transition-classical.json).

## Streaming matrix recurrence

For matrix values `(A,B;C,D)` at point `x`, carry `K=D/b1` plus the `a1` and
`b1` tags. At the next point `y`, let `delta=x+y` and
`scale=P(y)/P(x)`, where `P` is the four-point node polynomial. Then
`A'=A+delta*a1+delta^2`, `B'=B+delta*b1`,
`C'=scale*(C+delta*K)`, `D'=scale*D`, and `K'=scale*K`. Since each multiplier
is a fixed field constant, these updates use only CNOT gates once the tags and
initial matrix are available.

The recurrence matches direct matrix evaluation on all 8,064 supported GF(8)
tail cases and 2,112 seeded GF(2^12) verifier-form cases. Private kernel v14
then compiled 66 matrix actions with this recurrence into a one-word XOR
checksum: `Q=888`, `T=5,544`, 32 cases, zero checksum errors, and zero phase
flips. The 70 payload words and three stream tags were preserved. The kernel
starts from a supplied point-4 matrix and tags; it does not yet include the
compact-prefix decode, reversible matrix setup, or DQI output. See the
[`recurrence receipt`](../../evals/2026-11-23-exp057-matrix-stream-recurrence.json),
[`v14 receipt`](../../evals/2026-11-23-exp057-matrix-stream-v14.json),
[recurrence log](../../log/2026-11-23-exp057-matrix-stream-recurrence.md),
[v14 run log](../../log/2026-11-23-exp057-matrix-stream-v14.md), and
[v14 milestone](../../milestone/2026-11-23-exp057-matrix-stream-v14.md).

## Precomputed-matrix action gate

Private Kaggle kernel version 5 compiles the out-of-place action
`(u,v) -> (a*u+b,c*u+d)` for one tail symbol. Across 64 invertible matrices,
all outputs matched; the 70-word payload, rank, and pivot were preserved, with
no phase flips and no dirty scratch. The cell measured `Q=873`, `T=84`.
Receipt: [`exp-057 tail matrix action`](../../evals/2026-11-22-exp057-tail-matrix-gate.json).

The four matrix entries are independent precomputed inputs in this early
screen. Private v15 later composed prefix decoding, matrix setup, and the
66-symbol checksum stream at `Q=889`, `T=19,004`. DQI output/cleanup and the
official verifier remain open; see the
[`v15 receipt`](../../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json).

## Coefficient-derived tail action gate

Private Kaggle kernel version 6 derives and applies the one-symbol action from
four supplied polynomial coefficients. Across 64 cases at point 4, it passed
at `Q=889`, `T=822`; the 70-word payload, rank, and pivot were preserved, all
16 scratch qubits were clean, and there were no output errors or phase flips.
The run also repeated the prefix and precomputed-matrix gates. Receipt:
[`exp-057 coefficient-derived tail action`](../../evals/2026-11-22-exp057-tail-bezout-action.json).

The coefficients are direct inputs in this one-symbol screen. The later v15
screen covers prefix decoding and all 66 matrix actions, but its checksum is
not the DQI output and it omits reversible cleanup and verification.

## Tail-matrix state encoding screen

The four evaluated matrix entries are not a reversible replacement for the
four-word coefficient state: the exhaustive GF(8) screen maps 2,016 supported
states to 444 matrix keys, with 1,572 collisions and a maximum fiber of 7.
Retaining the full `b1` field word removes all collisions and reconstructs the
coefficients in this domain. The same formula reconstructs 32 seeded GF(2^12)
verifier-form cases (16 each at error weights 31 and 35). Receipt:
[`exp-057 tail-matrix encoding`](../../evals/2026-11-22-exp057-tail-matrix-encoding.json).

This is not a compact-prefix input or an exhaustive GF(2^12) injectivity
result. Private v15 later composed the compact prefix, `b1`-tagged setup, and
the 66-symbol stream; see the
[`v15 receipt`](../../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json).

## In-place coefficient-to-matrix setup gate

Private Kaggle kernel version 7 now maps the four supplied coefficient words
in place to `(A(x), B(x), C(x), D(x))` and retains `b1` for reversible
recovery. The point-4 screen passed 64 cases at `Q=889`, `T=558`; it preserved
the other 66 payload words and rank/pivot, left 28 scratch qubits clean, and
had no matrix errors, tag errors, or phase flips. The same counts passed a
local 64-case point-69 screen. Receipt:
[`exp-057 tail-matrix state gate`](../../evals/2026-11-22-exp057-tail-matrix-state-gate.json).

Private kernel v15 composes the compact-prefix decoder, matrix setup, and all
66 tail actions in one circuit. Across 32 cases covering both prefix pivots
(`a0`: 31, `a1`: 1), the matrix and tags matched, the checksum had zero errors,
all 66 tail words were preserved, 12 scratch qubits were clean, and there were
no phase flips. It measured `Q=889`, `T=19,004`, one qubit under the width gate.
The fourth matrix word stores `K=D/b1`; each tail action reconstructs its `D`
term as `K*b1`. Rank workspace is reused to fit the width.

Private kernel v16 reran this same checksum circuit on 31 verifier-form
syndrome cases at weights 29–35 and one synthetic alternate-pivot case. All
matrix, tag, and checksum checks passed at the same `Q=889`, `T=19,004`.
Verifier-form cases were resampled to fit the current prefix shape, so this is
not an error-rate estimate. The circuit still does not consume the tail pairs
with the key-equation solver or implement the DQI output, phase, cleanup, or
official verifier. See the [v16 receipt](../../evals/2026-11-23-exp057-verifier-form-v16.json)
and [run log](../../log/2026-11-23-exp057-verifier-form-v16.md), plus the
[raw Kaggle output](kaggle-v16-output.log).

A separate classical support audit compared 17 four-point prefix blocks using
the official DQI distribution, then checked origins 0 and 24 on fresh seeds.
Origin 24 had 55 unsupported shapes in 49,152 shots versus 75 for origin 0,
but this is only a modest pre-circuit estimate. The integrated gate path assumes
prefix points 0–3; changing that requires coordinated updates to the reversible
prefix decoder and all 66 tail actions. Keep the circuit unchanged until the
full output and cleanup path can validate that choice. See the
[audit receipt](../../evals/2026-11-23-exp057-prefix-origin-audit.json) and
[run log](../../log/2026-11-23-exp057-prefix-origin-audit.md).

This is an integrated resource screen, not a DQI candidate. It outputs only a
checksum, reuses the rank register, and does not restore the prefix/matrix
state, generate the DQI phase/output, or run the official verifier. See the
[`v15 receipt`](../../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json),
[run log](../../log/2026-11-23-exp057-prefix-matrix-stream-v15.md), and
[milestone](../../milestone/2026-11-23-exp057-prefix-matrix-stream-v15.md),
plus the [raw Kaggle output](kaggle-v15-output.log).

Next gate: connect the 66-symbol actions to the DQI output/phase, uncompute
the setup while preserving the required input registers, measure the complete
resource count, then run the official verifier. No competition submission was
made.

## Sequential FMA future-pair update

Private Kaggle kernel v17 checks one reversible sequential-FMA update on 32
seeded pairs for each pivot branch. Both branches matched
`d' = g_j*d + d_j*g` and the selected `g'` update, preserved the pivot inputs,
cleaned 48 scratch qubits, and had no phase flips. The compiled cell is
`Q=108`, `T=210` for `delta=37`; it remains below the 50-qubit scratch ceiling.
Reusing the retained old-pair registers as XOR targets reduced the initial
cell from 60 to 48 scratch qubits and from 252T to 210T.

This is one pair cell with its pivot inverse supplied as input. It is not the
70-symbol key-equation solve. The full FMA recurrence has 2,415 pair updates;
repeating this 210T cell would cost 507,150T before setup or cleanup, already
above the whole DQI gate. Keep it as a correctness/width result and do not
repeat this implementation in the full schedule. The next gate remains the
complete streamed key-equation output, phase, and cleanup at the full resource
limit. See the [v17 receipt](../../evals/2026-11-23-exp057-fma-pair-update-v17.json),
[run log](../../log/2026-11-23-exp057-fma-pair-update-v17.md), and
[raw Kaggle output](kaggle-v17-output.log).
