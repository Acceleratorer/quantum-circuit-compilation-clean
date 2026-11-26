---
id: exp-082
title: Source-built V22 chemistry with base DQI
task: portfolio
status: completed_historical_ineligible
date: 2026-11-26
result: All official verifiers PASS; Kaggle ref 58958257 completed at 33.08801; excluded from source-owned candidates by exp-056 provenance review
---

# exp-082 — V22 chemistry loader candidate

This candidate changes only the chemistry loaders from exp-074's V20 payload
to Goodpjw2008's V22 source description. It keeps exp-074's refitted weights,
source-generated base chemistry inputs, DQI, and Invsqrt.

## Result

The V22 notebook reports 3,306 loader Toffolis per pass while keeping its
compiled loader 0. Our source-generated loader 0 costs 263, so the source-built
candidate uses 3,324 per pass. The other 14 loaders match the V22 counts. The
official chemistry verifier passed at default and salt 42 (78,016 shots each),
with 13,148 Toffolis total. Invsqrt and DQI also passed. The measured local
verifier GM is `33.08804494`, up `0.00167755` from exp-074's `33.08636739`.

This is a small local improvement in the verifier metric. The bundle was
submitted as Kaggle ref `58958257` and later completed at public score
`33.08801`. Its local GM is `0.00167755` above exp-074's local score.
The live rank-1 score is `34.50408`, so this submission records the incremental
measured result and does not close the rank-1 gap.

## Eligibility correction — 2026-11-27

Treat this as a historical measurement, not an eligible source-owned candidate.
The DQI and Invsqrt inputs are based on
`tonylica/quantum-ai-32-85306-task-generators`. The static provenance review in
exp-056 found that dataset reconstructs released KMX stages byte-for-byte and
rejected it for reuse. Do not use these components in a future submission or
describe this score as a compliant source-owned result.

## Source and handling

- V22 loader descriptions are adapted from Goodpjw2008's version-26 notebook,
  which states Apache-2.0. The notebook was read as text; its code was not run.
- The 3,306-Toffoli payload is data. The builder emits new KMB files from that
  payload and source-generated register metadata; it does not copy candidate
  circuits from the notebook.
- The chemistry table is the pinned Maoxin v4 raw parameter table. The code
  uses the source-built Tony Li dataset for the base DQI, Invsqrt, and loader
  circuits.
- Static review found the adapted loader builder reads its pinned text payload,
  runs its local loader model, and writes generated circuits and a factorization.
  The private Kaggle kernel runs the trusted, hash-pinned source generator and
  official verifiers. No downloaded notebook is executed.

Attribution and modifications are in [NOTICE.md](NOTICE.md); hashes and
provenance are in [source.json](source.json).

The verifier evaluation summary is in
[`evals/2026-11-26-exp082-source-built-v22-chemistry.json`](../../evals/2026-11-26-exp082-source-built-v22-chemistry.json).
Raw Kaggle outputs and the generated archive remain under the ignored `out/`
directory.
