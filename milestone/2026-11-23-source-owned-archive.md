# 2026-11-23 — source-owned archive gate

## Gate

Reach rank 1 with a complete competition archive generated from attributed
source, with exact member hashes and official verifier passes for invsqrt,
DQI, and dfthcsos before submission.

## Progress: 3 of 3 members verified

- Invsqrt: exp-062, Q=43; official verifier PASS.
- DQI: exp-063, Q=890; official verifier PASS on 102,400 shots with zero
  value and phase errors.
- dfthcsos: exp-064; official verifier PASS on 78,080 shots, score
  `295,006,518.96994764`, Q=427. The accuracy and gap margins are very small;
  see the [exp-064 report](../experiments/exp-064/README.md).

The 18-member source-owned archive is assembled and its SHA-256 matches the
receipt: `dd4615023eef0478f34738bd7205f3233a14c6cd7ccb800fa55e0b71b20233b6`.
Kaggle accepted it as submission ref `58832495`; CLI readback at
`2026-11-24T15:21:56Z` reports
`COMPLETE` with public score `28.71611`.
The source-owned score is `5.53933` below rank 1.

The latest public snapshot has rank 1 at `34.25544`. Accelra's previous
`33.17067` entry used public circuits and ranked `354 / 3671`; that is not
the source-owned result.
Ref `58832495` scored `28.71611`, still below rank 1 by `5.53933`.
Rank 1 remains the target; the CLI readback returned no private score.

Receipts: [exp-062](../experiments/exp-062/README.md),
[exp-063](../experiments/exp-063/README.md),
[exp-064](../experiments/exp-064/README.md), and
[exp-065](../experiments/exp-065/README.md). Component passes verify circuit
correctness; the completed Kaggle result sets the source-owned baseline
at `28.71611`; rank 1 remains unmet.
