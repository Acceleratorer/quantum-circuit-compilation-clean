---
date: 2026-11-26
title: DQI rank-99 phase-product screen
status: no_go
---

# exp-077 — rank-99 phase-product screen

## Question

Can the decoder's five GF(2^12) phase products be replaced with the existing
99-term GF(2^24) tensor phase circuit, saving Toffolis without changing the
verified phase?

## Run

- Private Kaggle kernel: `accelra/exp-077-dqi-rank-99-phase-product`, version 2.
- The first version stopped after build because the SDK is an unpackaged
  `kickmix.so`; the builder expected Python distribution metadata. The source
  launcher now falls back to the module's version string or
  `competition-sdk-unpackaged`.
- The second version built and ran the official DQI verifier at the default
  hash-derived seed and explicit seed `20261126` (102,400 shots each).
- Both verifier invocations returned `PASS`, but the default seed had one
  phase error. The experiment's stricter gate rejected any errors, so the
  private kernel ended with status `ERROR` before writing a receipt.

## Result and decision

The experiment used `src/dqi/generate.py` and its Apache-2.0
`pro_q2_897` kit. That produces a Q=897 decoder with 454,477
max/static Toffoli-like gates, not
the active exp-074 DQI source pipeline (Q=900, 318,972 static and 316,131.22
mean Toffolis). The candidate measured 440,632.83 mean Toffolis and a
424.286B DQI score, versus exp-074's 305.042B. The current rank-1 tie gate is
268.965B.

This is a wrong-source, worse-cost result with one sampled phase error. Keep
the exp-074 baseline; do not submit this build. The next DQI change must be
screened against exp-074's actual source pipeline.

Full numbers: [`evals/2026-11-26-exp077-phase-product-rank99.json`](../evals/2026-11-26-exp077-phase-product-rank99.json).
