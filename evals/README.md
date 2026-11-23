# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-23T00:16:46Z`)

- Best own public score: `28.14028`, submission `58479383`.
- Latest leader: `Entangled Team`, `33.83493`; score gap `5.69465`.
- Own rank: `1356 / 3598` in the full snapshot; see
  [metadata](2026-11-23-live-leaderboard-001646Z.json) and the
  [retained CSV](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-23T00-16-46Z.csv).
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
- Exp-057 v18 measures one normalized MBU FMA pair update at `Q=50`, `T=54`
  with 13 clean scratch qubits. Repeating it for the 2,415 pair updates gives
  `130,410T`, matching the existing `42T` product plus `12T` controlled-swap
  ledger. The existing `202,075T` full projection leaves only `10,035.59T`
  under the `212,110.59T` gate; integration, width, DQI output/phase, cleanup,
  and verifier remain open. This component result does not create new budget.
  See the [v18 receipt](2026-11-23-exp057-fma-pair-update-mbu-v18.json).
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

Leaderboard CSVs are retained under `kaggle/snapshots/`; their hashes and the
download archive hash are recorded in metadata. The ZIP remains ignored by the
repository rules. Row count, ordering, leader, and own-team rank were checked.
Refresh the leaderboard before every submission.
