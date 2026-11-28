---
id: exp-101
title: Screen Diana v156 source-owned DQI generator
task: dqi
tests: source-manifest; native-4096
status: closed_no_go_score_gate
date: 2026-11-28
result: Source-owned v156 build is clean locally, but its verifier bill is 31.7% above the live tie gate; no private kernel or competition submission.
---

# exp-101 — Diana v156 DQI source screen

This was the single follow-up to exp-100.  The source is the public
`dziyanavalenta/q2026-v156-dqi-generator` dataset.  The local screen used the
released source recipe and its `release_d80` output hash; it did not use a
compiled submission archive as an input.

## Evidence

- Source archive SHA-256: `55da8b50e5b20a76e196d297391482a4864f1527f42360322f9139b04a297783`.
- Candidate circuit SHA-256: `1abd01dedaeaad13194426261b221691268e7b88b53c5817eaf8e8d45c5e2912`.
- Width: `Q=890`.
- Static Toffoli count: `360,498`.
- Native diagnostic mean: `359,300.734` over `4,096` shots.
- Native diagnostic failures: `0` value, `0` phase.
- Common-R verifier bill: `339,035,243,514`.

## Gate and decision

The current rank-1 tie gate is `257,362,135,701.191` verifier-cost units.
At Q=890, using the v150 reference repetition factor gives a mean-Toffoli
equivalent gate of about `271,499`.  The v156 common-R bill is `31.73%` above
the cost gate and its native mean is about `32.34%` above that reference mean
gate.  Zero observed diagnostic failures do not close this resource gap.

Close the lead as a score no-go.  Do not launch a private Kaggle kernel and do
not submit it.  Reopen DQI work only when a new source-owned construction has a
local resource screen near or below the gate.

Receipt: [`evals/2026-11-28-exp101-diana-v156-dqi.json`](../../evals/2026-11-28-exp101-diana-v156-dqi.json).
