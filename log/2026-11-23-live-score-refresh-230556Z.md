# 2026-11-23 — live Kaggle leaderboard refresh

The Kaggle CLI full public leaderboard download completed at
`2026-11-22T23:05:56Z`. It contains 3,596 unique teams in descending score
order. `Accelra` remains at `28.14028`, now rank `1,353`; Entangled Team leads
at `33.83493`, a `5.69465`-point gap.

Holding the other two submitted task costs fixed, score equivalence now gives
a DQI target of `200.147e9`. At `Q=890` and `R=1.1912605`, that is a mean
`T <= 212,110.59`. The existing `202,075T` FMA count is still only a
projection, leaving `10,035.59T` before omitted work. This is not a measured
leader cost or a candidate.

## Verification

- Command: `kaggle competitions leaderboard google-verifiable-quantum-circuit-compilation --download --path kaggle/snapshots/2026-11-23`.
- CSV SHA-256: `bdce33b7f3e63631aa7b396dc32c684347172c98e5f06dd9b4b4e4e6260a8736`.
- Source ZIP SHA-256: `10499bf51961ce38516d962d37716fcf2568fc1d1bb227e3973614e9f9475b99`.
- Row count, unique team IDs, score ordering, leader, and own rank were checked.
- [Snapshot receipt](../evals/2026-11-22-live-leaderboard-230556Z.json) and
  [retained CSV](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-22T23-05-56.csv).

This was a read-only refresh. No circuit was built or submitted.
