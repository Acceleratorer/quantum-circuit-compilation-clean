---
id: exp-026
title: Combine cutoff-17 synthesis with same-qubit retention
task: dqi
tests: [C-029]
direction: D-008
status: complete
date: 2026-11-13
result: full official DQI PASS; Kaggle public score 27.08903
---

# Cutoff-17 plus retained products

This candidate composes the two verified rewrites: cutoff-17 synthesis from
Ozertuu and Areeb's same-qubit retained-product planner. The planner finds 241
free products again on the cutoff-17 circuit, preserving 889 qubits and saving
241 more static Toffoli-like gates.

- DQI SHA-256: `c60beda89448fad6f927de6a7c53786c82d88d33e51744b1281a9e68ca1d3e1e`
- Full official local verification: 102400 shots, PASS, 0 value errors, 0 phase errors
- DQI score: `360308609486.46423`
- Archive SHA-256: `39be3341cdf390987e869ea0bde5f0eed3e02129cef5341e3cc247da58914167`
- Local zero-failure GM estimate: `27.0890220341`

- Submission ref: Kaggle `58294002`
- Submission state: Kaggle ref `58294002`, status `SubmissionStatus.COMPLETE`, public score `27.08903`.
