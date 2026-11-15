---
id: exp-036
title: Atakan terminal-folds verified portfolio
task: portfolio
tests: C-037
status: submitted_pending
result: local GM 27.3154195993; Kaggle submission 58383886 pending
---

# Atakan terminal-folds verified portfolio

This experiment packages the best locally verified portfolio found in the
2026-11-15 public-source sweep:

| Task | Member | Evidence | Local result |
|---|---|---|---:|
| invsqrt | `a4d46b17` | full official verifier, 200,540,928 shots | 78,673.5414396 |
| dqi | `821bf8d1` | full official verifier, 102,400 shots | 360,209,905,486.0156 |
| dfthcsos | `6f85dc86` | full official verifier, 78,080 shots | 294,878,475.0543 |

The portfolio's local default geometric mean is `27.3154195993`, above the
previous public score `27.28986`. Kaggle submission `58383886` uses the exact
18-member archive recorded in [receipt.json](receipt.json). The archive and
downloaded notebooks remain outside Git; the receipt records their hashes and
provenance.

The DQI member is reused from the current public-best portfolio. The targeted
weight-16/17 correctness audit remains open, so this result is a verified
submission candidate rather than an exhaustive DQI proof.
