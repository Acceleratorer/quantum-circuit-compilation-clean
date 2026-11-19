---
id: D-004
title: Improve the source-owned DQI decoder with a new key-equation algorithm
status: active
tasks: dqi, all
last_checked: 2026-11-19
---

# D-004: improve the source-owned DQI decoder

The public 392k decoder and hybrid portfolio are measurement references only.
The standing user decision forbids submitting or copying downloaded circuits;
the archive is not a candidate until an attributed source-owned generator
reproduces it. Existing product-retention variants have already been screened.

The active path is a source-owned DQI decoder with a genuinely different
key-equation algorithm. Keep the official verifier's salted failure rate in
the score model, and require the full `R × Q² × T` budget before building a
candidate. The latest score-equivalence estimate is `242.451e9`; at
`R=1.1912605` and `Q=890`, the DQI gate is `T <= 256,943` (see the current
leaderboard refresh below and the saved score model in the mid-competition
milestone).

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
| 4+66 | 4,720 | 71 | 18 | 248,265 | 8,678 |
| 8+62 | 4,585 | 205 | 31 | 249,666 | 7,277 |
| 38+32 | 4,166 | 3,877 | 145 | 398,946 | -142,003 |

The estimate is `42 * (FMA products + reconstruction products) + 111 *
inverses + 45,045`. The 4+66 split is lowest among the tested splits 1–18,
but its 8,678T margin must cover branch/control, phase, and cleanup work. This
screen does not compile a reversible circuit, bound the cost over all inputs,
or prove that reconstruction fits the 50-qubit scratch ceiling. Do not treat
it as a score-gate pass; FMA stays open only for a concrete reversible schedule
that verifies against the official scorer.
