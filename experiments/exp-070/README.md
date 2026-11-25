---
id: exp-070
title: Source-built V18 chemistry loader check
task: dfthcsos
status: verified_but_worse_than_baseline
date: 2026-11-25
result: PASS at 284624435.77; 11.52% higher cost than exp-066
---

# exp-070 — source-built chemistry loaders

Rebuilt the 15 ANGLE_k loader circuits from Goodpjw2008's Apache-2.0 V18
notebook, [QCC | Shorter Chemistry Loaders | LB 33.24213](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-24213).
The source notebook plans generated loaders 2–14. Loaders 0–1 were generated
from the source angle words with a sparse pair lookup. No compiled circuit
input was read.

## Result

The unmodified official DF-THC-SOS verifier passed all 78,016 shots. The
candidate uses 4,240 Toffolis per pass and stays within the 128-qubit ANGLE_k
cap. Its task cost is 284,624,435.77.

This is worse than exp-066's verified chemistry cost of 255,214,794.21 by
11.52%. With exp-069's DQI and exp-066's other members held fixed, the
geometric-mean projection is 31.84075, below exp-066's 32.85341 public result
and exp-069's 33.01962 projection. This is a local estimate, not a Kaggle
score. Do not submit this candidate.

The source notebook SHA-256 is
`a0e7554c2552c799fe8ef7edccd9110a2b75f65052eaac42495257a7b4494997`; the
source factorization NPZ SHA-256 is
`71e1c87fe316bde17a00b3a484c4c7eb5c92d16ba8537270b979dead8b9cf37e`.
Detailed verifier metrics are in [the evaluation record](../../evals/2026-11-25-exp070-source-chemistry.json).
