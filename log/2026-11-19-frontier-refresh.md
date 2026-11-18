---
id: 2026-11-19-frontier-refresh
date: 2026-11-19
---

# Frontier refresh and external portfolio screen

The Kaggle CLI snapshot at `2026-11-18T18:55:00Z` places `Accelra` at
`781 / 3338` with `28.14028`; `Z³C¹oherence` leads at `31.61727`. The archived
CSV and hash are in `evals/2026-11-18-live-leaderboard-185500.json`.

The public Ozertuu portfolio's published verifier receipt reports all three
tasks PASS and a local score of `28.23163018`, which would rank around 72
against that snapshot. Its 18 archive member hashes match the published
receipt. It was not submitted because the standing user decision requires our
own generator for submitted circuits.
Verifier and archive receipts are in `evals/2026-11-18-ozertuu-282316.json`.

The top-1 score gap remains `3.47699`. Keep work on the active DQI direction
D-004; the next useful gate is the reversible BM transition from exp-045, not
another external portfolio or a marginal component swap.
