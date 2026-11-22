# exp-057 FMA pair update component

## Score target

The current rank-1-equivalent DQI target is `T <= 213,956.98` at `Q=890` and
`R=1.1912605`. The 70-symbol circuit must fit this complete resource bound;
the new component count is not a circuit estimate.

## Gate achieved

Private Kaggle kernel v17 passed the one-pair sequential-FMA update for both
pivot branches: 32 cases per branch, `Q=108`, `T=210`, 48 clean scratch
qubits, preserved pivot inputs, and zero phase flips. This is below the
50-qubit component scratch ceiling.

Evidence: [v17 evaluation receipt](../evals/2026-11-23-exp057-fma-pair-update-v17.json),
[run log](../log/2026-11-23-exp057-fma-pair-update-v17.md), and
[private kernel v17](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/17).

## Resource decision

The cell receives the pivot inverse as input and updates one pair at a fixed
`delta`. The 70-symbol FMA recurrence has 2,415 pair updates, so repeating this
cell would cost `507,150T` before setup or cleanup, above the full DQI target
of `213,956.98T`. Do not use this implementation unchanged in the schedule.

The competition gate remains open: a candidate still needs the complete
key-equation solve, `Q <= 890`, the full `R × Q² × T` ledger, DQI output/phase,
clean reversible workspace, and a passing official verifier.
