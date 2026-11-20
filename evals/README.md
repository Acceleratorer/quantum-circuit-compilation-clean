# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-20T17:14:49Z`)

- Candidate: Bori 44Q inverse + Bori chemistry + previously scored Asterios DQI
- Best own public score: `28.14028`, submission `58479383`
- Latest leader: `Rithvik Redrouthu`, `32.56892`; Kaggle API snapshot at
  `2026-11-20T17:14:49Z`
- Own rank: `1079 / 3464` in the full snapshot; see
  [its metadata](2026-11-20-live-leaderboard-171449Z.json) and CSV
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result)
- DQI-only target to match the latest leader with other costs fixed: about
  `224.406e9`, or mean `T <= 237,820` at `Q=890`
  (score-equivalence estimate, not the leader's measured cost)
- Full member hashes, verifier evidence, and submission: [2026-11-18-bori-frontier-hybrid.json](2026-11-18-bori-frontier-hybrid.json)
- External portfolio screen: its published receipt reports all three tasks
  PASS and local score `28.23163`; not submitted because it has no generator
  of our own. See [the receipt and decision](2026-11-18-ozertuu-282316.json)
- Current public-candidate screen and decoder budget: [2026-11-20-mid-competition.md](../milestone/2026-11-20-mid-competition.md)

The saved leaderboard CSVs are retained under `kaggle/snapshots/` so historical
ranks can be checked later. Refresh the live leader before every submission.
