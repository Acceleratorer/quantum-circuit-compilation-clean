---
id: D-004
title: Promote the public 392k DQI decoder, then recover its generator
status: active
tasks: dqi, all
last_checked: 2026-11-12
---

# D-004: public 392k DQI decoder

The 392k decoder is the largest verified local gain found in the current cache. Submit it once quota allows, then spend research time on one of two paths:

1. recover or reconstruct a deterministic generator from the public dataset and kernel inputs;
2. run the existing product-retention transform against this decoder, preserving the same verifier contract.

Do not replace the candidate with an unverified lower-cost circuit. The official DQI verifier's salted failure rate controls the score multiplier.

