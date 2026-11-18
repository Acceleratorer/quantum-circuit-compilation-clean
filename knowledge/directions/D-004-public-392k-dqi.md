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

