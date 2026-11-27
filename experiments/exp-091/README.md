---
id: exp-091
title: Static chemistry loader tensor-rank screen
task: dfthcsos
tests: experiments/exp-091/chemistry_tensor_screen.py
status: no_go_rank99_pencil
date: 2026-11-28
result: The V22 loader payload has 123–131 product terms per custom loader; a 128-trial matrix-pencil screen found no rank-99 decomposition witness, so no kernel was launched.
---

# exp-091 — chemistry loader tensor-rank screen

This is a static screen of the tracked V22 loader payload. It decodes the
payload data only; it does not execute downloaded notebook code, build a
circuit, run a verifier, or submit to Kaggle.

## Gate

Replacing the measured source-built chemistry cost `249,853,852.96` while
holding the exp-089 QV2 DQI projection and Invsqrt fixed would require about
`204,476,813.83`, an 18.16% reduction. A promising loader route would need a
substantial reduction in the 123–131 bilinear product terms per custom loader.

## Screen

- The ten custom V22 loaders contain 1,277 product terms in total and no
  duplicate `(left feature, right feature)` pair.
- Their left/right flattening ranks are 98–99, so rank 99 is the smallest
  possible target for a full-rank bilinear decomposition.
- For 128 seeded random output slices per loader, the matrix-pencil
  sufficient test for a rank-99 decomposition found no witness. This is not a
  lower-bound proof; it only rejects the cheap simultaneous-diagonalization
  route.

## Decision

Do not launch a private kernel from this screen. A real candidate needs an
explicit tensor decomposition and a source-bound loader emitter, then a
resource estimate that clears the chemistry gate before full verification.
