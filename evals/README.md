# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-22T12:26:26Z`)

- Best own public score: `28.14028`, submission `58479383`.
- Latest leader: `Entangled Team`, `33.73732`; score gap `5.59704`.
- Own rank: `1306 / 3560` in the full snapshot; see
  [metadata](2026-11-22-live-leaderboard-122626Z.json) and the
  [retained CSV](../kaggle/snapshots/2026-11-22/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-22T12-26-26.csv).
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result).
- DQI-only target with other task costs fixed: `201.889e9`, or mean
  `T <= 213,956.98` at `Q=890` and `R=1.1912605`. This is score-equivalence
  math, not the leader's measured circuit cost.
- Current source-owned FMA projection: `202,075T`, leaving only `11,881.98T`
  under the score-equivalent gate before omitted work. Exp-057's classical
  one-symbol transition passes, and its reversible one-symbol action measures
  `Q=873`, `T=84` with precomputed matrix entries. Generating those entries,
  full-width cleanup, and the 66-symbol integration remain unmeasured; the
  `84T × 66` estimate may overlap the projection. This is not a candidate. See
  the [classical tail receipt](2026-11-22-exp057-tail-transition-classical.json)
  and [matrix-action receipt](2026-11-22-exp057-tail-matrix-gate.json).
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

The leaderboard CSV is retained under `kaggle/snapshots/`. Its SHA-256 is
recorded in the metadata file. The redundant downloaded ZIP was removed after
the CSV hash, row count, leader, and own-team rank were confirmed. Refresh the
leaderboard before every submission.
