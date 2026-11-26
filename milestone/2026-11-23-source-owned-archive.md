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
  circuits. All task verifiers passed; the source build produced 3,328
  Toffolis/pass versus the notebook's claimed 3,310. Kaggle submission
  `58907057` completed at `33.08169`, improving exp-071's source-owned score
  by `0.02716`. The local verifier measured four value errors on the rewritten
  DQI hash; see the [exp-072 evaluation](../evals/2026-11-26-exp072-source-built-v19-chemistry.json).
- The latest full snapshot ranks Accelra `719 / 3733` at `33.17067` from a
  public circuit archive. The source-owned score `33.08169` is score-equivalent
  to rank `1164`. Rank 1 is `34.34445`; its gap from the source-owned best is
  `1.26276`.
- exp-073 rebuilt the V19 chemistry with the verified, unmodified DQI base.
  All three official verifiers passed with zero DQI value/phase errors. Its
  local GM is `33.0813367703`, which does not establish a public-score gain
  over exp-072's `33.08169`; no submission was made. See the
  [exp-073 evaluation](../evals/2026-11-26-exp073-v19-base-dqi.json).
- exp-074 rebuilt the V20 chemistry from source and passed all official
  verifiers with the same base DQI. It measured 3,325 Toffolis/pass, only three
  below exp-073 and 207 above the notebook's 3,118 claim. Local GM is
  `33.0863673873`; Kaggle ref `58917074` completed at `33.08634`, improving
  the source-owned best by `0.00465`. See the
  [exp-074 evaluation](../evals/2026-11-26-exp074-source-built-v20-chemistry.json).
- exp-082 rebuilt V22 chemistry from source, passed all official verifiers,
  and completed as Kaggle ref `58958257` at `33.08801`, improving the
  source-owned best by `0.00167`. Its local GM is `33.08804494`; the
  `33.17067` public-archive result remains ineligible. See the
  [exp-082 evaluation](../evals/2026-11-26-exp082-source-built-v22-chemistry.json).
- A fresh Kaggle CLI top-ten read at `2026-11-26T06:23:47Z` shows leader `Cat
  with 2 Qubits` at `34.50408`, leaving a `1.41774` gap to the source-owned
  best. The DQI score-equivalent tie gate is `285,041.64` mean T at `Q=890`.
- A static read of Goodpjw2008's latest public chemistry source found a
  `3,306 T/pass` loader recipe versus exp-074's `3,325`; its chemistry score
  implies only about `+0.032` local GM if exp-074's other members stay fixed.
  That notebook also pins public DQI and Invsqrt binaries, so its `33.25733`
  full score is not an eligible portfolio. Keep the recipe as a reference;
  skip a port for now. Source slug:
  [`qcc-shorter-chemistry-loaders-lb-33-25733`](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25733),
  notebook SHA-256 `12e4877137f12203f83efedee3d31cd8fe81c135aa3b4ffaa1ee994553eeccb8`.
  Kaggle metadata says `33.25733`; its embedded notebook heading says
  `33.25737`. This was a static screen; we did not run that notebook.
- exp-053's four-to-five-pivot handoff failed the hard width gate at `Q=891`.
  Its no-ancilla parity-controlled follow-up kept `Q=891` and added 76 T, so
  close this 4+1 continuation. See the [v35 receipt](../evals/2026-11-26-exp053-four-plus-one-handoff-v35.json)
  and [v36 receipt](../evals/2026-11-26-exp053-parity-handoff-v36.json).

The `2026-11-26T00:50:28Z` leaderboard snapshot has 3,740 rows: Accelra is
`746 / 3740` at `33.17067`; rank 1 remains `34.34445`. The source-owned best is
`33.08634`, still `1.25811` below rank 1. The refreshed snapshot and hash are
recorded in the [exp-074 evaluation](../evals/2026-11-26-exp074-source-built-v20-chemistry.json).

Rank 1 remains unmet. The gate requires a source-owned submission that scores
above the leader, not only component verifier passes.

The latest CLI read (`2026-11-26T17:42:19Z`) still shows `Cat with 2 Qubits`
at `34.50408`; exp-082 is `1.41607` below it. The refreshed DQI tie gate is
`278,784.97` mean T at `Q=900`, derived from exp-082's non-DQI component costs.

Receipts: [exp-062](../experiments/exp-062/README.md),
[exp-063](../experiments/exp-063/README.md),
[exp-064](../experiments/exp-064/README.md), and
[exp-065](../experiments/exp-065/README.md). Component passes verify circuit
correctness; the completed Kaggle result sets the source-owned baseline
at `28.71611`; rank 1 remains unmet.
