---
id: exp-022
title: Verify Syed v12 own-circuit portfolio
task: all
tests: [C-026]
direction: D-005
status: verification_partial
date: 2026-11-13
result: chemistry and DQI independently PASS; invsqrt smoke PASS, exhaustive run still pending; candidate uses the public Apache-2.0 Syed v12 portfolio with 46Q invsqrt, 889Q DQI, and 4074-static-angle chemistry
---

# Syed v12 own-circuit portfolio

This candidate was discovered from the public Kaggle notebook and dataset:

- Notebook: https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook
- Dataset: https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio
- License: Apache-2.0 (see the source dataset's `LICENSE` and `NOTICE`)

The portfolio is materially better than the current v24 archive on all three local task costs:

| task | Syed v12 stated result | v24 reference in this repo |
|---|---:|---:|
| invsqrt | Q=46, cost 80,162.76 | Q=62, cost 93,555.26 |
| dqi | Q=889, mean T=383,156, zero-failure cost 3.6073e11 | Q=892, cost 3.71568e11 |
| dfthcsos | cost 296,635,967.59 | cost 297,237,044.95 |

All 18 submission members are kept outside Git in the local staging/archive area. Git stores only the manifest, receipts, verifier logs, and reproduction pointers.
