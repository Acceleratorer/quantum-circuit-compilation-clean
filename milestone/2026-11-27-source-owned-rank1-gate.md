# Source-owned rank-1 gate — 2026-11-27

## Target

Live rank 1 is 34.50408 (`Cat with 2 Qubits`) on the latest Kaggle CLI read.
Proposal S-001 projects to verifier GM 31.79818 using source-built components;
it has not been scored by Kaggle.

## Required DQI improvement

With v155 Invsqrt and V20 chemistry held fixed, an exp-063 DQI at Q=890 must
cost no more than 279,171.55 mean Toffolis to tie the current leader. The
current source-built DQI costs 356,677.49 mean Toffolis, so the required
reduction is 21.73%. Recompute the gate against the live leaderboard before
any submission. To take rank 1, the final score must exceed the live leader.

## Evidence to clear the gate

- A source-owned DQI generator and exact output hash.
- Q at or below 890 and measured mean Toffolis below the refreshed tie gate.
- Correct DQI values and phase, clean scratch, and zero official-verifier errors.
- A reproducible complete archive with all three component receipts and member hashes.
- A Kaggle score above the live rank-1 score.

The active search is focused on DQI, which has the clearest source-owned route
to the required 21.73% reduction. The exp-057 FMA phase and cleanup routes
already failed their resource gates; do not revive them without a new
derivation that clears the cost target before another private build.
