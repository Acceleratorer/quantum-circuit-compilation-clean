---
id: exp-074
title: Source-built V20 chemistry with base DQI
task: portfolio
status: scored_public
date: 2026-11-26
result: All official verifiers pass; Kaggle ref 58917074 scored 33.08634
---

# exp-074 — V20 chemistry with source-built DQI baseline

This experiment ports only Goodpjw2008's source-built V20 chemistry loader. It
keeps exp-073's verified source-built DQI and Invsqrt circuits. No compiled
candidate circuit from V20 is used.

## Candidate gate

The notebook reports 3,118 Toffolis per chemistry pass. This source port
measured 3,325, so the reported count was not reproduced. It is three below
exp-073's 3,328. With the other measured component costs held fixed, the local
verifier GM is 33.08637, up 0.00503 from exp-073's 33.08134. Kaggle scored the
archive at 33.08634, improving the previous source-owned public score of
33.08169 by 0.00465. The notebook's 3,118 count was not reproduced, and rank 1
remains 1.25811 points higher.

## Verification and submission

Kaggle kernel version 3 completed all official verifiers:

- Chemistry: PASS at default and salt 42, 78,016 shots each; score
  `249,853,852.96142676`; 3,325 Toffolis/pass.
- Invsqrt: PASS, 200,540,928 shots; score `61,696.23146663024`.
- DQI: PASS, 102,400 shots; zero value and phase errors; score
  `305,041,647,011.3978`.
- Local verifier GM: `33.0863673873`; this is not a public-score projection.
- Archive: 18 members, SHA-256
  `a77203a68528a8f01a4e2275aff35a38e188be5a065a807021e9e12d8ac9e521`.

The archive was submitted as Kaggle ref `58917074` and completed at public score
`33.08634`. The post-submission snapshot has rank 1 at `34.34445` and Accelra at
`746 / 3740`; Accelra's higher `33.17067` entry used a public circuit archive.
The source-owned score-equivalent rank is `1176`. See the
[evaluation receipt](../../evals/2026-11-26-exp074-source-built-v20-chemistry.json)
and [run log](../../log/2026-11-26-exp074-v20-chemistry.md). Raw verifier logs
are kept under the ignored `out/kaggle-v3/` directory.

## Reproduction

    python experiments/exp-074/package_kernel.py <empty-staging-directory>
    kaggle kernels push -p <staging-directory>

The private kernel is
`accelra/exp-074-source-built-v20-chemistry-with-base-dqi`. Its package script
bundles the separated module and pinned source payloads.

## Attribution

- Goodpjw2008, [QCC | Shorter Chemistry Loaders | LB 33.25564](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25564), Apache-2.0. This experiment adapts its source-built chemistry loader only; the notebook SHA-256 is recorded in `source.json`.
- Tony Li, [Quantum AI 32.85306 task generators](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators), Apache-2.0. The source generator builds the base loaders, DQI, and Invsqrt circuits.
- Maoxin123, [3,357-Toffoli chemistry loaders](https://www.kaggle.com/code/maoxin123/qcc-33-17-3-357-toffoli-chemistry-loaders), source of the raw chemistry parameter table. Only `submission.npz` is read.

See `NOTICE.md` for code and data boundaries.
