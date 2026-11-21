# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-21T12:55:34Z`)

- Best own public score: `28.14028`, submission `58479383`.
- Latest leader: `Z³C¹oherence`, `33.34845`; score gap `5.20817`.
- Own rank: `1202 / 3519` in the full snapshot; see
  [metadata](2026-11-21-live-leaderboard-125534Z.json) and the retained CSV.
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result).
- DQI-only target with other task costs fixed: `209.035e9`, or mean
  `T <= 221,529` at `Q=890` and `R=1.1912605`. This is score-equivalence
  math, not the leader's measured circuit cost.
- Current source-owned FMA projection: `202,075T`, leaving `19,454T` for
  omitted work. Width, phase, and cleanup are unproven; this is not a candidate.
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

The leaderboard CSV is retained under `kaggle/snapshots/`. Its SHA-256 is
recorded in the metadata file. The redundant downloaded ZIP was removed after
the CSV hash, row count, leader, and own-team rank were confirmed. Refresh the
leaderboard before every submission.
