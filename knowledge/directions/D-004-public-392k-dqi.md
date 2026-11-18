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
candidate. The latest saved rank-1-equivalent target is `245.285e9`.

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

Source: Tang and Han, [New Decoding of Reed–Solomon Codes Based on FFT and
Modular Approach](https://arxiv.org/abs/2207.11079), Algorithms 4–6,
Appendix A, and Tables I–III. The 42-Toffoli field-multiplier reference is the
measured result recorded in `experiments/exp-005/README.md`.

