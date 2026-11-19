# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## Latest live status (`2026-11-19T10:49:12Z`)

- Candidate: Bori 44Q inverse + Bori chemistry + previously scored Asterios DQI
- Best own public score: `28.14028`, submission `58479383`
- Latest leader: `Z³C¹oherence`, `31.74002`; Kaggle CLI check at
  `2026-11-19T10:49:12Z`
- Own rank: `896 / 3381` in the full snapshot; see
  [its metadata](2026-11-19-live-leaderboard-104912Z.json) and CSV
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result)
- DQI-only target to match the latest leader with other costs fixed: about
  `242.451e9` (score-equivalence estimate, not the leader's measured cost)
- Full member hashes, verifier evidence, and submission: [2026-11-18-bori-frontier-hybrid.json](2026-11-18-bori-frontier-hybrid.json)
- External portfolio screen: its published receipt reports all three tasks
  PASS and local score `28.23163`; not submitted because it has no generator
  of our own. See [the receipt and decision](2026-11-18-ozertuu-282316.json)
- Current public-candidate screen and decoder budget: [2026-11-20-mid-competition.md](../milestone/2026-11-20-mid-competition.md)

The saved leaderboard CSVs are retained under `kaggle/snapshots/` so historical
ranks can be checked later. Refresh the live leader before every submission.
