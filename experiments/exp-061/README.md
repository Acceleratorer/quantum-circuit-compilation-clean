---
id: exp-061
title: 7-bit chemistry QROM score gate
task: dfthcsos
tests: official DFTHC-SOS verifier (78,016 shots); static loader-count gate
direction: D-004
status: verified_no_improvement
date: 2026-11-23
result: The source-generated 7-bit family passes the official verifier at 817,512,097.94, but its 18,255 static Toffolis per pass miss the 4,500 gate needed to beat the current best chemistry score.
---

# exp-061: 7-bit chemistry QROM score gate

## Result

The 7-bit factorization from the Apache-2.0 Kaggle dataset
[`danishlynxthembones/vqcc-thembones-milestone-set`](https://www.kaggle.com/datasets/danishlynxthembones/vqcc-thembones-milestone-set)
contains 1,219 addresses and 35-bit words for the 15 ANGLE loaders. The
source-generated balanced-tree QROM emits 1,217 static Toffoli-like gates per
loader, or 18,255 per pass. The official DFTHC-SOS verifier passed 78,016
shots at `Q=405`, `T=43,010`, score `817,512,097.94`.

This is a verified baseline for the source factorization, not a competitive
candidate. Its score is 2.77× the retained best chemistry score,
`294,642,305.56`. With the same factorization and `Q_total=405`, beating that
score requires at most 4,500 static ANGLES Toffolis per pass. The builder's
3,468 count is an intentional acceptance gate; the current QROM misses it and
the builder stops before writing candidate outputs.

The guarded regeneration script is [`build_7bit_chemistry.py`](build_7bit_chemistry.py).
It reads the pinned numeric fit and builds this repository's loader circuits;
the downloaded source data is not checked in.

The verifier receipt hash is `c79a1249b28a1364f3664d6f94e428b957afdc43c79bf13ae552751bff983e6a`.
The source NPZ hash is `e05fb18f808e410ff126d68b8415e6fd4b33712760f35f90412e96ba6a331f73`.
External source data and generated `.kmb` files remain in ignored local
staging; they are not part of this commit.

## Decision

No submission was made. Close this QROM route unless a concrete XOR-loader
construction first measures at most 4,500 static Toffolis per pass while
remaining within the 128-qubit ANGLES cap. The corrected whole-task SelectSwap
screen is in [`lit-select-swap-qrom-fit`](../../literature/papers/lit-select-swap-qrom-fit.md),
and the machine-readable record is in
[`evals/2026-11-23-exp061-qrom-score-gate.json`](../../evals/2026-11-23-exp061-qrom-score-gate.json).
