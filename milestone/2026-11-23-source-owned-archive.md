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
The exp-065 source-owned score was `5.53933` below rank 1.

## Latest progress (`2026-11-26`)

- exp-071's source-built hybrid completed as Kaggle ref `58894750` with public
  score `33.05453`.
- exp-072 rebuilt the V19 chemistry proposal without reading compiled input
  circuits. All task verifiers passed, but the source build produced 3,328
  Toffolis/pass versus the notebook's claimed 3,310. It was held from
  submission; its local verifier GM was `32.91482` on a DQI draw with four
  value errors. See the [exp-072 evaluation](../evals/2026-11-26-exp072-source-built-v19-chemistry.json).
- The latest full snapshot ranks Accelra `692 / 3722` at `33.17067` (public
  circuit archive). Rank 1 is `34.34445`; the gap from the account best is
  `1.17378`.

Rank 1 remains unmet. The gate requires a source-owned submission that scores
above the leader, not only component verifier passes.

Receipts: [exp-062](../experiments/exp-062/README.md),
[exp-063](../experiments/exp-063/README.md),
[exp-064](../experiments/exp-064/README.md), and
[exp-065](../experiments/exp-065/README.md). Component passes verify circuit
correctness; the completed Kaggle result sets the source-owned baseline
at `28.71611`; rank 1 remains unmet.
