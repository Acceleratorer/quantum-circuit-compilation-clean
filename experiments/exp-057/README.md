---
id: exp-057
title: Four-word streaming decoder for quadratic-over-linear FMA
task: dqi
tests: exhaustive GF(8) prefix and tail state and matrix encoding; 2,048 seeded GF(2^12); 256 seeded GF(2^12) tail-matrix factorization cases; 32-case private coefficient-to-prefix and prefix-to-coefficient screens including a1=0; 32-case private integrated prefix-plus-tail action across both pivots; 32-case private 66-symbol matrix-stream checksum across both pivots; 32-case private compact-prefix-to-matrix 66-symbol checksum v15; 32 verifier-form prefix and tail cases; 64-case private MBU FMA pair update across both branches; 64-case private precomputed-matrix action; 64-case coefficient-derived tail action; 64-case in-place matrix setup; 32-case classical Forney/FMA MBUC phase-compatibility screen; 97,118 exhaustive GF(8) Newton-residue versus direct interpolation cases
direction: D-004
status: coefficient-prefix-component-gates-passed_classical-66-tail-schedule-passed_branchless-prefix-inverse-v11-passed_integrated-prefix-plus-one-tail-v13-passed_precomputed-state-66-symbol-matrix-stream-checksum-v14-passed_compact-prefix-matrix-66-stream-v15-passed_mbu-fma-pair-update-v18-component-passed_classical-phase-compatibility-screen-passed_direct-fma-convert-scan-bridge-v19-failed_newton-residue-identity-v20-passed_newton-route-over-budget-and-input-contract-unmapped_full-70-symbol-schedule-dqi-output-cleanup-and-official-verifier-pending_native-node-scan-failed
date: 2026-11-23
result: V20 Newton insertion exactly matches direct Lagrange scanner-residue interpolation in 97,118 exhaustive GF(8) cases. At weight 35, its straightforward coefficient-array screen counts 2,415 variable GF products (~101,430T at 42T/product), above the 36,183.74T converter allowance before inverses and uncomputation. The recurrence requires error-root/residue inputs; no direct map from exp-057's 70 syndrome-derived FMA samples is established. This estimate is not a lower bound. No reversible screen, full schedule, or official verifier was run.
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

The Forney phase-compatibility screen independently constructs the error
locator/evaluator polynomials, recovers all error values from the FMA samples,
and compares their parity against the verifier's 4,095 MBUC masks. All 1,056
values and all 32 phases matched across weights 31 and 35, including forced
errors at prefix nodes 1, 2, and 3. Reproduce with
`python -m unittest discover -s tests -p test_exp057_phase_compatibility.py -v`.
This is a classical formula check only; reversible phase extraction, full
schedule cost, cleanup, and official verification are still open.

The existing `phase_inverse36_pivot` helper was measured locally on 64 seeded
inputs: it preserves the 12-bit value, cleans 12 scratch qubits, and matches
all 64 expected phases. It compiles to 168 static Toffoli-like gates and the
simulator executes 2,304 total, or 36 per mask. The official reference
Forney loop visits 4,095 positions, so inserting this helper once per position
costs `147,420T`, above D-004's refreshed `37,927.91T` remaining budget. The
existing 45,045T Chien/residue scan in
[`src/dqi/pro_q2_897/exp/scan/scan.py`](../../src/dqi/pro_q2_897/exp/scan/scan.py)
is already included in the FMA projection. The open algebraic aggregation
screen below has no reversible root-list construction or resource count yet.

An algebraic aggregation screen tests a possible way around that cost. Let
`L(M)` be the trace-dual transform satisfying
`Tr(e * L(M)) = popcount(e & M) mod 2`. For non-node error roots `b`, set
`g(b) = L(M_position(b)) / (b * P(b))`; set `g(b)=0` for roots at sample nodes
and add those node phases directly from the recovered values. The external
phase field sum then equals the coefficient of `X^(t-1)` in
`omega(X) * g(X) mod sigma(X)`, by Lagrange interpolation over the distinct
roots of `sigma`. A seeded 32-case screen at weights 31 and 35, including
prefix-node errors, had zero residue-identity errors and zero phase
mismatches. The screen interpolates only the tested roots; a reversible way to
derive the full mask polynomial/remainder, its gate cost, cleanup, and official
verification are still open. Reproduce with the same phase-compatibility test.

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

Private Kaggle kernel v18 passes the normalized MBU FMA pair update on 64
seeded cases, 32 per branch. Outputs match, the supplied ratio and branch are
preserved, 13 scratch qubits are clean, and there are no phase flips. The cell
measures `Q=50`, `T=54`.

The older v17 cell cost `210T`; repeating it over 2,415 updates would exceed
the full DQI gate. V18's `130,410T` repeated subtotal matches the existing
ledger's `42T` product plus `12T` controlled swap per update. The v19 local
diagnostic found that direct use of the padded FMA low-rank row fails phase
through the current CONVERT + scan path. That path costs `183,837T` by itself
at `Q=879`; a canonical DQI residue-pair control passes the same phase check.
Combining the measured path with the v18 subtotal would cost `314,247T`, so the
previous `202,075T` full projection is unsupported. The cell receives ratio
and branch inputs, and the full 70-symbol schedule, width, DQI output/phase,
cleanup, and official verifier remain unmeasured. See the
[v18 receipt](../../evals/2026-11-23-exp057-fma-pair-update-mbu-v18.json),
[run log](../../log/2026-11-23-exp057-fma-pair-update-mbu-v18.md), and
[raw Kaggle output](kaggle-v18-output.log), plus the
[v19 bridge receipt](../../evals/2026-11-23-exp057-fma-convert-scan-v19.json)
and [reproduction screen](convert_bridge_screen.py).

The follow-up cost split measures forward CONVERT at 69,220T, scan at 44,275T,
and reverse CONVERT at 70,342T. Even granting a zero-cost replacement for the
reverse step, the bridge plus v18 repeated updates totals 243,905T, above the
refreshed 210,868.74T score-equivalent gate before other work. See the
[cost-split receipt](../../evals/2026-11-23-exp057-convert-cost-split.json)
and [log](../../log/2026-11-23-exp057-convert-cost-split.md).

## Newton residue insertion screen

For existing error roots `beta_i` and desired scanner values
`y_i = e_i beta_i Pscan(beta_i)`, Newton interpolation updates the degree-`<t`
scanner numerator with

```text
c_i = (y_i + A_(i-1)(beta_i)) / sigma_(i-1)(beta_i)
A_i = A_(i-1) + c_i sigma_(i-1)
sigma_i = sigma_(i-1) (X + beta_i)
```

The recurrence is exact: it matches direct Lagrange interpolation for all
97,118 nonzero-magnitude, distinct-root cases of weights 1–4 in GF(8). The
screen is [`newton_residue_screen.py`](newton_residue_screen.py); receipt and
log: [`v20 evaluation`](../../evals/2026-11-23-exp057-newton-residue-v20.json)
and [`v20 log`](../../log/2026-11-23-exp057-newton-residue-v20.md).

At weight 35, a straightforward coefficient-array implementation counts 2,415
variable GF(2^12) products, about 101,430T at the project's 42T product cost.
This already exceeds the 36,183.74T allowance for replacing CONVERT, before
inversions or uncomputation. It is an operation-count estimate, not a lower
bound. More fundamentally, this recurrence consumes error roots and desired
residues, while exp-057 currently processes 70 syndrome-derived sample values;
no direct update map between those states is established. Do not build a gate
screen for this recurrence unless both the input mapping and a cheaper schedule
are derived. DQI output, cleanup, and the official verifier remain open.

## Phase-node alignment gate

Private-kernel versions 19 and 20 tested the FMA residue polynomial with its
matching 70-node polynomial. The isolated phase gate passed with the converter
at `Q=879`, `T=183,155`; the converter-free control had one phase error in two
cases. The passing screen uses a residue pair built from known error locations,
so it does not establish a reversible FMA generator or a full DQI candidate.
The measured converter-plus-FMA-update subtotal is over the current score gate.
See the [evaluation](../../evals/2026-11-23-exp057-phase-node-alignment.json)
and [run log](../../log/2026-11-23-exp057-phase-node-alignment.md).

## FMA-native-node scan screen (failed)

The standalone circuit screen used weights 31 and 35 and observed one phase
error at Q=851, T=43,593. It restored every input register and cleaned 11
scratch qubits. The scan skipped the first 70 positions and all 69 roots of
the FMA sample-node polynomial. The full sample-node error branch and official
verifier were not run, so this remains a failed shortcut screen.

Receipt: [evaluation](../../evals/2026-11-24-exp057-fma-native-node-scan.json).
Run with `python experiments/exp-057/native_node_scan_screen.py`.

## Native phase derivative diagnosis

A classical 64-case GF(2^12) screen isolated the phase mismatch: the raw FMA
numerator gives `error(r) * sigma_prime(r)` at an error root. The scanner needs
the corresponding `omega(r) / sigma_prime(r)` residue. The identity held on
all cases; correcting its predicted parity removed all 30 raw phase
mismatches. This does not implement the correction reversibly or establish
its cost. The next root-conditioned gate below tested that correction and
closed the route. See the
[evaluation](../../evals/2026-11-25-exp057-native-phase-derivative.json) and
[run log](../../log/2026-11-25-exp057-native-phase-derivative.md).

## Root-conditioned Forney phase gate (closed)

Private Kaggle version 23 tested the derivative correction at all 66
denominator-root positions from one seeded weight-31 and one seeded weight-35
case. It added `573,144` simulator-counted T, against a `34,837.57T` remaining
budget, exceeded the 890-qubit screen at `Q=892`, left scratch dirty, and had
one phase mismatch. The same T count for both weights shows that quantum
control did not make the compiled correction cost scale with the number of
roots. Close this route; do not integrate or submit it.

Receipt: [evaluation](../../evals/2026-11-26-exp057-root-conditioned-phase-gate.json),
[run log](../../log/2026-11-26-exp057-root-conditioned-phase-gate.md), and
[private Kaggle version 23](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/23).

## Tail key-equation composition

The canonical four-point FMA basis and all 66 streamed tail updates matched a
direct 70-symbol basis and the expected error locator/evaluator on 32 seeded
GF(2^12) cases, including 11 cases with errors at prefix roots 1, 2, or 3.
This closes the classical basis-composition check only. It does not implement
the derivative correction, DQI output, reversible cleanup, or the official
verifier. Keep the next step on the same DQI path: derive the required
`omega / sigma_prime` residue from the streamed state and measure the complete
reversible schedule. See the [evaluation](../../evals/2026-11-25-exp057-tail-key-equation-composition.json)
and [run log](../../log/2026-11-25-exp057-tail-key-equation-composition.md).

The direct Forney conversion `A = omega / sigma_prime mod sigma` passes its
classical residue checks, but ordinary polynomial Euclid averages 174,672T in
its cheaper direct-right-hand-side form on 64 verifier-shaped inputs. That is
4.83x the 36,183.74T replacement allowance before reversible branches or
cleanup, so neither measured EEA formulation is worth building. This closes
these direct implementations only; receipt:
[evaluation](../../evals/2026-11-25-exp057-forney-polynomial-inverse.json) and
[log](../../log/2026-11-25-exp057-forney-polynomial-inverse.md).
