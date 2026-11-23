# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-23T04:27:24Z`)

- Best own public score: `28.14028`, submission `58479383`.
- Latest leader: `Entangled Team`, `33.85279`; score gap `5.71251`.
- Own rank: `1372 / 3606 ranked teams` in the full snapshot; see
  [metadata](2026-11-23-live-leaderboard-042724Z.json) and the
  [retained CSV](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-23T04-27-24.csv).
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result).
- DQI-only target with other task costs fixed: `199.830e9`, or mean
  `T <= 211,775.05` at `Q=890` and `R=1.1912605`. This is score-equivalence
  math, not the leader's measured circuit cost.
- The previous source-owned FMA projection of `202,075T` is unsupported after
  the v19 bridge diagnostic. `CONVERT + scan + reverse CONVERT` measured
  `Q=879`, `T=183,837`; the canonical DQI residue-pair control passed phase,
  while the padded FMA low-rank row did not. Adding the v18 repeated pair-update
  subtotal gives `314,247T`, above the `211,775.05T` score-equivalent gate
  before omitted work. See the [v19 receipt](2026-11-23-exp057-fma-convert-scan-v19.json)
  and [reproduction screen](../experiments/exp-057/convert_bridge_screen.py).
- Exp-057's private v15 screen composes compact-prefix decoding, matrix setup,
  and 66 tail actions at `Q=889`, `T=19,004`. It outputs a checksum and does
  not establish full DQI output/phase, cleanup, or verifier pass; this is not a
  candidate. See the [v15 receipt](2026-11-23-exp057-prefix-matrix-stream-v15.json).
- Exp-057 v18 measures one normalized MBU FMA pair update at `Q=50`, `T=54`
  with 13 clean scratch qubits. Repeating it for the 2,415 pair updates gives
  `130,410T`, matching the existing `42T` product plus `12T` controlled-swap
  ledger. This component result does not create new budget; the v19 diagnostic
  shows the measured converter path cannot fit with it. Full integration,
  width, DQI output/phase, cleanup, and verifier remain open. See the
  [v18 receipt](2026-11-23-exp057-fma-pair-update-mbu-v18.json).
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

Leaderboard CSVs are retained under `kaggle/snapshots/`; their hashes and the
download archive hash are recorded in metadata. The ZIP remains ignored by the
repository rules. Row count, ordering, leader, and own-team rank were checked.
Refresh the leaderboard before every submission.
