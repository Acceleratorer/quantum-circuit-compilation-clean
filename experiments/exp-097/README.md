---
id: exp-097
title: Joint GF(2^12) tensor lift resource screen
task: dqi
tests: tmp/joint_lift_screen_20261128.py
status: closed_no_go_gate
date: 2026-11-28
result: The fixed seven-point GF(8) lift expands to a 49-term GF(2^12) joint tensor; projection through the existing 99-term GF(2^24) provenance tensor yields only a 931-T best-case saving, far below the roughly 57,861-T DQI gate.
---

# exp-097 — Joint GF(2^12) tensor lift resource screen

This is a local tensor/resource screen for the joint-pair construction in
`src/dqi/qv2_m4/kit/repo/src/dqi_q18_retire/`. It reconstructs the published
seven-term GF(8) tensor, lifts it through seven GF(8) evaluation points, and
projects the existing 99-term GF(2^24) provenance tensor to GF(2^12).

## Result

The screen produced:

| quantity | result |
|---|---:|
| published GF(8) tensor terms | 7 |
| lifted joint GF(2^12) terms | 49 |
| projected GF(2^12) terms | 99 |
| all-context minimum | 147 |
| all-context maximum | 346 |
| all-context mean | 246.000244140625 |
| zero-context count | 346 |
| nonzero-context minimum | 147 at `c = 2545` |
| nonzero-context maximum | 246 |
| projected full saving across 31 best nonzero contexts | 931 T |

The current QV2 source build measures mean `333,238.013 T`; the refreshed
rank-one DQI tie gate is about `275,376 T`, so the screen would need roughly
`57,861 T` of verified reduction. The fixed lift is therefore not a credible
near-gate construction. Its zero-context count is also worse than the nominal
baseline accounting (`346` versus `192`).

This is a tensor/resource screen only. It did not launch a Kaggle kernel, run
the official verifier, or produce a submission candidate. The original local
screen remains outside the repository because it is a one-off audit script.

The machine-readable receipt is
`evals/2026-11-28-exp097-joint-gf12-lift-screen.json`.
