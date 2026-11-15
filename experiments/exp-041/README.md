---
id: exp-041
title: Atakan compatible 4028 chemistry refit
task: portfolio
tests: hosted official verifiers; independent archive hash and GM check
status: submitted_pending
result: local GM 28.0581094382; chemistry 294827530.2995; Kaggle refs 58389412 and 58389450 pending
---

# Atakan compatible 4028 chemistry refit

This candidate keeps the current best 44-qubit inverse and 890-qubit DQI
members and replaces only the chemistry factor/loaders with Atakan's
compatible 4028-Toffoli refit. The public notebook reports unmodified official
verifier PASS at the default shots and a second chemistry salt. Its downloaded
`reproduction_audit.json` reports the exact task results and credits Syed Asad
Ali as the original inverse/DQI builder.

| Task | Cost | Qubits | Evidence |
|---|---:|---:|---|
| invsqrt | 75,170.6202573 | 44 | PASS, 200,540,928 shots |
| dqi | 347,904,227,555.5428 | 890 | PASS, 102,400 shots, 0 errors |
| dfthcsos | 294,827,530.2995 | 427 | PASS, 78,080 shots |

The exact 18-member archive passed CRC and member SHA-256 checks locally. Its
independent geometric mean is `28.0581094382`, a small improvement over
exp-039's `28.0564936608`. The archive remains outside Git under
`kaggle/staging/targeted-2026-11-15/atakan-terminal/`.

