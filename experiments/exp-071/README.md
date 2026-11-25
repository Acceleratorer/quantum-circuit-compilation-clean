---
id: exp-071
title: Source-built chemistry loader hybrid
task: portfolio
status: scored_public
date: 2026-11-25
result: Kaggle public score 33.05453; chemistry PASS at 250575905.14
---

# exp-071 — source-built chemistry loader hybrid

This portfolio replaces the two expensive source-plan loaders in exp-070 with
ThemBones source KMX loaders. Their first ten angle-word columns match the
V18 factorization exactly. Both KMX files were compiled locally; no compiled
loader input was used. The remaining V18 loaders and factorization were also
rebuilt from source.

## Verification

- Chemistry: official verifier PASS at default salt and `--salt 42`; 78,016
  shots; score `250,575,905.1396231`; 3,344 Toffolis/pass; 128-qubit loader
  cap met.
- DQI: source build matched `4b572141…`; official exp-069 verifier PASS at
  102,400 shots with zero observed value or phase errors.
- Invsqrt: source build matched `68eb8c13…`; official exp-066 verifier PASS
  at 200,540,928 shots.
- Archive: 18 members, CRC and member hashes checked; SHA-256
  `378066e803c3383057159f13dac13ba86933dfbdd82dea7db37ddb49041aebd6`.

Kaggle submission `58894750` completed with public score `33.05453`. This is
`0.11614` below the team's best `33.17067` and `1.28992` below the latest
recorded rank-1 score `34.34445`. The earlier local projection `33.22214` was
not a valid public-score estimate; see the [score calibration](../../log/2026-11-25-exp071-score-calibration.md)
and [evaluation record](../../evals/2026-11-25-exp071-source-hybrid.json).

## Attribution

- Chemistry loaders 2–14 and the factorization: Goodpjw2008's Apache-2.0
  [V18 chemistry notebook](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-24213).
- Chemistry loaders 0–1: Danish Ali / team ThemBones' Apache-2.0 source
  distribution, documented in exp-066's `chemistry/README.md` and release
  notices.
- DQI: Tony Li's Apache-2.0 generator dataset, as pinned in exp-069.
- Invsqrt: rebuilt using the credited source chain in
  [exp-066](../exp-066/README.md).

The exact notebook and factorization hashes, verifier values, archive
integrity, leaderboard snapshot, and Kaggle status are in the evaluation JSON.
