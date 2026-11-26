---
id: exp-045
title: Streaming Berlekamp-Massey state-space screen for DQI
task: dqi
tests: tests/test_exp045_bm_state.py; src/dqi/pro_q2_897/exp/convert/hankel_check.py; experiments/exp-045/hankel_locator_screen.py
status: no_go_published_cost_gate
result: the published reversible BM decoder is complete but costs 442,397T at 1,837 qubits; direct port misses the current eligible Q²T gate by 9.17×
---

# Streaming Berlekamp-Massey state-space screen

## Target

The current retained portfolio scored `28.14028`; the Kaggle CLI snapshot at
`2026-11-18T16:00:48Z` placed team `Accelra` at rank `752 / 3332`, while the
leader scored `31.61727`. With inverse and chemistry fixed, matching that
score requires the DQI cost to fall from `347.904e9` to about `245.285e9`.

At `Q=890` and `R=1`, that target is roughly `310k` mean Toffolis. Keeping the
current inferred `R≈1.191` tightens it to about `260k`. A direct 70-round
Berlekamp-Massey count has about 1,225 discrepancy products plus 1,225
coefficient-update products: `102.9k` Toffolis at 42 per GF(2^12) product for
one pass, before inversion, phase evaluation, and the work needed to restore
the syndrome input. The same algorithm with two additional 35-symbol state
registers reaches roughly `Q=1,730`, where the DQI `Q²×T` cost loses much of
that advantage.

## Hypothesis

The packed Berlekamp-Massey state may fit in the already-required 70 syndrome
registers. After `k` input symbols, the active nonconstant coefficients in the
connection and backup polynomials use `deg(C)+deg(B)` GF(2^12) words. Small
field enumeration suggests this is at most `k`. The packed state keeps the
active coefficients of `C` and `B`, their nominal degrees, the shift, and the
previous discrepancy.

If a reversible update can compute the next discrepancy from this packed state
without retaining the raw syndrome prefix, it could keep `Q` near the current
890-qubit frontier while using BM's much lower nonlinear-operation count.

## Evidence and limits

`tests/test_exp045_bm_state.py` checks all prefixes for GF(2) sequences through
length 12, GF(4) through length 7, and GF(8) through length 6. It also checks
seeded length-70 sequences over the competition's GF(2^12) polynomial basis
(`0x1053`). Across 128 sequences and every prefix, `deg(C)=L`, the coefficient
arrays use at most 69 field words, and the packed state including the 12-bit
previous discrepancy and shift uses at most 847 bits. This is seven bits over
the 840-bit syndrome bank, and is sampled evidence rather than a worst-case
bound.

The tested shift-elision identity
`shift = processed + 1 - L - deg(B)` is false even on a valid GF(2^12)
two-error power-syndrome input. With roots `[2, 2089]` and magnitudes
`[3436, 1351]`, the first syndromes are `[1, 0, 1]`; after three symbols the
BM state has `shift=1`, `L=2`, and actual `deg(B)=0`, so the identity predicts
2. Keep the shift counter in this state encoding unless a different reversible
encoding is established. The regression check is in
[`tests/test_exp045_bm_state.py`](../../tests/test_exp045_bm_state.py).

The exhaustive [`feedback_degree_screen.py`](feedback_degree_screen.py) checks
all GF(2) prefixes of lengths 5 through 12. The next BM feedback term has no
affine or quadratic formula at any tested length. Degree-4 formulas fit the
packed-state image through length 8, but fail for lengths 9 through 12. At
length 12 the exact check covers all 4,096 prefixes and 33 state coordinates
(26 nonzero coordinates). This rules out a direct degree-4 feedback formula
at the longer tested prefixes; it does not rule out a composed reversible
transition or a higher-degree formula.

The existing in-place Hankel primitive at
`src/dqi/pro_q2_897/exp/convert/hankel_check.py` also passes its local check:
700 triangular forward/reverse cases and 100 triangular Hankel-35 round trips
with `B_35 = 1` and `B_(>35) = 0`. A fixed 35-by-35 transform uses 147
GF(2^12) products (6,174 Toffolis forward; 12,348 for the pair), with no
extra transform words. A block method could reduce discrepancy convolution
cost, but this does not directly replace 70 BM rounds because the locator
changes after each discrepancy.

## 2026-11-26 block/Hankel continuation

The added H70 check uses an anti-triangular Hankel matrix with `B_70 = 1` and
`B_(>70) = 0`. One seeded GF(2^12) sample matches direct multiplication and
round-trips through the inverse: 363 field products (15,246T) per direction,
or 30,492T for the pair. The coefficient sequence is external to the
70-symbol input vector. This is a primitive check, not the full BM key-equation
matrix: that matrix needs the nonzero syndrome terms through `S_69`.

For a known locator degree `e`, the block key equation is
`H_e[i,j] = S_(i+j+1)`, `H_e x = [S_(e+i+1)]`, where
`x[j] = lambda_(e-j)`. A deterministic valid-syndrome sample at each of
`e = 1, 17, 35` recovers the same locator as standard BM. The direct dense
Gaussian solve at `e=35` needs 22,050 non-unit field products (926,100T at
42T/product), excluding pivot inversions, phase, and cleanup. It also
materializes 1,225 field words (14,700 qubits). This is a no-go for the dense
solver at the current `Q=900`, `T<=278,742.57` rank-1 tie gate; it is not a
lower bound on a structured solver.

The degree is supplied to this solve. Unknown-degree detection, singular pivot
branches, reversible cleanup, and a low-space structured solve remain open.
Do not treat this fixed-degree classical solve or the H70 primitive as a
candidate. The next gate is one degree-independent structured update that
matches BM on verifier-form inputs and has a complete `Q`/`T` schedule below
the live score gate.

A primary-source block-generator construction computes a matrix-BM generator
whose determinant is the scalar locator, but it requires `b-1` more scalar
sequence elements than scalar BM. At maximum degree `t=35`, applying `b=2`
therefore needs at least 71 symbols, while DQI provides 70 (inference from the
paper's stated overhead). Close this documented block-size-2 route for the
full correction radius; only a no-extra-syndrome structured update remains in
scope. See [Kaltofen, “What parallel computations I do today,” PASCO 2010, §2.2](https://www.csd.uwo.ca/~mmorenom/Publications/pasco2010.pdf).

This is only a state-space screen. The model computes each discrepancy from the
original syndrome prefix, so it does **not** yet provide the required local
reversible transition. Injectivity on small fields is evidence, not a proof
for length 70, and no circuit has been built or submitted. The published
high-space BM comparison and its `Q² × T` cost are recorded in
[`exp-043`](../exp-043/README.md); its transition-reconstruction technique is
not the same as proving this packed state can replace the syndrome history.

The standard half-GCD route remains a no-go for implementation until a length-70
operation count shows a real reduction. Its asymptotic bounds depend on fast
polynomial multiplication, and the paper's radix-2 FFT model requires power-of-2
roots of unity; GF(2¹²) has multiplicative group order 4,095, so that model does
not apply directly. The source gives no crossover or reversible-circuit cost at
this size. A custom block update using the existing Hankel-35 transform remains
unproven. See [van der Hoeven and Lecerf, *Optimizing the half-gcd algorithm*](https://www.texmacs.org/joris/gcd/gcd.html).

## Decision (2026-11-27)

The primary-source follow-up found an exact reversible BM decoder for this
syndrome task. Its complete circuit includes the locator, MBU phase, evaluator,
scan, syndrome restoration, and cleanup, but measures `442,397T` at `Q=1,837`.
That is `9.17×` the current eligible `Q²T` allowance. Close the direct BM/Hankel
route. Reopen it only with a concrete adaptation whose complete schedule fits
`Q=890`, `mean T <= 205,608.39`, including phase, restoration, and cleanup. See
[`lit-reversible-bm-fit`](../../literature/papers/lit-reversible-bm-fit.md).
