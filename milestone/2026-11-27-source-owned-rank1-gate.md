# Source-owned rank-1 gate — 2026-11-27

## Target

Live rank 1 is 34.65589 (`Cat with 2 Qubits`) in the 2026-11-27 11:20 UTC
leaderboard snapshot.
Proposal S-001 projects to verifier GM 31.79818 using source-built components;
it has not been scored by Kaggle.

## Required DQI improvement

With v155 Invsqrt and V20 chemistry held fixed, an exp-063 DQI at Q=890 must
cost no more than 275,518.87 mean Toffolis to tie the current leader. The
current source-built DQI costs 356,677.49 mean Toffolis, so the required
reduction is 22.75%. This is a derived score-equivalence gate, not a measured
cost for the leader's DQI. Recompute the gate against the live leaderboard before
any submission. To take rank 1, the final score must exceed the live leader.

## Evidence to clear the gate

- A source-owned DQI generator and exact output hash.
- Q at or below 890 and measured mean Toffolis below the refreshed tie gate.
- Correct DQI values and phase, clean scratch, and zero official-verifier errors.
- A reproducible complete archive with all three component receipts and member hashes.
- A Kaggle score above the live rank-1 score.

Keep the next work to one DQI construction with a credible path to the
22.75% reduction. D-005 failed its source-mapping screen before a private
kernel; the exp-057 FMA phase and cleanup routes failed their resource gates.
Do not reopen those branches without a new derivation that clears the cost
target before another private build. See the
[latest leaderboard and gate receipt](../evals/2026-11-27-live-gate-112015Z.json).
