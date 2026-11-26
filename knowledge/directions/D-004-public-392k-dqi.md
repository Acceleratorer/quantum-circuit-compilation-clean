---
id: D-004
title: Improve the source-owned DQI decoder with a new key-equation algorithm
status: parked
tasks: dqi, all
last_checked: 2026-11-27
---

# D-004: improve the source-owned DQI decoder

The public 392k decoder and hybrid portfolio are measurement references only.
The standing user decision forbids submitting or copying downloaded circuits;
the archive is not a candidate until an attributed source-owned generator
reproduces it. Existing product-retention variants have already been screened.

The Kaggle “Rank #1 Breakthrough” package notebook is already audited in
[exp-043](../../experiments/exp-043/README.md); it remains disqualified as a
compiled-artifact-only source.

The latest Kaggle CLI read at `2026-11-26T17:42:19Z` shows `Cat with 2 Qubits`
at `34.50408`. Source-owned exp-082 now leads our submissions at `33.08801`,
a `1.41607` public-score gap. Holding exp-082's other two component costs
fixed, matching the leader requires DQI cost at or below `269.005e9`, or mean
`T <= 278,784.97` at `Q=900` and `R=1.1912604648`. Exp-082 measures
`316,131.22T`, so the required reduction is `37,346.25T` (11.81%). This is
score-equivalence math, not a measurement of the leader's DQI circuit. See the
[score gate receipt](../../evals/2026-11-26-dqi-score-equivalent-gate.json).

The latest implementation gates close the current DQI branches: exp-057's
root-conditioned phase correction costs `573,144T`, peaks at `Q=892`, leaves
scratch dirty, and has one phase mismatch; exp-053's 4+1 and parity handoffs
both peak at `Q=891` before the remaining pivots; and the direct EEA and
round-trip converter estimates are already above the score gate before full
mapping and cleanup. The published BM resource point is `6.50x` over the tie
gate. Receipts: [phase gate](../../evals/2026-11-26-exp057-root-conditioned-phase-gate.json),
[v35](../../evals/2026-11-26-exp053-four-plus-one-handoff-v35.json),
[v36](../../evals/2026-11-26-exp053-parity-handoff-v36.json),
[EEA/converter gate](../../evals/2026-11-26-dqi-score-equivalent-gate.json),
and [published BM gate](../../evals/2026-11-26-bm-published-cost-gate.json).

A source-only profile of the exact exp-074 DQI release found `318,972` static
Toffoli-like gates. `decoder_return` is the largest stage at `109,515`; the
four D16 substitutions total only `850`. The current `37,346.25` mean-Toffoli
score gap is `34.10%` of the return stage's static count; this is a scale comparison,
not an exact gate-deletion requirement. The profile is a target-setting
diagnostic, not a measured candidate. See the
[stage profile receipt](../../evals/2026-11-26-dqi-stage-profile.json).

**Decision:** park D-004. Reopen it only with a different source-owned
algorithm whose projected full `R × Q² × T` cost is under the current gate and
whose phase, output restoration, and cleanup have a credible width/cost plan.
No DQI candidate or submission is ready.

## 2026-11-23 live leaderboard and focused gate

The latest full Kaggle CLI snapshot at `2026-11-23T00:16:46Z` has 3,598 teams.
`Accelra` is rank 1,356 at `28.14028`; Entangled Team leads at `33.83493`, a
`5.69465`-point gap. Holding the other two submitted task costs fixed,
matching that score requires DQI cost at or below `200.147e9`, or mean
`T <= 212,110.59` at `Q=890` and `R=1.1912605`. The `202,075T` FMA projection
leaves only `10,035.59T` for all omitted work. This is score-equivalence math,
not a measured leader cost or a candidate. The snapshot and calculation are in
[`evals/2026-11-23-live-leaderboard-001646Z.json`](../../evals/2026-11-23-live-leaderboard-001646Z.json).

The official DQI contract audit clarifies the next gate: exp-057's 66-action
checksum does not yet use the MBUC masks or apply the required error-value
phase. The published BM alternative is also over both width and Toffoli gates.
Use the classical phase-compatibility gate before any further circuit build;
see [the contract audit](../../log/2026-11-23-dqi-contract-gate.md).

The valid eight-point GF(8) screen finds that ratios alone need a six-bit
fixed branch projection; ratio plus final rank needs four bits, with nine
four-position choices. This is a block-tag lead only, not a GF(2^12) bound or a
reversible eraser. See the
[`exp-053 projection receipt`](../../evals/2026-11-22-exp053-valid-ratio-history.json).

The active circuit path is the four-word FMA prefix state in exp-057. Its
classical one-symbol transition reconstructs the complementary row and passes
exhaustive GF(8) plus 32 seeded verifier-form GF(2^12) cases. A private
Kickmix screen also compiles one out-of-place tail action at `Q=873`, `T=84`
for 64 cases, but takes all four matrix entries as precomputed inputs. Matrix
generation from the prefix state, its workspace cleanup, and the 66-symbol
schedule remain open. The `84T × 66` figure is only a sensitivity estimate
because those field products may overlap the existing `202,075T` FMA
projection. Continue this single lane through an integrated gate with
`Q <= 890`, complete Toffoli accounting, clean workspace, zero phase errors,
and the official verifier. No submission is ready. See the
[classical tail receipt](../../evals/2026-11-22-exp057-tail-transition-classical.json),
[matrix-action receipt](../../evals/2026-11-22-exp057-tail-matrix-gate.json),
[exp-057 record](../../experiments/exp-057/README.md), and prior
[exp-053 branch-tag record](../../experiments/exp-053/README.md).

## 2026-11-23 exp-057 v15 integrated checksum screen

Private kernel v15 composes the compact-prefix decoder, point-4 matrix setup,
and all 66 tail actions at `Q=889`, `T=19,004`. Its 32 cases cover both
prefix pivots; matrix/tag/checksum errors and phase flips are zero, all tail
words are preserved, and 12 scratch qubits are clean. This verifies the
integrated checksum cell only. It does not emit the full FMA basis or DQI
phase, restore the prefix/matrix state, or pass the official verifier. The
`202,075T` projection remains unvalidated as a complete circuit; v15's cost
must not be treated as additive or overlapping without a composed gate ledger.
Continue this single lane by turning the 66 streamed pair actions into the
state consumed by the tail key-equation solve, then measure output/phase and
reversible cleanup before running the official verifier. See the
[v15 receipt](../../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json),
[log](../../log/2026-11-23-exp057-prefix-matrix-stream-v15.md), and
[milestone](../../milestone/2026-11-23-exp057-prefix-matrix-stream-v15.md).

Private kernel v16 reran the same `Q=889`, `T=19,004` checksum cell on 31
verifier-form syndrome samples at error weights 29–35, plus one synthetic
alternate-pivot case. Matrix, tag, and checksum errors remained zero. The
verifier-form cases were conditioned on the supported four-point prefix shape;
they do not measure decoder coverage or failure rate. This closes only the
input-domain check for the checksum component. The tail key-equation solve,
phase/output, cleanup, full resource ledger, and official verifier remain open.
See the [v16 receipt](../../evals/2026-11-23-exp057-verifier-form-v16.json)
and [run log](../../log/2026-11-23-exp057-verifier-form-v16.md).

## 2026-11-23 exp-057 sequential FMA pair update

Private kernel v17's 210T implementation would cost 507,150T over the 2,415
pair updates and is closed. V18 replaces the product cleanup with MBU and
passes 64 cases (32 per branch) at `Q=50`, `T=54`, with 13 clean scratch
qubits and zero phase flips. Repeating this cell gives `130,410T`, matching
the existing product-plus-swap term in the `202,075T` full projection; that
projection leaves only `10,035.59T` under the current gate.

This is a component measurement only: the ratio and branch are inputs, and
the full 70-symbol schedule, DQI output/phase, cleanup, and official verifier
are not included. Build one composed schedule and measure its complete
`Q`/`T` ledger; continue only if it fits the full gate. The update count comes
from the [exp-053 70-symbol ledger](../../experiments/exp-053/README.md#pivot-normalized-fma-recurrence).
See the [v18 receipt](../../evals/2026-11-23-exp057-fma-pair-update-mbu-v18.json),
[run log](../../log/2026-11-23-exp057-fma-pair-update-mbu-v18.md), and
[exp-057 record](../../experiments/exp-057/README.md). No submission is ready.

## 2026-11-25 native phase diagnosis

A 64-case classical GF(2^12) screen confirms the native FMA scan's missing
factor: at each simple error root, `omega(r)/(r*P_data(r))` equals
`error(r)*sigma_prime(r)`. This is a diagnosis, not a reversible fix. Keep
work on the same exp-057 lane: derive the `omega/sigma_prime` residues from the
v15 streamed state through the tail key-equation solve, then measure the full
resource and cleanup schedule before submission. See the
[evaluation](../../evals/2026-11-25-exp057-native-phase-derivative.json),
[screen](../../experiments/exp-057/native_phase_derivative_diagnostic.py), and
[run log](../../log/2026-11-25-exp057-native-phase-derivative.md).

## 2026-11-21 live leaderboard refresh

The full Kaggle snapshot at `2026-11-21T12:55:34Z` has 3,519 teams.
`Accelra` is rank 1,202 at `28.14028`; `Z³C¹oherence` leads at `33.34845`,
a `5.20817`-point gap. With the other submitted task costs fixed, matching the
leader requires DQI cost at or below `209.035e9`, about a `39.92%` reduction
from `347.904e9`, or mean `T <= 221,529` at `Q=890` and `R=1.1912605`.
The projected FMA count is `202,075T`, leaving `19,454T` before omitted work.
That projection is not a circuit result: the complete 4+66 width, phase, and
cleanup schedule is still open. No candidate or submission is ready. The
snapshot and exact score model are in
[`evals/2026-11-21-live-leaderboard-125534Z.json`](../../evals/2026-11-21-live-leaderboard-125534Z.json).

## 2026-11-21 branch-history erasure screen — width gate missed

Private kernel version 22 compiles the four-pivot sentinel label with all four
branch bits erased. Across 32 arbitrary GF(2^12) four-sample inputs, labels and
final rank matched, scratch was clean, and phase flips were zero. The circuit
measured `Q=928`, `T=6,212`: it removes four persistent branch bits but peaks
nine qubits wider and 310T higher than version 21, and exceeds `Q=890` by 38.
Close this all-fields-live layout as a candidate. The reversible label relation
is useful only if the full 4+66 schedule reuses payload wires enough to fit the
width gate. The complete schedule remains open; see
[`exp-053`](../../experiments/exp-053/README.md).

## 2026-11-20 live leaderboard refresh

The full Kaggle leaderboard snapshot at `17:14:49Z` contains 3,464 unique
teams. `Accelra` is rank 1,079 at `28.14028`; the leader is Rithvik Redrouthu
at `32.56892`, a `4.42864` point gap. Holding the other submitted task costs
fixed, matching this score requires DQI cost at or below `224.406e9`, about a
`35.50%` reduction from `347.904e9`, or mean `T <= 237,820` for `Q=890` and
`R=1.1912605`. This is score-equivalence math, not a measured leader cost or
a candidate. The exact leaderboard CSV, SHA-256, and score model are recorded
in [`evals/2026-11-20-live-leaderboard-171449Z.json`](../../evals/2026-11-20-live-leaderboard-171449Z.json).

## 2026-11-19 update — packed BM transition screen

`exp-046` exhaustively screened every GF(2) prefix through length 9. At
length 9, direct degree-4 formulas cover only `21 / 29` forward-state output
bits and `24 / 28` full-inverse outputs. The inverse conditioned on an intact
syndrome symbol covers `27 / 27` bits, but that form retains the input symbol
and does not solve the low-space uncompute problem. Keep the direct low-degree
formulation closed; a composed GF(2^12) transition remains unproven and must
pass the complete `R × Q² × T` budget before circuit work.

## 2026-11-19 focused gate — completed

The bounded screen tested whether the packed BM next-feedback value had a
sparse degree-2 formula over field-valued state coordinates. The direct
degree-4 Boolean route was already closed; no public-source sweep or retention
variant was reopened. `exp-047` pre-registered the GF(4)/GF(8) screen and its
optimistic resource ceiling.

The `exp-047` screen found no degree-2 field predictor by prefix length 2 in
GF(4) or GF(8). Close this polynomial-feedback formulation; it does not
establish that every possible BM-state transition is impossible.

The static audit in `exp-048` found no mechanical rewrite capable of closing
the current gap. At the saved rank-1 score target, the 890-qubit candidate
needs mean `T <= 259,947`; the reference circuit measured 367,118. Any next DQI
experiment must use a genuinely different key-equation algorithm and predict
the full reversible `R × Q² × T` cost before implementation. A literature
candidate such as the fast modular approach remains unproven at the required
70-symbol redundancy and space budget.

## 2026-11-19 Hankel block-update gate — no-go

For a BM state with locator `C`, backup `B`, and syndrome `S`, let
`A_j = (C*S)_j` and `U_j = (B*S)_j`. The existing Hankel-35 transform computes
35 fixed-locator outputs in 147 variable field products. A BM correction
`C <- C + α x^m B` changes every remaining discrepancy to
`A_j <- A_j + α U_(j-m)`. Thus batching the fixed-locator dot products does not
remove dynamic work: each correction still needs variable products across the
remaining discrepancy suffix, in addition to the usual locator coefficient
update. Across 70 symbols this remains quadratic and adds the initial `A`/`U`
transforms; it does not improve the direct BM product ledger. Keeping both
35-word streams live also needs 70 field words (840 qubits) unless a separate
in-place schedule proves reuse, while the 890-qubit frontier has only 50
qubits beyond the 840 syndrome bank. Do not build this block formulation.

## 2026-11-19 focused gate — FMA / FDMA at 70 symbols

The target is the source-owned RS(4095, 4025) DQI instance: 70 symbols over
GF(2^12), with 840 syndrome-input qubits. The saved rank-1-equivalent score
target still requires mean `T <= 259,947` at `R=1.1912605`, `Q=890`.

Tang and Han's paper reports classical field-operation totals at redundancy
32 and 128 for FDMA, and 512 for FMA. It does not report reversible Toffoli or
live-qubit counts at redundancy 70. Its classical multiplication totals also
include fixed-coefficient field multiplies, which are linear over GF(2) and
cost no Toffolis when compiled as XOR networks. The paper is a solver candidate,
not evidence that its classical 10x speedup transfers to this DQI score.

For the direct FDMA loop, the generic 70-symbol path has about 14,664
variable-by-variable GF(2^12) products before syndrome transforms or the rest
of decoding. The matrix-vector updates need three products per vector once its
`g`, `W`, and `V` values are data-dependent; the initial `g=1` and `W=1,V=0`
updates are linear. Counting 69 future `(d,g)` updates per first iteration,
36 locator-evaluation points per later iteration, and 36 products to form
`z` gives the estimate. At the measured 42-Toffoli generic multiplier cost in
`exp-005`, that is about 615,888 Toffolis for one forward key-equation pass
alone. This already exceeds the full score gate, so close the direct FDMA
translation. The ledger is `3*C(70,2)-69 + 3*36*69 + 36 = 14,664`.

FMA batches the updates recursively, but its ordinary clean reversible
translation also misses the gate. An optimistic product ledger for Algorithm
6 follows the paper's `70 -> 64 + 6` split, uses a seven-product 2x2 matrix
multiply, uses four variable products per updated vector, and exploits the
known `g=1` values along untouched first branches. This gives about 4,455
dynamic field products, or about 374,220 Toffolis for compute-use-uncompute
at 42 Toffolis per product. That excludes the remaining decoder work. A
direct implementation also has to retain the first-half matrix while solving
the second half. The 840 input qubits leave only 50 scratch qubits under
`Q=890`, and the paper supplies no pebbling schedule showing the intermediate
matrix fits that space. For reproducibility, the product ledger uses
`P(1, pristine)=P(1, updated)=0`. For split `n=a+b`,
`P(n, pristine)=P(a, pristine)+P(b, updated)+2*b+7*(n+1)` and
`P(n, updated)=P(a, updated)+P(b, updated)+4*b+7*(n+1)`. This is an
unresolved live-state estimate, not a lower bound.

**Decision:** no-go for direct FDMA or a straightforward clean FMA port. Do not
build either circuit. Reopen FMA only with a concrete reversible schedule that
proves the complete `R × Q² × T` cost under the saved target; asymptotic
classical complexity alone is insufficient.

For a bounded MBU follow-up, the most optimistic FMA cleanup floor is one
42-Toffoli product per each of 4,455 dynamic field products: 187,110 Toffolis.
Adding the existing 45,045-Toffoli scan leaves only 27,792 Toffolis under the
259,947 gate for every phase correction and other nonlinear operation. This
is a screening ceiling, not an estimate: it assumes measurement-based cleanup
can replace the second product pass, while the 50-qubit workspace still has no
proven schedule. FMA is worth reopening only if both the full cleanup count and
an in-place ≤50-qubit schedule fit those gates.

The product-level MBU assumption is now confirmed with the source-owned
GF(2^12) arithmetic on Kickmix 1.0.0: `mul_xor` followed by `erase_product`
builds to 37 qubits and 42 Toffoli-like operations total. The phase correction
and measurement-based erasure add zero Toffolis. This validates the 42-Toffoli
per-product floor, but does not include FMA rank controls or prove the required
≤50-qubit schedule.

The classical 70-symbol path was checked on deterministic verifier-form
syndromes with 1, 31, and 35 errors. Direct FMA and both block trees (`38+32`,
`64+4+2`) recovered the exact monic locator and evaluator polynomials in all
six cases. This keeps the classical solver plausible; it does not change the
no-go for a quantum circuit without a proven live-state schedule.

The same runs count 79 GF(2^12) coefficients in the materialized 38-point
left basis, or 948 qubits. That state alone exceeds `Q=890`, so a schedule that
stores the whole polynomial matrix is ruled out. This leaves streaming or
in-place reuse as the concrete liveness problem; it is not a lower bound on
other representations.

Source: Tang and Han, [New Decoding of Reed–Solomon Codes Based on FFT and
Modular Approach](https://arxiv.org/abs/2207.11079), Algorithms 4–6,
Appendix A, and Tables I–III. The 42-Toffoli field-multiplier reference is the
measured result recorded in `experiments/exp-005/README.md`; the local MBU
check uses `src/dqi/pro_q2_897/exp/arithmetic/field.py`.

The simplest space-time tradeoff does not fit the score gate. With the ledger
recurrence above, `P(64, pristine) = 3,771` products. If the 64-symbol first
half is erased after updating the final six inputs and recomputed for the root
matrix composition, the total becomes 8,226 products: 345,492 Toffolis plus
the 45,045-Toffoli scan, or 390,537 before other decoder work. This closes
that one-recompute schedule; a compressed or streamed ≤50-qubit schedule is
still unproven.

## Balanced-split count screen (2026-11-19)

Minimizing the same product recurrence over every split `n=a+b` gives
`P(70, pristine)=4,166`, with a `38+32` root split, versus 4,455 for the
power-of-two-plus-tail `64+6` split. At 42 Toffolis per product plus the
45,045-Toffoli scan, that is 220,017T and leaves 39,930T under the saved
259,947T gate. This is a count-only opportunity: the paper establishes FMA
for arbitrary redundancy but does not give this split schedule, and no
≤50-qubit liveness schedule or circuit has been shown. Do not treat it as a
candidate until both are verified.

`exp-049` tested whether the 38+32-style update can simply discard the
original block after producing the right `(d,g)` pairs. It cannot: exhaustive
GF(8), 4+4 enumeration found a maximum preimage of 65, requiring at least 7
side-information bits for that small case. This does not prove a 70-symbol
lower bound; it means a viable schedule must explicitly carry compressed
history in the unused input slots or scratch. The 38+32 root split leaves six
field slots (72 bits) in the 840-bit bank, plus 50 scratch qubits, for that
history. No encoding or complete liveness schedule has been shown.

A follow-up in `exp-049` recorded all sequential branch decisions as well as
the final right-block state. Exhaustive GF(8), six-symbol cases still had
largest preimages 21 (3+3) and 63 (4+2), requiring 5 and 6 additional bits.
Thus one history bit per update is not a complete encoding at these sizes;
this does not give a 70-symbol lower bound or prove that 122 bits are
insufficient.

The vectorized `exp-049` screen exhaustively checked all `GF(8)^8` inputs for
splits `6+2` and `7+1`, including branch history and final right state. Their
largest fibers were 2,177 and 114,940, requiring 12 and 17 additional label
bits; selected entries matched the sequential reference. These cases do not
bound the 70-symbol fiber, but they provide a reproducible small-field screen
for the state width.

Keeping the first three left-side `d` samples reduced those small-case residual
labels to 6 and 9 bits. For the 70-symbol root, the corresponding 36-bit side
state would leave at most 16 qubits for the residual label and overlapping
scratch. A concrete feasibility gate is now to prove the maximum fiber is at
most `2^16` and implement its label reversibly; no 70-symbol bound is known.

A projective encoding screen on all `GF(8)^8` inputs for split `6+2`, with
three left samples retained, reduced the right state by 4 bits but raised the
maximum-fiber label from 6 to 9 bits (64 to 343 inputs). The net saving was 1
bit in this small case; it neither bounds the 70-symbol fiber nor yields a
reversible schedule.

The valid-domain screen also exhaustively covered all 97,119 GF(8), eight-point
error patterns through weight 4, retaining those same three input samples.
Locator recovery had zero failures; the maximum fibers were 1 for split 4+4
and 7 for split 5+3 (0 and 3 residual label bits). The reproducible call is
`screen_valid_error_domain(3, 0b1011, 4, 3)` in `exp-049`; these small cases do
not bound the 70-symbol maximum fiber.

For the 70-symbol root state, 64 right-pair field words plus 70 branch bits
occupy 838 qubits. At `Q=890`, that leaves an absolute 52-qubit ceiling for
additional collision labels and any overlapping scratch. A viable label must
be computed reversibly, and its live width must be reduced further wherever
scan or phase-extraction scratch overlaps. The small-field fibers do not prove
that a label within this budget exists.

## 2026-11-19 public handoff screen — Hengck23

The staged notebook `kaggle/staging/hengck23-dqi-kmb-2026-11-19/dqi-kmb-at-59-56854.ipynb`
was inspected as JSON/text only; no notebook code ran and no circuit archive
was downloaded. The handoff identifies its circuit as an iteration of the
SomeJoint fused-confluent decoder and credits the Apache-2.0 upstream. It says
`generate.py` is omitted. The notebook code only runs the official verifier on
`dqi_iter014.kmb` from a Kaggle dataset, so this is not a reproducible generator.
The staged notebook metadata declares no dataset source or license; its handoff
credit alone does not establish the license for that compiled artifact.

The two result blocks disagree: the handoff table reports zero errors and a
59.846 ratio, while the notebook's embedded verifier output reports one value
error in 102,400 shots, `Q=889`, mean `T=433,784.891`, and cost
`410,274,633,000.49` (`R=1.196731`, ratio `59.56855`). Use the embedded output
as the conservative measurement. That cost is 1.67× the saved rank-1-equivalent
DQI gate (`245.285e9`) and is also worse than the saved best-DQI measurement
(`347.904e9`).

**Decision:** no-go as a candidate. Keep the handoff as a measurement reference;
do not copy its circuit. Its named T-only optimizations save at most a few
thousand Toffolis; the in-place multiplier idea may lower qubit count but has
no demonstrated schedule. Neither closes the current ~107k gap. The next DQI
attempt must still change the key-equation algorithm and prove its reversible
space schedule before circuit generation.

Provenance: [Kaggle discussion 753607](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/discussion/753607).
The staged notebook SHA-256 is `b9c09c6522e2da1a0b19d2584e0e9955001bedebb69e420c7c10fe93027adcc0`.

## 2026-11-19 converter trial — rejected

Replacing `final_decoder.conversion.convert_safe` with the source-owned
`exp/convert/repair.py` path produced `Q=897`, `T_static=488,466`, and
56,996,735 operations. The owned baseline is `Q=897`, `T_static=454,477`, so
this variant is worse; it was not verifier-tested or submitted. Its temporary
517 MB circuit was deleted. Do not retry this converter path.

## 2026-11-19 early-termination I-FDMA screen — no-go

The official verifier samples error weight `e` with mean `31.0467` (median 31);
`77.5%` of shots have `e >= 30`. The 2e-step MA/I-FDMA guarantee in Jiang et
al. assumes error positions lie in `{2t, ..., n-1}`. This verifier instead
samples positions uniformly from `0..4094`, so that guarantee does not apply
to the benchmark as specified. Even under the paper's multiplication ledger,
at `e=31, t=35` I-FDMA needs `18et - 6e^2 + 3e = 13,857` field multiplications;
at the source-owned 42-Toffoli multiplier cost, that is `581,994` Toffolis for
the locator solve alone, above the saved `259,947` target. Close this I-FDMA
route; do not build it. The distribution was computed from the verifier's
`optimal_dqi_weights` formula and `sample_error` implementation in
`kaggle/staging/competition-runtime/verifiers/dqi/verifiers/dqi/verify_submission_dqi.py`.

Source: Jiang et al., [Error Correction Decoding Algorithms of RS Codes Based
on An Earlier Termination Algorithm](https://arxiv.org/abs/2407.19484), Theorem
4 and Table I. This screen does not rule out other key-equation algorithms.

## 2026-11-19 FMA complementary-row screen

`experiments/exp-049/fma_state_compression.py` now reconstructs the
complementary modular-basis row from a normalized low-rank row. Extended
Euclid supplies a determinant-`P` solution; a polynomial correction enforces
the complementary rank and the key equation at common-zero points. Exhaustive
GF(4), four-point checking passed all 256 inputs. Deterministic random checks
passed 256 GF(8), eight-point inputs and 256 GF(2^12), 38-point inputs.

For verifier-form syndromes at weights 1, 31, and 35, the 38-point left block
needed 2, 38, and 38 normalized field words, respectively, plus 32 right-side
input words and no common-zero samples. The largest sampled states occupy 840
qubits and leave 50 under `Q=890`. This counts persistent information only;
the classical correction solve has no reversible liveness or Toffoli ledger.
The three error weights are samples, not a proof over the verifier's complete
input domain. Keep FMA open only for a reversible ≤50-qubit implementation
whose full score gates are measured; no circuit or submission exists yet.

## 2026-11-19 FMA split and complement screen refresh

The read-only Kaggle CLI leaderboard refresh at `2026-11-19 07:25 UTC` still
has `Z³C¹oherence` first at `31.74002`. The current score-equivalence gate is
`T <= 256,943` at `R=1.1912605`, `Q=890`.

`exp-049` now reconstructs and composes the left basis for `4+66`, `8+62`, and
`38+32` on verifier-form samples at `e=1,31,35`. Every composed normalized low
row matches the direct 70-point basis. At `e=31,35`, each split retains 70
field words (840 qubits) and leaves 50 qubits for all scratch and history.
This remains a classical composition check.

A seeded dynamic-taint screen for `e=31,35` counted variable products and
inversions in the reconstruction. Using the in-tree 42T product, 66T inverse,
45T inverse erasure, and the 45,045T root scan gives these sample-path totals:

| Split | FMA products | Reconstruction products | Inverses | Estimated T | Margin to 256,943T |
|---:|---:|---:|---:|---:|---:|
| 4+66 | 4,720 | 71 | 8 | 247,155 | 9,788 |
| 8+62 | 4,585 | 205 | 10 | 247,335 | 9,608 |
| 38+32 | 4,166 | 3,877 | 25 | 385,626 | -128,683 |

The estimate is `42 * (FMA products + reconstruction products) + 111 *
inverses + 45,045`. `poly_divmod()` now reuses one divisor-leading inverse per
division. A separate 1,024-shot screen at e=31 and e=35 found common-zero
correction in 2 shots; the representative cost paths above need none. The
4+66 split is lowest among the tested splits 1–18, but its 9,788T margin must
cover branch/control, common-zero, phase, and cleanup work. This screen does
not compile a reversible circuit, bound the cost over all inputs, or prove
that reconstruction fits the 50-qubit scratch ceiling. Do not treat it as a
score-gate pass; FMA stays open only for a concrete reversible schedule that
verifies against the official scorer.

## 2026-11-20 local FMA pivot-invertibility screen

`experiments/exp-052` checked the per-sample update used by the sequential
FMA recurrence. For distinct points, the update determinant is
`(x_i+x_j)*d_j` on the swap branch and `(x_i+x_j)*g_j` otherwise. The FMA
branch rule selects a nonzero factor whenever the pivot `(d_j,g_j)` is
nonzero. The pre-step basis determinant is a nonzero scalar times the product
of prior point factors, so its evaluation at the next distinct point is
invertible; applied to pristine `(d_i,1)`, it cannot produce a zero pivot.

The checker found no zero pivots and exactly inverted every sampled pair in all
256 pristine GF(4) four-point inputs, all 97,119 valid GF(8) eight-point error
patterns through weight four, and 192 seeded GF(2^12) 70-point DQI inputs at
weights 1, 31, and 35. This supports an in-place data-pair update when its
pivot and branch are available. It does not supply a circuit decomposition or
resolve rank/branch history, complementary-row liveness, the 50-qubit scratch
limit, or the complete Toffoli count. Keep the 4+66 path as a count-only lead
until those gates are met.

An extension in `experiments/exp-052` counted full `(d,g,rank1,rank2)` states
after every sequential step. All states stayed distinct across all 256
pristine GF(4) inputs and all 97,119 valid GF(8), eight-point error patterns
through weight four. Each step updates only later samples, so its pivot pair
remains unchanged to the end; replaying branch predicates from those pivots
and the initial ranks recovers the branch sequence classically. This opens a
branch-replay route, but no reversible replay circuit, scratch bound, or
Toffoli count has been established for 70 symbols.

## 2026-11-20 FMA branch-replay storage gate

`exp-052` now makes the naive replay width explicit. Retaining the expanded
70-pair state means 140 GF(2^12) values (1,680 qubits), above the 890-qubit
limit. Keeping 70 branch-history qubits and two 8-bit ranks beside the
840-qubit compact payload would use 926 qubits before arithmetic scratch.
Kickmix's HMR operation measures in the X basis and returns a random bit with
phase kickback; it does not expose the computed branch bit as a free classical
register ([format semantics](https://github.com/quantumlib/Qualtran/blob/main/docs/kickmix/kickmix_format.md#semantics),
[HMR instruction](https://github.com/tanujkhattar/zkp_ecc/blob/main/docs/kickmix_instruction_set.md#hmr-instruction)).

**Decision:** the naive replay from retained pivots is a no-go at `Q=890`.
Keep the 4+66 FMA estimate open only if a branch oracle can be derived from
the 840-qubit compact payload with a complete <=50-qubit liveness and
Toffoli/phase ledger. The current evidence does not supply that oracle, so
there is still no FMA circuit or score-gate pass.

`exp-052/fma_branch_window.py` then tested a smaller oracle on every valid
GF(8), eight-point pattern through weight four. The key consisted of the
post-step ranks and a contiguous window of pivot pairs around the current
step. The later steps needed up to five pairs; ranks plus one pivot failed.
That rules out the simple local-window replay, not a circuit that extracts
branch bits directly from the compact polynomial payload.

`exp-052/fma_locator_history.py` then grouped all 97,119 valid GF(8),
eight-point patterns through weight four by error-location support and
enumerated every nonzero magnitude assignment. Branch histories vary with
magnitudes: one of 35 weight-three supports has two histories, and seven of 35
weight-four supports have multiple histories (up to five). Reject the
support-only branch-oracle formulation. This small-domain result does not
rule out a magnitude-dependent oracle derived directly from the complete
compact payload. A separate grouping by normalized final low row also found
collisions between branch histories, so that row alone is insufficient. Keep
FMA open only with a complete <=50-qubit and Toffoli/phase schedule.

`exp-052/fma_branch_gate.py` compiles one base-case branch predicate and rank
update to 95 Toffoli-like gates, with a one-bit selector for the sparse
lower-row column of the leaf matrix. For fixed point polynomial `L`, the
selector represents `[L, 0]` or `[0, L]`; `d` and `g` supply the top row.
Repeating that local cell for all 70 leaves costs 6,650T and leaves 3,138T of
the 9,788T remainder. Its local peak is 73 qubits including the pivot pair
and ranks; projecting the pair into the existing 840-qubit payload gives
`Q=889`. This remains an optimistic local ledger: it excludes pivot
generation, FMA-tree composition, and selector liveness during recursive
composition. Kickmix simulated all 262,144 rank/zero-class inputs: output
ranks and selector matched the reference, 32 scratch qubits returned to zero,
and no phase flips occurred. At that point the unresolved gate was a complete
compact-state/liveness and phase schedule; the later rank-invariant refinement
below increases the local remainder but does not supply that schedule.

## FMA leaf branch encoding

Tang and Han's [Algorithm 6](https://arxiv.org/abs/2207.11079) already encodes
each leaf choice in its output matrix: one branch places the nonzero lower-row
polynomial in the left column, and the other places it in the right column.
This gives a concrete place to store the branch result in the matrix
representation instead of allocating a separate history bit per leaf. It does
not yet prove that the recursive matrix composition can consume and clean every
intermediate within `Q<=890`.

Do not assume HMR can clear the branch after the rank and sample updates. On
unrestricted local FMA states, the post-update state need not determine the
branch: over GF(8), pivot `(1,1)`, point difference `1`, ranks `(3,2)` with
sample `(1,2)` on the no-swap branch and ranks `(2,3)` with sample `(2,1)` on
the swap branch both produce sample `(3,2)` and ranks `(3,4)`. A promise-aware
oracle may still exist, but generic measurement-based erasure is not justified
by this update. `exp-052` now compiles a local branch/rank leaf that writes a
one-bit selector for the sparse lower-row column. Recursive liveness and the
phase ledger remain unproved.

## 2026-11-19 18:37 UTC Kaggle leaderboard refresh

The read-only Kaggle CLI top-20 query still shows `Z³C¹oherence` first at
31.74002, with `ThemBones` second at 31.64282. The top score is unchanged, so
the saved DQI gate remains `T<=256,943` at `Q=890` and `R=1.1912605`.

## 2026-11-20 FMA rank-invariant branch-gate refinement

For step `j`, valid ranks satisfy `r1+r2=2j+1`, which makes the branch test
`r1<r2` equivalent to `r1<=j`. The specialized constant comparator costs 79T
and peaks at 72 qubits for one leaf. Across 70 steps it uses 5,530T, saves
1,120T against the 95T general comparator, and leaves 4,258T of the prior
9,788T remainder. The projected total is `Q=888` if the pivot pair is already
inside the 840-qubit payload. The checker covered 19,880 valid rank/zero-class
cases with clean scratch and no phase flips.

This improves only the local branch/rank ledger. It does not generate pivots,
compose the FMA tree, establish selector liveness, or prove the full circuit
fits `Q<=890` and `T<=256,943`.

The exhaustive GF(8) locator-history pass also found 99 normalized final low
rows across 97,119 valid patterns; 8 rows occurred with multiple branch
histories, up to five for one row. A normalized low row alone cannot supply the
selector history.

## 2026-11-20 FMA compact-state branch recovery screen

The same exhaustive GF(8) pass found 97,119 distinct exact 2x2 basis matrices
for 97,119 valid patterns; no matrix was associated with multiple branch
histories. For split `4+4`, the normalized left low row plus the common-zero
exception samples directly recovered all four original left samples and their
branch history in all 97,119 cases. The left recovery state had 512 distinct
values, no history collisions, and required at most two exception samples.
Adding the untouched right input samples yielded 97,119 distinct compact
states, again with no left-history collisions.

For pristine inputs (`g_i=1`), the sample recovery follows the key equation.
When `W(x_i)` is nonzero, `d_i=N(x_i)/W(x_i)`. At a common zero, set
`A=W/gcd(W,N)` and `B=N/gcd(W,N)`: when `d_i A(x_i)+B(x_i)=0`, recover
`d_i=B(x_i)/A(x_i)`; otherwise retain `d_i` as an exception sample. The screen
implements this recovery and replays the 4-step FMA history on every pattern.

This validates the information encoding only for the exhaustive GF(8),
eight-point, weight-at-most-four domain. It does not give a reversible
GF(2^12) circuit, a 70-symbol bound, or a Q/T schedule. The next gate is to
translate the sample recovery and history replay into a reversible schedule
that fits the `4+66` state and remaining resource budget.

### 2026-11-20 factorized-state codec screen

The factorized tuple has at most 14 degree layouts: `deg(G)=0..2`,
`deg(A)<=2-deg(G)`, and `deg(B)<=1-deg(G)` with `B=0` allowed. The selected
low row has rank at most 4 and obeys `d_i W(x_i)+N(x_i)=0`; if `W=0`, then the
degree-at-most-one `N` vanishes at all four public points, forcing a zero row.
Thus `W/G` is nonzero. `G` and `A=W/G` are monic, and the roots of `G` are
among the four public points. The tuple therefore packs into four field words
plus a four-bit layout tag. The
tag fits in the rank register's unused high bits at the four-point split:
rank1 is at most 7, leaving five high bits in its 8-bit register. Pack/unpack
recovered all 4,096 GF(8) inputs with zero collisions; 2,048 seeded GF(2^12)
samples also had zero collisions. This is a classical layout check only; the
reversible tag computation and cleanup are not built.

### 2026-11-20 arithmetic cost screen

The cost screen separates branch-history recovery from complementary-row
reconstruction. Across all 4,096 arbitrary GF(8) four-sample inputs, low-row
normalization/factorization, sample recovery, and branch replay use at most four
factorized words and have a 5,118T arithmetic-only proxy (median 4,488T). The
full block transform still needs the complementary row; adding its separate
6,138T proxy and 252T low-row composition gives an 11,508T screen. Even if
charged additively, this is below the current 54,868T projected margin, but the
count can overlap the FMA ledger and excludes controls, live scratch, phase,
and cleanup. The next gate is a compiled reversible encoder/decoder and a
measured 4+66 schedule; no full circuit exists yet.

## 2026-11-20 4+66 fused factorization — width lead, circuit open

An exhaustive screen over all 4,096 arbitrary GF(8) four-sample vectors at
points `{0,1,2,3}` recovered each vector from the normalized low row plus its
common-zero exception samples, with no state collisions. The exception-count
distribution was 0: 2,570, 1: 1,232, and 2: 294. This is small-field evidence;
the stronger bound follows from the four-point rank invariant: the row ranks
sum to 9, so the normalized low row has rank at most 4. Its polynomial pair
`(W,N)` has `deg(W)<=2`; if `N` is nonzero, `deg(N)<=1`. Therefore
`gcd(W,N)` has degree at most 2 and has at most two distinct common-zero roots.

Let `G=gcd(W,N)`, `A=W/G`, and `B=N/G`. Store the monic `G` without its leading
1, the coefficients of `A` and `B`, and the original `d_i` sample at each
public point where `G(x_i)=0`. The root positions are derived from `G`, so no
location mask is needed: the FMA basis determinant is the node polynomial, so
`G` divides it and all roots are among the four public points. At every other
point, `d_i*A(x_i)+B(x_i)=0`; coprimality gives `A(x_i)!=0`, so recover
`B(x_i)/A(x_i)`. This factorized state reconstructs the original four samples
and therefore their FMA branch history.

The exhaustive arbitrary GF(8) screen found 4,096 distinct factorized states,
zero collisions, at most two common-root samples, and at most four coefficient
and sample words. The factorized state is injective on the full four-sample
domain. A concrete fixed-width label is the four recovered sample values in
point order, totaling 48 bits for GF(2^12). The exhaustive GF(8) screen checks
that every factorized state maps to a distinct label. This removes the separate
24-to-27-bit sidecar and avoids serializing the variable-length polynomial
tuple. The in-place reversible circuit that computes the label remains
unbuilt.

If that code is implemented in-place, the persistent 4+66 payload remains
840 qubits. The existing branch cell's additional 48-qubit workspace projects
`Q=888` when its pivot pair is available inside the payload, leaving two
qubits under the gate. This is a width lead, not a schedule proof: the encoder
and decoder's scratch, Toffoli cost, phase cleanup, and pivot liveness remain
open. The branch kernel plus prior sampled path leaves 4,582T for this and all
other omitted work.

Explicit sidecars remain over width if live through the branch cell: `Q=915`
for a 27-bit sorted form, `Q=914` for a 26-bit dense capacity, and `Q=927` for
the 39-bit fixed-position form. Their old extraction ledger is only a fallback
estimate and does not apply to the fused factorization. In that ledger, six
direct clean-ancilla 12-bit zero tests cost 252T; fixed-position copies give a
1,029T listed subtotal, while two packed value writes give 1,017T before
unaccounted routing. Neither subtotal is reconciled against dynamic-taint
products, output selection, phase correction, or cleanup.

## 2026-11-20 zero-workspace GF(2^12) product audit

The existing `field.py::mul_xor0` accumulates a product into a separate target
register without allocating private qubits. For `GF(2^12)`, its tensor has 42
terms and the implementation applies one CCX per term, so the source-level
cost is 42 Toffoli-like gates per product. This can remove the multiplier's
private ancilla from a schedule; it does not remove the separate 12-bit output
register required by the accumulator or prove that the FMA update is in-place.

The local Kickmix 1.0.0 check compiled the product cell at 36 qubits and 42
Toffoli-like gates; eight GF(2^12) sample products matched and both operands
were preserved. A forward FMA pair update compiled at 72 qubits and 84
Toffoli-like gates in each branch specialization; four sample pairs passed in
each branch. That cell keeps the 24-bit output pair separate from the input
pair, so it does not establish an in-place schedule. The remaining gate is a
complete pair-update schedule with output-register liveness, phase cleanup,
and branch/rank storage under the 50-qubit scratch ceiling.

## 2026-11-20 pivot-normalized FMA recurrence

`exp-053` tests a row-normalized FMA update. For no-swap, divide the first row
of `[[g_j,d_j],[0,delta]]` by nonzero `g_j`; for swap, divide the first row of
`[[g_j,d_j],[delta,0]]` by nonzero `d_j`. These are nonzero row scalings, so
they preserve row rank and pivot zero classes. Exhaustive GF(8), four-sample
inputs and 48 seeded GF(2^12), 70-symbol DQI samples matched the reference
branch history, row ranks, and normalized low row.

For a swap branch, one controlled input swap followed by the shared update
`d ^= r*g; g *= delta` yields the FMA-ordered output pair; a second pair swap
would incorrectly reverse the output. The one input swap costs 12T per suffix
update. The ratio is computed and uncomputed with two products per pivot. The
existing in-place inverse uses 66T forward and 72T to restore the pivot; pivot
orientation adds 24T. Thus the 70-symbol arithmetic ledger is 2,415 pair
products, 140 ratio products, 70 inverse/restore pairs, 28,980T of pair input
swaps, and 1,680T of pivot swaps: 147,630T.

`exp-053` compiled the corrected one-pair cell at `Q=888, T=300`, preserving 16 rank
bits and a branch bit. Kickmix simulated 32 valid pivot cases across both
branches; pivot values were restored, all 31 scratch qubits were clean, and no
phase flips occurred. This cell does not build the 4+66 state schedule. Adding
the existing sampled reconstruction ledger, 45,045T scan, and 5,530T
branch/rank cell projects 202,075T, leaving 54,868T under the saved gate. This
still excludes the 4+66 width schedule and uncounted phase work.

The direct pair bank remains 1,668 qubits before ratio workspace, 778 above
`Q=890`. The remaining gate is a complete 4+66 schedule that generates and
consumes each pair from the compact payload and proves ratio, branch, rank,
phase, and workspace liveness. The corrected count is still a projection; no
full circuit or submission exists.

### Pivot replay from one-word samples

`exp-053` now checks a streamed pivot calculation: for pivot `j`, replay the
prior normalized updates from pristine `d_j` using the earlier ratios and
branches. The exact variable-product count is `sum(j)=2,415`, equal to the
direct suffix-update count, so this avoids keeping the expanded pair bank if
the ratios can replace the consumed samples. Replay matched the direct
recurrence on all 4,096 arbitrary GF(8) four-sample inputs and 48 valid
GF(2^12), 70-symbol DQI samples.

The ratio sequence alone is not a reversible encoding: the GF(8) screen has
3,052 ratio vectors for 4,096 inputs, with a maximum fiber of 8 and up to 8
branch histories per vector. In the 48 sampled DQI cases, weight-one inputs
had as many as 69 zero ratios. The branch/phase label therefore cannot be
handled as a zero-ratio bitmask without a stronger bound. No circuit liveness
or output-generation schedule has been established; the remaining task is a
compact reversible label and its cleanup within the 50-qubit workspace.

The screen now also shows that ratios plus the complete branch history label
all 4,096 GF(8) four-sample inputs uniquely. A rank-comparison default does not
make that history sparse: the sampled GF(2^12) cases had up to 69 branch
exceptions at weight 1, 8 at weight 31, and 1 at weight 35. This is not a
bound for all valid inputs and does not supply the reversible encoder. Across
16 samples per weight, the screen saw 2, 1, and 3 distinct exception masks at
weights 1, 31, and 35. The final rank pair did not identify the mask at weights
1 or 35, so the small sample does not reduce the history to rank state alone.

`normalized_fma.py::decode_replayed_samples()` gives an explicit inverse when
the four branch bits are kept with the first four pivot ratios. The branch bit
selects projective coordinates `[r_j:1]` or `[1:r_j]`; reversing each prior
update's Möbius matrix recovers `d_j`. This passed all 4,096 arbitrary GF(8)
four-sample inputs and the first four samples of all 48 GF(2^12) DQI cases.
The four history bits fit in the five upper rank bits unused after the prefix.
This is a classically reversible layout; the in-place gate encoder/decoder and
full 4+66 schedule remain unbuilt.

## 2026-11-20 rank-exception transition screen

`exp-054` checked whether rank-default exceptions have a low-transition mask.
Across all 4,095 nonzero error locations at magnitude 1, it found 70 masks with
at most two transitions; 21 scalar checks across selected magnitudes matched.
Across 50,000 valid samples at each of weights 31 and 35, it found 258 masks.
Weight 31 reached nine transitions once; weight 35 reached four.

An enumerative code for masks with at most nine transitions requires 37 bits,
18 above the optimistic 19-qubit room left by the `Q=871` pair-cell
projection. A codebook for the 258 observed masks needs nine bits, but the
sample does not bound the full valid domain and provides no reversible encoder.
Close the generic transition-count encoding route; do not spend another screen
on transition histograms unless a structural bound appears. Keep the FMA path
focused on a direct branch oracle or a reversible 4+66 compact-state schedule
with a complete width, Toffoli, and phase ledger.

## 2026-11-20 fixed-shape sample decoder width gate

`exp-053/fixed_shape_decoder.py` compiled the out-of-place decoder for
`G=1`, `deg(A)=2`, `deg(B)=1` in private Kaggle kernel version 5. All 32
generated valid cases recovered the four samples, preserved the coefficient,
rank, and branch inputs, left 55 scratch qubits clean, and had zero phase
flips. The cell costs `Q=952`, `T=612`: 840 payload + 8 rank + 1 branch + 48
fresh output + 55 scratch, exceeding the `Q=890` gate by 62.

Close the out-of-place decoder layout. This does not rule out an in-place
permutation or a streamed schedule that reuses payload words. Continue only
with such a layout and include its tag, phase, and cleanup costs in the full
4+66 ledger. The helper is the unchanged Apache-2.0 port attributed in
`src/dqi/NOTICE`; the run was private and the helper hash matched its manifest.

### Three-sample streaming-label screen

The source-owned `screen_fixed_shape_streaming_labels()` exhaustively checked
1,568 GF(8) states for `G=1`, monic irreducible `A` of degree 2, and `B` of
degree 1. Across all eight layouts formed by choosing three sample points and
retaining either `A` coefficient, each key has a maximum fiber of four.
Every layout has collisions with identical four-point branch history. A tag
depending only on the discarded coefficient needs at least three bits, since
the induced conflict graphs need 6 or 7 colors.

The follow-up screen checked every GF(8)-linear form `u` of the three retained
samples and retained coefficient, then every fixed rank-2 GF(2)-linear
projection of `discarded * u(key)`. No two-bit label exists in this family for
any of the eight layouts. Close the coordinate encoding, its branch-history
and coefficient-only tags, and this fixed-projection bilinear family. A
follow-up also exhausted all 32,768 affine GF(8)-field-linear kernel functions
`v(key)=c+sum(lambda_i*key_i)`, allowing a different rank-2 projection per
key; none labels the collision fibers. Arbitrary GF(2)-linear/nonlinear
kernels, higher-degree tags, or a different residual representation remain
open. None of these GF(8) screens bounds GF(2^12).

Keep the next gate on the source-owned in-place four-pivot ratio/history map,
then integrate it into the complete 4+66 width, Toffoli, phase, and cleanup
schedule. The current evidence proves classical reversibility, not a circuit.

## 2026-11-20 constant-aware four-point recovery cost

The same 48 seeded GF(2^12) DQI prefixes were recounted after specializing
operations whose operands are public constants. Multiplication by the four
evaluation points is a GF(2)-linear map, and division by the monic gcd can
skip its fixed leading coefficient. The raw mean/max was 4,822.25/5,238T;
the constant-aware mean/max is 2,876.125/3,114T. Both paths recovered the same
factorization, four samples, ratios, and branches. These costs begin after the
low row is formed and normalized, omit CNOTs and circuit liveness, and do not
establish a reversible encoder or the full 4+66 schedule. See
[`exp-053`](../../experiments/exp-053/README.md) for the reproducible screen.

## 2026-11-20 factorized-state tag width lead

The existing shape ID uses four bits, but its payload-conflict graph over all
4,096 arbitrary GF(8) four-sample inputs has 9 edges and chromatic number 3.
A deterministic three-color map gives a two-bit tag with zero label collisions
on that exhaustive domain. The same map had zero collisions across 48 seeded
GF(2^12) DQI prefixes. This can save two tag qubits per live block if the
color decoder is built. For the pristine four-point prefix, however, the
four-bit shape ID already fits in unused high bits of the existing rank
register, so reducing it to two bits does not itself lower total qubit count.
The map is not a GF(2^12) proof or an in-place circuit. The 4+66 width and
phase schedule remain open.

A conservative audit of all four-word support patterns accepted by the generic
packer has chromatic number 7, requiring a three-bit tag. It deliberately
ignores gcd, node-root, coprimality, and modular-basis constraints, so it is an
upper bound for arbitrary packed tuples rather than the true DQI image. The
two-bit color code is usable only after proving those constraints reduce the
GF(2^12) image conflict graph.

## 2026-11-20 projective sentinel label map

`exp-053/inplace_ratio_codec.py` replaces the duplicate zero ratio at each
pivot with the omitted projective ratio. For a fixed invertible prefix matrix
and rank-order flag, this is a permutation of GF(2^m); the prefix determinant
stays nonzero for distinct evaluation points. Since prior labels determine the
prefix matrix and rank order, induction proves the full 70-symbol
sample-to-label map is a permutation for arbitrary inputs over GF(2^m). A
classical run round-tripped 64 seeded arbitrary GF(2^12) vectors and matched
the independent recurrence; the prior 48 valid DQI cases also pass.

The fixed-determinant collision only rejects `(matrix, sample) ->
(updated_matrix, label)` when the matrix is treated as independent input. It
does not contradict the full triangular map. The reversible gate circuit,
workspace liveness, phase cleanup, and 4+66 cost remain unbuilt for the full
70-symbol map.

## 2026-11-20 four-pivot sentinel gate result

Private Kaggle kernel version 21 compiled the in-place sentinel relabeling for
the first four pivots. It matched the classical codec on 32 arbitrary
GF(2^12) four-sample inputs, preserved the explicit branch history and other
66 payload words, cleaned all 71 scratch qubits, and had zero phase flips.

The measured circuit is `Q=919`, `T=5,902`, versus `Q=902`, `T=3,200` for the
ratio/history encoder. The sentinel transform adds 17 qubits and 2,702
Toffoli-like gates while retaining all four branch bits; it exceeds the
`Q=890` gate by 29 qubits. Do not carry this explicit-history layout into the
full 4+66 schedule. The useful next gate is a reversible branch-history eraser
with a width projection under 890 before another full-path build. Results and
limits are in [`exp-053`](../../experiments/exp-053/README.md).

## 2026-11-20 field-growth screen for the shape tag

`exp-055/shape_tag_field_growth.py` first rebuilds the pristine four-point
payload-conflict graph. It exhausts GF(8) and GF(16), then checks 65,536
four-tuples from `0..15` with competition GF(2^12) arithmetic and points
`0,1,2,3`. The existing three-color map has no collisions in those runs.

The follow-up applies the map to a real transformed 4+4 context with left
input `(1,6,1,6)`, points `4,5,6,7`, and the rank pair produced by the left
block. Exhaustive GF(8) checking gives 22 conflict edges and chromatic number
5; the old three-color map has 274 same-color collisions. For example, the
same payload `(5,7,0,0)` represents shape IDs 10 and 4, both color 0, for
distinct right inputs `(0,0,0,5)` and `(0,1,7,7)`. This rejects repeating the
pristine prefix map across blocks. In the corresponding GF(2^12) run over
`0..15` values, no collisions appeared, but 61 states fell outside the
current codec catalog. That subset does not establish a full-field result.

The two-bit prefix tag is therefore not a 34-qubit saving across 17 blocks:
the pristine tag already occupies unused rank bits, and its blockwise
extension fails the exhaustive small-field gate. Reproduction and limits are
in [`exp-055`](../../experiments/exp-055/README.md).

## 2026-11-26 half-GCD gate — close at degree 35

Using the current exp-082 portfolio, the score-equivalent DQI gate is
`T <= 278,784.97` at `Q=900` and `R=1.1912604648`. That is an 11.81%
reduction from the unchanged DQI's `316,131.22` mean Toffolis; the leader score
is `34.50408`, not a measured leader component cost. See the
[gate receipt](../../evals/2026-11-26-dqi-score-equivalent-gate.json).

The exp-057 direct-RHS EEA screen measures `174,672T` mean (`195,612T` max)
for the degree-at-most-35 GF(2^12) Forney-residue problem
([receipt](../../evals/2026-11-25-exp057-forney-polynomial-inverse.json)).
Combining its mean with the `130,410T` v18 pair-update subtotal gives an
optimistic `305,082T`, still `26,297T` above the live gate before other
work. Even with zero overhead, the EEA stage would need to fall to `148,375T`
(15.1% below its measured estimate). The screen's error-root/residue inputs
are also not mapped from the 70 syndrome-derived FMA samples; the receipt is a
classical operation count, not a reversible circuit.

Half-GCD is asymptotically `O(M(d) log d)` field operations, but that does not
establish a gain at this degree. FLINT's finite-extension-field polynomial
GCD implementations use ordinary Euclid below degree 80–120 and switch to
half-GCD above, placing degree 35 below their practical crossover. The fast
polynomial multiplication model in van der Hoeven's analysis also assumes
roots of unity that GF(2^12) does not provide in characteristic two. See the
[FLINT algorithm/source notes](https://github.com/flintlib/flint/blob/main/doc/src/algorithms/polynomials/gcd.md)
and [van der Hoeven's half-GCD paper](https://www.texmacs.org/joris/gcd/gcd.pdf).

The optimistic FMA subtotal is forward-CONVERT + the remaining residue scan
(the 70-point prefix is already handled) + v18 pair updates:
`69,220 + 44,275 + 130,410 = 243,905T`
([cost split](../../evals/2026-11-23-exp057-convert-cost-split.json),
[v18 update](../../evals/2026-11-23-exp057-fma-pair-update-mbu-v18.json)).
It leaves `34,837.57T` under the live tie gate and omits reverse CONVERT.
The native FMA phase still mismatches 30 of 64 classical cases; the derivative
identity repairs those cases classically, but no reversible correction has
been built or costed
([phase receipt](../../evals/2026-11-25-exp057-native-phase-derivative.json)).

The direct-RHS EEA estimate for `omega / sigma_prime` is `174,672T` mean.
With the `130,410T` v18 pair updates, the optimistic subtotal is `305,082T`,
`26,339T` above the live tie gate, before complete input mapping and
cleanup. It is not a reversible circuit or a candidate
([EEA receipt](../../evals/2026-11-25-exp057-forney-polynomial-inverse.json)).

The existing per-position `phase_inverse36_pivot` route costs `36T` for each
of the 4,095 Chien positions, or `147,420T`, against `34,837.57T` remaining.
Close this direct insertion; the count uses the measured helper cost in the
[exp-057 record](../../experiments/exp-057/README.md) and is not a lower bound
on an integrated phase algorithm.

For a packed list of 35 roots with all phase operands available, the same
helper costs `1,260T`, leaving `33,577.57T` for root extraction and omitted
work. The current scan emits no root list. A straightforward one-hot compactor
would spend `860,160T` just writing root-coordinate bits (`24,576` set bits
across GF(2^12)'s nonzero elements, times 35 slots), before pointer updates,
mask access, or cleanup. This closes that layout only; it is not a lower bound
on other root encodings.

**Decision:** close half-GCD and park the current EEA phase implementation;
do not submit it. Reopen the DQI path only if a source-owned, reversible phase
correction fits the `34,837.57T` remaining budget and composes with the full
decoder under `Q <= 900`, followed by official verification. No root compactor
within that budget has been shown. These are feasibility gates, not
lower-bound proofs.

## 2026-11-27 provenance correction

Exp-073/074/082 reused DQI and Invsqrt inputs from Tony Li's task-generator
dataset. Exp-056 had already rejected that dataset because its generators
reconstruct released KMX stages byte-for-byte. Keep exp-082's score as a
historical measurement only; it is not a source-owned candidate. The
`278,784.97T` tie figure above is conditional on exp-082's portfolio and is not
the active source-owned gate. Do not reuse those circuits; recompute the score
gate around an eligible, independently generated portfolio. Using exp-065's
eligible component costs, the current conditional target is `205,608.39T` at
`Q=890`, versus `356,677.49T` mean in exp-063. This target assumes exp-065's
other task costs and repetition factor remain fixed; see the eligible gate in
[`evals/2026-11-26-dqi-score-equivalent-gate.json`](../../evals/2026-11-26-dqi-score-equivalent-gate.json).

## 2026-11-26 published BM cost gate

The optimized published BM DQI circuit is closed as a direct port: its
`440,000T`, `Q=1,837` resource point is `6.50×` the current rank-1 tie gate
under `R × Q² × T`. The 19-qubit exception stack solves the history-storage
problem but does not meet this competition's score gate at the reported width.
See the [cost receipt](../../evals/2026-11-26-bm-published-cost-gate.json) and
[log](../../log/2026-11-26-bm-published-cost-gate.md). This closes only the
published resource point, not every possible BM redesign.
