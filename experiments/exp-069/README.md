---
id: exp-069
title: DQI no-edit source baseline
task: dqi
status: verified_zero_observed_errors
date: 2026-11-25
result: DQI cost 305.042B, zero observed errors; public score benefit unconfirmed
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

The original local-cost projection of `33.01962` was not validated as a public
score estimate. exp-071 reused this exact DQI source hash and scored `33.05453`
after replacing only the chemistry member. Scaling exp-066's public score by
the chemistry cost change alone predicts `33.05491`, within `0.00038` of the
actual result. This is evidence that the exp-069 local DQI saving did not add a
measurable public-score gain in that submission; salt or scoring variation is
a plausible explanation, not a proven cause. Keep the verifier result, but do
not use `33.01962` as a leaderboard projection. See the
[calibration note](../../log/2026-11-25-exp071-score-calibration.md).

See evals/2026-11-25-exp069-dqi-no-edit-baseline.json and receipts/.
