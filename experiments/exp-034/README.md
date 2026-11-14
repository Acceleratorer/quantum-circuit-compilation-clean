---
id: exp-034
title: Static check of two current frontier notebooks
task: portfolio
tests: []
status: no_improvement
date: 2026-11-15
result: No source-complete candidate beating 27.28986 was established; Atakan's 27.30683 and 27.29711 estimates are conditional, not public scores.
---

# Frontier notebook check

Two recent public notebooks were inspected as text. Neither notebook had an
executed code cell in its downloaded version, and neither establishes a new
observed portfolio score.

- Atakan's notebook contains an earlier conditional estimate of `27.3068304`
  and a later V52 continuation estimate of `27.2971061`. Neither is an
  observed public score; the later record says `fresh_all_tasks_pass=False`.
  It reuses DQI evidence, so it does not close the DQI source and correctness
  gap.
- Asterios's notebook explores a related chemistry refit using 4,033-Toffoli
  loaders. The inspected copy contains no executed code cells or measured
  public result.

Neither is a submission candidate. The next high-value work is a DQI generator
that we can reproduce from committed source and measure against the current
frontier.

Source hashes and Kaggle references are in [SOURCES.md](SOURCES.md). Raw
notebook copies are kept locally under `external/` and excluded from Git.
