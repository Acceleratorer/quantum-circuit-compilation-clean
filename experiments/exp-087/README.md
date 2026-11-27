---
id: exp-087
title: Measure the source-built pro-q2-897 DQI decoder
task: dqi
status: completed-below-score-gate
date: 2026-11-27
---

# exp-087 — pro-q2-897 DQI score gate

This experiment rebuilds the pinned `pro_q2_897` generator from source and
runs the official DQI verifier in a private Kaggle kernel. It does not submit
to the competition. The build uses the repository launcher
[`src/dqi/generate.py`](../../src/dqi/generate.py), not the upstream
`build_897.py` entry point.

The port is Apache-2.0-licensed SomeJoint code, not our design. Its documented
design lineage passes through an unlicensed repository; see
[`src/dqi/NOTICE`](../../src/dqi/NOTICE). The kernel runs offline, checks the
source manifest, and rejects any generated circuit whose hash differs from
the upstream build hash.

## Gate

The 2026-11-27 11:20 UTC leaderboard snapshot puts rank 1 at `34.65589`. With
S-001's Invsqrt and chemistry costs fixed and the baseline repetition factor
held at `1.1912604648`, a DQI at `Q=897` must measure at or below `271,235.47`
mean Toffolis to tie. The private verifier run also computes the exact cost
gate using the candidate's measured repetition factor.

## Measured result

Kaggle kernel version 1 completed successfully in 467 seconds:
[`accelra/exp-087-pro-q2-dqi-source-gate`](https://www.kaggle.com/code/accelra/exp-087-pro-q2-dqi-source-gate).
The source build checked all 68 pinned files and reproduced the upstream circuit
hash. The official verifier passed 102,400 shots with zero value or phase errors.

It measured `440,632.997988` mean Toffolis at `Q=897` (`454,477` maximum) and a
repetition factor of `1.1912604648`. The top-1 tie ceiling is `271,235.465853`
mean Toffolis at this width, so this decoder is 62.45% above the ceiling and
would need a 38.43% reduction to tie. Replacing S-001's DQI component with this
measurement, while holding its other components fixed, projects to `29.48041`.
That is a calculated projection, not a Kaggle score. Keep S-001 and this
baseline distinct; do not submit this decoder as a top-1 candidate.

Full verifier and build record: [`evals/2026-11-27-exp087-pro-q2-897.json`](../../evals/2026-11-27-exp087-pro-q2-897.json).

## Decision

Close the unchanged pro-q2-897 reproduction as a baseline. Any follow-up DQI
design must plausibly cut at least 38.43% from its measured mean Toffolis, or
lower the combined `R × Q² × T` cost enough to clear the same score gate, before
another full Kaggle verifier run.

## Reproduction

```powershell
py -3.14 experiments/exp-087/package_kernel.py <empty-staging-directory>
& '<path-to-kaggle.exe>' kernels push -p <staging-directory>
```

The packager reads the pinned source files and creates one self-contained
kernel script outside the Git checkout. It does not execute the source locally.
