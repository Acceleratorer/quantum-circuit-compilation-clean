---
id: exp-032
title: Atakan portfolio with constrained chemistry refit
task: portfolio
tests: [C-035]
status: verified_ready_for_submit
date: 2026-11-13
result: chemistry official PASS; projected local GM 27.2699740595
---

# Atakan portfolio with chemistry refit

This is exp-031 with a constrained refit of the chemistry weights. The inverse
and DQI members are unchanged, so the archive remains directly comparable.

## Evidence

- **Inverse:** `4560ac0c017b`, 46 qubits, score `78765.63681893334`,
  `200540928` verified shots.
- **DQI:** `821bf8d15703`, 889 qubits, score `360209905486.0156`,
  `102400` shots, zero value and phase errors.
- **Chemistry:** `bdd3cd1df1b5`, 427 qubits, `14776` Toffoli-like gates,
  score `296008698.5905082`, `78080` verified shots, official PASS.

The projected zero-failure geometric mean is `27.26997405953837`, an
improvement of `0.000002248643646` over exp-031. This is a local estimate;
Kaggle submission is held until the quota resets.
