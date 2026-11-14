---
id: exp-033
title: Maoxin v25 4044-loader chemistry with constrained refit
task: portfolio
tests: [C-036]
status: submitted_pending_score
date: 2026-11-14
result: chemistry official PASS; projected local GM 27.2898566324
---

# Maoxin v25 chemistry refit

This candidate keeps the exp-031 inverse and DQI members and replaces the
chemistry member with Maoxin v25's 4,044-Toffoli loaders, followed by a
constrained reduced-gradient refit of the factorization weights.

## Evidence

- **Inverse:** `4560ac0c017b`, official source PASS, 46 qubits,
  score `78765.63681893334`.
- **DQI:** `821bf8d15703`, official source PASS, 889 qubits,
  score `360209905486.0156`, zero value and phase errors in `102400` shots.
- **Chemistry:** `06d67d21dbfe`, official local PASS, 427 qubits,
  `14750` Toffoli-like gates, score `295362181.14128023`,
  `78080` verified shots, `lambda_eff=46.895912537812926`.

The projected zero-failure geometric mean is `27.289856632448792`, an
improvement of `0.000028872220689` over the unrefit Maoxin v25 portfolio.
The archive has been submitted to Kaggle as the required `submission.zip`;
official scoring is pending (ref `58348395`).
