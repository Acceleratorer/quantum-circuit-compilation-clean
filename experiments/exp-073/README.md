---
id: exp-073
title: Source-built V19 chemistry with unmodified base DQI
task: portfolio
status: verified_local_not_submitted
date: 2026-11-26
result: All verifiers PASS; local GM 33.0813367703; no public submission
---

# exp-073 — V19 chemistry with base DQI

This is one controlled follow-up to exp-072. It keeps the source-built V19
chemistry and Invsqrt inputs, but copies the source-built DQI base circuit
without applying the ten gate rewrites that produced four value errors in
exp-066 and exp-072.

The build pins the base DQI hash to exp-071's verified source output
(4b572141…) and the Invsqrt hash to 68eb8c13…. The chemistry builder and
its compressed source payloads are reused from exp-072 by the packager, so this
experiment does not duplicate those files in Git.

## Gate

Kaggle kernel version 2 completed all official verifiers:

- Chemistry: PASS at default and salt 42, 78,016 shots each; 3,328
  Toffolis/pass.
- Invsqrt: PASS, 200,540,928 shots.
- DQI: PASS, 102,400 shots, zero value and phase errors; base hash
  `4b572141…`.
- Local verifier GM: `33.0813367703`; this is not a public-score projection.
- Archive: 18 members, SHA-256
  `4a8c4338027eee4fdc984c7417ed49b24059c232706a3fa6df044e552cacfc87`.

No public submission was made. The local result does not establish an
improvement over exp-072's public `33.08169`; keep exp-073 as the verified
zero-error DQI baseline. Full receipts are in
[`evals/2026-11-26-exp073-v19-base-dqi.json`](../../evals/2026-11-26-exp073-v19-base-dqi.json)
and [`log/2026-11-26-exp073-base-dqi.md`](../../log/2026-11-26-exp073-base-dqi.md).

## Reproduction

    python experiments/exp-073/package_kernel.py <empty-staging-directory>
    kaggle kernels push -p <staging-directory>

The private kernel is accelra/exp-073-source-built-v19-chemistry-with-base-dqi.
