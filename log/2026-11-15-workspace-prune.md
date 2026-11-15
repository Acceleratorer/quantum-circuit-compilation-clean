---
date: 2026-11-15
title: Prune downloaded Kaggle caches outside the evidence repository
type: cleanup
---

Measured the workspace before deletion and recorded every target in
`cleanup/2026-11-15-root-prune-manifest.json`. The canonical Git repository
`tmp/github_publish/`, its exp-036 submission archive, and `.venv/` were
protected. The remaining downloaded datasets, extracted notebooks, duplicate
archives, scratch clones, and temporary outputs are safe to redownload from
Kaggle or reproduce from the receipts.
