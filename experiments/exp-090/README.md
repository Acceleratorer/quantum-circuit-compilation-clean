---
id: exp-090
title: Audit current public QV2 and verifier-cost leads
task: portfolio
status: closed_no_gate_candidate
date: 2026-11-27
result: Public QV2Beat matches the QV2 DQI baseline; its independent chemistry changes are too small, and the public zero-test DQI pin is provenance-excluded.
---

# exp-090 — public lead audit

This is a read-only audit. Public Kaggle notebooks were downloaded as text
and were not executed. The downloaded files remain under the ignored
`external/` directory.

## Evidence

- Live Kaggle leaderboard read with the CLI at 2026-11-27: rank 1 is
  `34.66186` (`Cat with 2 Qubits`).
- `toshiaki517/qv2beat` metadata SHA-256:
  `kernel-metadata.json` =
  `bf21360ab4889446f7d1756d5ccae798023589fb803b56f089cfe3991cadd7df`;
  notebook =
  `7643ba7894e276c3d37dab1ed15ab5d83e30b0b83b2995ed326138cb5ba99b41`.
  Its own description says its DQI is Matt Liston's compiler on Syed Asad
  Ali's source, the same QV2 lineage rebuilt in exp-089. Its new work is ten
  chemistry loaders and a coefficient refit, not a lower-cost DQI.
- `ghazarosbarseghyan91/vqcc-goodpjw-13106-t-clean-dqi-v30-gate` is a gate
  script, not a generator. It pins DQI
  `6f78ecdd636051d4d2dd8f24aaece1d454eb220aaf0df2c1d64c3d96fe22081d`, which
  is the public zero-test-cut line already excluded by exp-056. It is not an
  eligible input for a new build.
- The official DQI verifier was downloaded read-only and hash checked as
  `f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65`.
  Applying its exact repetition formula to exp-089's QV2 mean T and Q with
  zero observed errors still gives `313,736,311,904.35`, about `20.68%`
  above the current DQI tie gate. The observed three errors therefore account
  for only about `1.19%` of the measured score; error-rate cleanup cannot close
  the gap.

## Decision

Do not run a kernel from this audit. No source-owned change here has a
credible path to the required roughly 18% DQI reduction. The next DQI work
must be a new algorithmic construction or a source-level transformation with
an explicit resource screen; this lead is closed.

