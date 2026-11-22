# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-22T23:05:56Z`)

- Best own public score: `28.14028`, submission `58479383`.
- Latest leader: `Entangled Team`, `33.83493`; score gap `5.69465`.
- Own rank: `1353 / 3596` in the full snapshot; see
  [metadata](2026-11-22-live-leaderboard-230556Z.json) and the
  [retained CSV](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-22T23-05-56.csv).
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result).
- DQI-only target with other task costs fixed: `200.147e9`, or mean
  `T <= 212,110.59` at `Q=890` and `R=1.1912605`. This is score-equivalence
  math, not the leader's measured circuit cost.
- Current source-owned FMA projection: `202,075T`, leaving only `10,035.59T`
  under the score-equivalent gate before omitted work. Exp-057's private v15
  screen now composes compact-prefix decoding, matrix setup, and 66 tail
  actions at `Q=889`, `T=19,004`. It outputs a checksum and does not establish
  the complete FMA projection, DQI output/phase, reversible cleanup, or
  verifier pass; its cost cannot yet be safely added to or subtracted from the
  projection. This is not a candidate. See the
  [v15 receipt](2026-11-23-exp057-prefix-matrix-stream-v15.json).
- Exp-057 v17 also measures one reversible FMA pair update at `Q=108`, `T=210`
  with 48 clean scratch qubits. It takes the pivot inverse as input and is not
  integrated into the 70-symbol solve. Repeating it for 2,415 FMA pair updates
  would cost `507,150T`, already above the whole DQI gate; do not use this cell
  unchanged in the full schedule. See the
  [v17 receipt](2026-11-23-exp057-fma-pair-update-v17.json).
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

Leaderboard CSVs are retained under `kaggle/snapshots/`; their hashes and the
download archive hash are recorded in metadata. The ZIP remains ignored by the
repository rules. Row count, ordering, leader, and own-team rank were checked.
Refresh the leaderboard before every submission.
