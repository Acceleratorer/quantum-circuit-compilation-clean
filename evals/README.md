# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Current snapshot

- Candidate: Bori 44Q inverse + Bori chemistry + previously scored Asterios DQI
- Best own public score: `28.14028`, submission `58479383`
- Current leader: `Z³C¹oherence`, `31.61727`; score gap: `3.47699` as checked
  with Kaggle CLI at `2026-11-18 07:03 UTC`
- Own rank: `635 / 3296` in the saved snapshot at
  `2026-11-18T04:56:45Z`; this is not a live rank
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result)
- DQI-only target to match the current leader with other costs fixed: about
  `245.285e9` (derived from the public scores; not the leader's measured cost)
- Full member hashes, verifier evidence, submission, and CSV hash: [2026-11-18-bori-frontier-hybrid.json](2026-11-18-bori-frontier-hybrid.json)
- Current public-candidate screen and decoder budget: [2026-11-20-mid-competition.md](../milestone/2026-11-20-mid-competition.md)

The saved leaderboard CSV is retained under `kaggle/snapshots/2026-11-18/` so
the historical rank can be checked later. Refresh the live leader before every
submission.
