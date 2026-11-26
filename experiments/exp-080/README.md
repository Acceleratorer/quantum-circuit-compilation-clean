---
id: exp-080
title: Full 70-point normalized FMA recurrence gate
task: dqi
status: no_go_resource_gate
---

# exp-080 — Full 70-point normalized FMA recurrence

## Why reopen this path

The official DQI verifier has no 890-qubit hard cap; it scores
`R(eps+) * Q^2 * T`. The 890 value in exp-053 was an internal score-equivalence
gate, not a validity rule. At the live leader's score, the tie gate is about
`284,402` mean Toffolis for `Q=891`. Exp-053's incomplete arithmetic-only
projection was `202,075`, leaving about `82,327` Toffolis for omitted phase,
cleanup, and integration work if its count scales.

This experiment compiled the **full 70-point sample-to-ratio/history map** with
the existing measurement-recycle encoder, kept branch history explicitly, and
measured exact `Q` and static Toffoli count. It passed 32 deterministic
GF(2^12) cases, including clean scratch and zero phase flips. At `Q=958` it
uses `632,090` static Toffolis, versus a current score-equivalent tie gate of
about `246,013` mean Toffolis. The static cost is `2.57x` the gate, so this
layout is a no-go before a full DQI build or official verifier run.

## Source and execution

- Reuses the source-owned prefix encoder in `experiments/exp-053` without
  editing its historical implementation.
- Extends its rank comparator from the hand-coded first five pivots to a
  reversible constant comparison for all 70 pivots.
- Embeds the existing field-arithmetic helper from `src/dqi/pro_q2_897/exp/arithmetic/field.py`;
  its Apache-2.0 lineage and notices are in `src/dqi/NOTICE` and `src/dqi/LICENSE`.
- Builds and runs only as a **private Kaggle kernel**. The result and source
  hashes are recorded in `evals/` below.

The private run is recorded in
[`evals/2026-11-26-exp080-full-fma-resource-gate.json`](../../evals/2026-11-26-exp080-full-fma-resource-gate.json).

## Gate

The measured map does not meet the gate. Close this schedule and return to the
source-level DQI search. The earlier `202,075T` arithmetic-only projection
missed the cost of reversible sample reconstruction.
