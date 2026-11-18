---
id: exp-045
title: Streaming Berlekamp-Massey state-space screen for DQI
task: dqi
tests: tests/test_exp045_bm_state.py; src/dqi/pro_q2_897/exp/convert/hankel_check.py
status: feasibility_screen
result: packed BM state is injective and fits the processed-prefix coefficient budget in exhaustive small-field checks; no reversible circuit yet
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
field enumeration suggests this is at most `k`, and that the packed state
(`C`, `B`, their degrees, `L`, shift, and previous discrepancy) uniquely
encodes the full processed prefix.

If a reversible update can compute the next discrepancy from this packed state
without retaining the raw syndrome prefix, it could keep `Q` near the current
890-qubit frontier while using BM's much lower nonlinear-operation count.

## Evidence and limits

`tests/test_exp045_bm_state.py` checks all prefixes for GF(2) sequences through
length 12, GF(4) through length 7, and GF(8) through length 6. It also checks
seeded length-70 sequences over the competition's GF(2^12) polynomial basis
(`0x1053`). Across 128 sequences, `deg(C)=L`, the coefficient arrays use at
most 69 field words, and the packed state including the 12-bit previous
discrepancy and shift uses at most 847 bits. This is seven bits over the
840-bit syndrome bank, and is sampled evidence rather than a worst-case bound.

The exhaustive [`feedback_degree_screen.py`](feedback_degree_screen.py) checks
all GF(2) prefixes of lengths 5 through 12. For each length, the next BM
feedback term has no affine or quadratic Boolean formula over the packed
state bits. This rules out a single low-degree feedback expression; it does
not rule out a composed reversible transition or a block algorithm.

The existing in-place Hankel primitive at
`src/dqi/pro_q2_897/exp/convert/hankel_check.py` also passes its local check:
700 triangular forward/reverse cases and 100 Hankel-35 round trips. A fixed
35-by-35 transform uses 147 GF(2^12) products (6,174 Toffolis forward; 12,348
for the pair), with no extra words. A block method could reduce discrepancy
convolution cost, but this does not directly replace 70 BM rounds because the
locator changes after each discrepancy.

This is only a state-space screen. The model computes each discrepancy from the
original syndrome prefix, so it does **not** yet provide the required local
reversible transition. Injectivity on small fields is evidence, not a proof
for length 70, and no circuit has been built or submitted. The published
high-space BM comparison and its `Q² × T` cost are recorded in
[`exp-043`](../exp-043/README.md); its transition-reconstruction technique is
not the same as proving this packed state can replace the syndrome history.

## Next gate

Derive either an explicit reversible local transition from the packed state
and next syndrome symbol, or a block locator update that can use the Hankel-35
transform. Include the inverse that restores the input. Count the complete
forward, phase-evaluation, and uncompute Toffolis and peak qubits before
implementing the circuit. The candidate must beat `R×Q²×T = 245.285e9`;
isolated multiplier savings do not pass the gate.
