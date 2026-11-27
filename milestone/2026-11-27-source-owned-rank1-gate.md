# Source-owned rank-1 gate — 2026-11-27

## Target

Live rank 1 is 34.66186 (`Cat with 2 Qubits`) in the 2026-11-27 15:36 UTC
leaderboard snapshot.
Proposal S-001 projects to verifier GM 31.79818 using source-built components;
it has not been scored by Kaggle. Substituting the measured QV2 DQI component
projects to 32.42186, still 2.24000 below rank 1; this is not a Kaggle score.

## Required DQI improvement

With v155 Invsqrt and V20 chemistry held fixed, an exp-063 DQI at Q=890 must
cost no more than 275,376.53 mean Toffolis to tie the current leader. The
source-built exp-063 DQI costs 356,677.49 mean Toffolis, so the required
reduction is 22.79%. The exact QV2 rebuild measured a score of
317,508,715,032.39 and passed with three value errors; exp-089 records that
reproduction. It projects to 32.42186 in S-001, not a Kaggle score, and is
22.19% above the derived tie-cost gate. The lower exp-069 result
(305,041,647,011.40; zero observed errors) is measurement-only: exp-056 rejects
its dataset because its generators reconstruct released KMX stages. Do not
use its code or circuit as an optimization or submission base. QV2's Apache
source may be developed in a private Kaggle kernel with full attribution, but
the unchanged upstream design is not ours. Recompute the gate against the live
leaderboard before any submission. To take rank 1, the final score must exceed
the live leader.

## Evidence to clear the gate

- A source-owned DQI generator and exact output hash.
- Q at or below 890 and measured mean Toffolis below the refreshed tie gate.
- Official verifier PASS at the required salts; report every value/phase error
  and repetition factor in the measured score.
- A reproducible complete archive with all three component receipts and member hashes.
- A Kaggle score above the live rank-1 score.

Keep the next work to one QV2 source-level change implemented and measured as
our own modification. It must have a credible path to at least an 18.16% score
reduction (about 60,521 mean T at Q=889 if the measured repetition factor
holds) before another private build. D-005 failed its source-mapping screen;
the exp-057 FMA phase and cleanup routes failed their resource gates. Do not
reopen those branches without a new derivation that clears the cost target. See the
[latest leaderboard and gate receipt](../evals/2026-11-27-live-gate-153613Z.json)
and [QV2 verifier receipt](../evals/2026-11-27-exp089-qv2-dqi-source.json).
The exp-069 restriction is recorded in the
[exp-056 provenance screen](../experiments/exp-056/README.md).
