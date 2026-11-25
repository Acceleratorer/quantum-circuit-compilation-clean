---
id: exp-069
title: DQI no-edit source baseline
task: dqi
status: verified_zero_observed_errors
date: 2026-11-25
result: DQI cost 305.042B, zero observed errors, projected portfolio 33.01962
---

# exp-069 — DQI no-edit baseline

Rebuild the pinned Apache-2.0 DQI generator and run the official verifier with
no gate rewrites. This checks whether the remaining value error in exp-068
comes from either of its two retained phase edits or from the base source
circuit. No compiled circuit is used as input, and no competition submission
is created.

## Result

The source rebuild matched the pinned base DQI hash. The official verifier
passed 102,400 shots with zero value errors and zero phase errors; DQI cost was
305041647011.3978. This is lower than both exp-066 and exp-068.

Holding exp-066's invsqrt and chemistry members fixed projects a total score of
33.01962, an estimated gain of 0.16621 over 32.85341. The projection remains
below the account's 33.17067 best, so this DQI circuit is recorded as a
source-owned candidate without submitting another lower-scoring portfolio.

See evals/2026-11-25-exp069-dqi-no-edit-baseline.json and receipts/.
