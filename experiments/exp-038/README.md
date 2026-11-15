---
id: exp-038
title: Maoxin 4028-Toffoli chemistry portfolio
task: portfolio
tests: source-notebook official verification log; archive member hash check
status: scored_public
result: local GM 27.3167386412; Kaggle submission 58386039 scored 27.31674
---

# Maoxin 4028-Toffoli chemistry portfolio

This candidate keeps the verified `a4d46b17` inverse-square-root and
`821bf8d1` DQI members from exp-036, and replaces only the chemistry member
with Maoxin123's public 4,028-Toffoli coded-word loaders and factor weights.

The source notebook output log reports full official verifier passes:

| Task | Cost | Qubits | Evidence |
|---|---:|---:|---|
| invsqrt | 78,673.5414396 | 46 | PASS, 200,540,928 shots |
| dqi | 360,209,905,486.0156 | 889 | PASS, 102,400 shots, 0 value/phase errors |
| dfthcsos | 294,835,760.7737 | 427 | PASS, 78,080 shots |

The chemistry cost improves from exp-036's `294,878,475.0543` by
`42,714.2805` (0.014487%), raising the local geometric mean from
`27.3154195993` to `27.3167386412`.

Kaggle submission `58386039` scored `27.31674`. The authenticated leaderboard
endpoint did not expose its live rank, so no rank is claimed.

The exact 18-member archive, SHA-256 values, and source output log are recorded
in [receipt.json](receipt.json). The archive is kept outside Git under
`kaggle/staging/exp-038-maoxin4028/`.
