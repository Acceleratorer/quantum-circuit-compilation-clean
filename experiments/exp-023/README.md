---
id: exp-023
title: Refine Syed v12 chemistry weights
task: dfthcsos
tests: [C-026]
direction: D-005
status: submitted_pending
date: 2026-11-13
result: official chemistry verifier PASS; refined weight file lowers the chemistry cost by 0.85 while preserving the Syed v12 invsqrt and DQI bytes
---

# Syed v12 refined chemistry

This is a surgical follow-up to exp-022. The public Orecord pipeline refit only
`dfthcsos/submission.npz`; all 15 angle loaders, `invsqrt.kmb`, and `dqi.kmb`
remain byte-identical to the Syed v12 portfolio.

- Source pipeline: https://www.kaggle.com/code/orecord/quantum-circuit-compilation-pipeline
- Base portfolio: https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook
- Archive: `artifacts/submission_syed_v12_refined.zip` (kept outside Git)
- Archive SHA-256: `3f2d8d70965fa1f9afcb1e9da5bae2f400cf12204d1692b1bb80f26beabc8d85`

The official local verifier passed all three members used in the archive. The
chemistry score moved from `296635967.5935997` to `296635966.74267346`; the
zero-failure geometric-mean estimate moved from `27.078387708141392` to
`27.078387734033633`.

- Submission state: Kaggle ref `58288978`, status `SubmissionStatus.PENDING`, public score ``.
