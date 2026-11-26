---
id: exp-077
title: DQI rank-99 phase-product screen
task: dqi
status: no_go
date: 2026-11-26
result: Wrong source variant and one sampled phase error; candidate cost exceeds exp-074 baseline
---

# exp-077 — DQI rank-99 phase-product screen

This tested a 99-term GF(2^24) phase-product rewrite in the older
`pro_q2_897` generator. It did **not** build exp-074's active DQI member.

The source-built candidate used Q=897, had 454,477 max Toffolis, and averaged 440,632.83 Toffolis. Its
default-seed verifier run observed one phase error; a second seed observed
none. Its DQI score was 424.286B, above both exp-074's 305.042B baseline and
the current 268.965B rank-1 tie gate. No public submission was made.

This is a closed no-go result. Keep it only as a record of the source mismatch
and failed phase screen; future changes must build from exp-074's actual DQI
source pipeline.

See the [evaluation](../../evals/2026-11-26-exp077-phase-product-rank99.json)
and [run log](../../log/2026-11-26-exp077-phase-product-rank99.md).
