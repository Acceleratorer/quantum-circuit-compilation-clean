# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Current snapshot

- Candidate: Bori 44Q inverse + Bori chemistry + previously scored Asterios DQI
- Best own public score: `28.14028`, submission `58479383`
- Current leader: `Z³C¹oherence`, `31.61727`; refreshed with Kaggle CLI at
  `2026-11-18T18:55:00Z`
- Own rank: `781 / 3338` in the saved snapshot at `2026-11-18T18:55:00Z`; see
  [the snapshot metadata](2026-11-18-live-leaderboard-185500.json) and its CSV
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result)
- DQI-only target to match the current leader with other costs fixed: about
  `245.285e9` (derived from the public scores; not the leader's measured cost)
- Full member hashes, verifier evidence, and submission: [2026-11-18-bori-frontier-hybrid.json](2026-11-18-bori-frontier-hybrid.json)
- External portfolio screen: its published receipt reports all three tasks
  PASS and local score `28.23163`; not submitted because it has no generator
  of our own. See [the receipt and decision](2026-11-18-ozertuu-282316.json)
- Current public-candidate screen and decoder budget: [2026-11-20-mid-competition.md](../milestone/2026-11-20-mid-competition.md)

The saved leaderboard CSV is retained under `kaggle/snapshots/2026-11-18/` so
the historical rank can be checked later. Refresh the live leader before every
submission.
