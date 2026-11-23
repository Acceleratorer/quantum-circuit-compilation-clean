---
id: exp-058
title: Static audit of the 33.17 ablation notebook
task: all
tests: static notebook inspection; downloaded code was not executed
direction: D-004
status: measurement_reference_only
date: 2026-11-23
result: The portfolio is assembled from other authors' public circuits; its local gate-deletion leads fail and it is not a source-owned candidate.
---

# exp-058: public ablation notebook audit

## Source and handling

The Kaggle CLI pulled version 32 of
[Asterios' ablation notebook](https://www.kaggle.com/code/asteriospanoras/qcc-33-1702-ablation-floors-human-vs-ai-next/versions/32)
on 2026-11-23. Kaggle metadata marks it frozen; its last run was
`2026-11-20T00:31:17.761Z`. The notebook SHA-256 is
`fb8d97fd13f3407e4ac7ab6575ceb546176fc5e681ebd337534779b96f315665`.
File hashes and input slugs are in [`provenance-manifest.json`](provenance-manifest.json).

The notebook was read as JSON/text only. No cell ran and no notebook output or
circuit archive was downloaded. Cell 94 sets `WRITE_SUBMISSION = True` and can
write a submission ZIP if its source archive is attached, so executing the
downloaded notebook would have a write side effect.

## Findings

- The notebook's 33.17033 portfolio is a public-file composition. Its own
  credits say the circuits are other authors' work; it does not provide a
  source-owned generator for that portfolio. The live rank-1 score in the
  2026-11-23 00:16 UTC snapshot is 33.83493. This is measurement evidence,
  not a candidate to submit under the standing source-owned-circuit rule.
- On a public 901-qubit DQI file, the notebook reports that deleting two
  alleged zero-product gates caused 14–20 value errors across verifier runs;
  deleting the dependent tail caused 12–18. These edits worsened measured
  cost despite saving static Toffolis. The result applies to that file and
  argues for full-verifier checks after any rewrite.
- On its public 890-qubit DQI file, a liveness audit found peak width for
  54% of the steps and 91.7% average wire liveness. That file offers no
  simple wire-reuse gain; a different algorithm/layout is needed.
- The notebook also reports exhaustive local scans finding no removable
  gate in its 39-qubit inverse or its chemistry loaders. Those floors are
  specific to its public inputs and rewrite families, not proofs about our
  source-owned circuits.

## Decision

Keep the notebook as a measurement reference only. Do not port its circuit
files or package its public portfolio. This audit closes another local
gate-deletion route on the reference circuits; it does not change the active
source-owned exp-057 DQI path, whose full output, phase, cleanup, and official
verifier gates remain open.
