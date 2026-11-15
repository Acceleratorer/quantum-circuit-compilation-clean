---
id: exp-039
title: Ozertuu private verified portfolio 28.05649
task: portfolio
tests: source notebook verifier evidence; exact archive member hash check
status: scored_public
result: local GM 28.0564936608; Kaggle submission 58387243 scored 28.05649
---

# Ozertuu private verified portfolio 28.05649

Ozertuu's public notebook `vqcc-verified-portfolio-28-056` emits an
18-member `submission.zip` from the dataset
`ozertuu/vqcc-verified-private-portfolio-28056`. The notebook reports the
unchanged official verifier results below and authenticates every member by
SHA-256 before writing the archive.

| Task | Cost | Qubits | Verification |
|---|---:|---:|---|
| invsqrt | 75,170.6202573 | 44 | PASS, 200,540,928 shots |
| dqi | 347,904,227,555.5428 | 890 | PASS, 102,400 shots, 0 value/phase errors |
| dfthcsos | 294,878,470.7110 | 427 | PASS, 78,080 shots |

The reported zero-error local geometric mean is `28.0564936608`, compared with
exp-038's public `27.31674`. The exact archive SHA-256 and all 18 member hashes
are in the external receipt under `kaggle/staging/exp-039-ozertuu-28056/`.

Kaggle accepted the archive as submission `58387243` and scored it `28.05649`.
The rank will be recorded only if the authenticated leaderboard makes it
available.

The source credits Syed Asad Ali as the original builder of the 44-qubit
inverse and 890-qubit DQI circuits, and records the chemistry lineage and
licences in its `SOURCE_CREDITS.md`. Finite DQI sampling is still not an
exhaustive proof.
