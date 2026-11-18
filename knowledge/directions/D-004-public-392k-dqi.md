---
id: D-004
title: Promote the public 392k DQI decoder, then recover its generator
status: active
tasks: dqi, all
last_checked: 2026-11-19
---

# D-004: public 392k DQI decoder and hybrid frontier

The 392k decoder is the largest verified DQI gain found in the current cache. The current package pairs it with the lower-cost public invsqrt and chemistry members from the Attabeezy frontier, reaching a member-level local estimate of 25.4495384012. Submit that hybrid once quota allows, then spend research time on one of two paths:

1. recover or reconstruct a deterministic generator from the public dataset and kernel inputs;
2. run the existing product-retention transform against this decoder, preserving the same verifier contract.

Do not replace the candidate with an unverified lower-cost circuit. The official DQI verifier's salted failure rate controls the score multiplier.

## 2026-11-19 update — packed BM transition screen

`exp-046` exhaustively screened every GF(2) prefix through length 9. At
length 9, direct degree-4 formulas cover only `21 / 29` forward-state output
bits and `24 / 28` full-inverse outputs. The inverse conditioned on an intact
syndrome symbol covers `27 / 27` bits, but that form retains the input symbol
and does not solve the low-space uncompute problem. Keep the direct low-degree
formulation closed; a composed GF(2^12) transition remains unproven and must
pass the complete `R × Q² × T` budget before circuit work.

