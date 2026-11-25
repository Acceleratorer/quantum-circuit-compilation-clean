# 2026-11-25 — exp-071 public score calibration

Kaggle CLI readback reports submission `58894750` as `COMPLETE` with public
score `33.05453`. The team's best remains `33.17067`; the recorded rank-1 score
is `34.34445`. exp-071 did not improve the account best.

The original local geometric-mean projection (`33.22214`) was too high. Using
exp-066's public score (`32.85341`) and changing only its chemistry cost from
`255,214,794.20557788` to exp-071's `250,575,905.1396231` gives a calibrated
projection of `33.054909`, only `0.000379` above the actual score. exp-071
reused exp-069's exact DQI hash, so this suggests the local DQI cost reduction
did not add a measurable public-score gain in this result. That attribution is
an inference; salt or scoring variation is not ruled out.

Decision: treat the `33.22214` and exp-069 `33.01962` figures as local-cost
projections, not leaderboard estimates. Keep the verified circuit record and
focus the next optimization on the single exp-057 residue-to-tail key-equation
path.
