---
date: 2026-11-26
title: Full 70-point FMA resource gate
status: no_go_resource_gate
---

# exp-080 — Full 70-point FMA resource gate

The official DQI verifier has no 890-qubit hard cap; its score uses
`R(eps+) * Q^2 * T`. I reopened exp-053 because its 890 target was internal,
then measured the full 70-point sample-to-ratio/history map in a private Kaggle
kernel.

The map passed all 32 cases, preserved labels and branch history, cleared
scratch, and had no phase flips. Its measured resources were `Q=958` and
`632,090` static Toffoli-like gates. At that width, the current leader tie gate
is about `246,013` mean Toffolis. This map exceeds it by a factor of `2.57`;
the older `202,075T` arithmetic-only projection omitted reversible sample
reconstruction.

**Decision:** close this schedule before building a full DQI candidate. The
no-go is cost-based, not the internal 890-qubit target. Details and source
hashes are in
[`evals/2026-11-26-exp080-full-fma-resource-gate.json`](../evals/2026-11-26-exp080-full-fma-resource-gate.json).
