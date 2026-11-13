---
id: exp-027
title: Raise DQI cutoff to 18 with same-qubit retention
task: dqi
tests: [C-030]
direction: D-009
status: submitted_pending
date: 2026-11-13
result: full official source PASS; local zero-failure GM 27.11042; Kaggle score pending
---

# Cutoff-18 plus retained products

This candidate uses Areeb's same-qubit retained-product planner on the cutoff-18
DQI rewrite. The source receipt reports 889 qubits, 383,414 static
Toffoli-like gates, 102,400 verified shots, and zero value or phase errors.
The higher cutoff excludes a small probability tail while preserving the same
qubit width and 241 retained products.

- Source kernel: https://www.kaggle.com/code/areebbb/qai-fewer-toffolis-same-qubits-lb-27-11042
- DQI SHA-256: `821bf8d157c03c3e868a0099b0ab1438cfba664ab1bc6fec3210654099b672a3`
- Full source receipt: `kernel_outputs/areebbb_2711042/receipt.json`
- Full source DQI result: score `360209905486.0156`, 102400 shots, 0 value errors, 0 phase errors
- DQI geometry: 889 qubits, 383,414 static Toffoli-like gates, reaction depth 40,891
- Chemistry: score `296015250.2044768`, 427 qubits, 14,776 Toffoli-equivalent cost
- Invsqrt: score `80162.73214111096`, 46 qubits
- Archive SHA-256: `86e4300cb2bef05944bbe8cb4f802f56f4c2481aaa73f579d7d51b808065e147`
- Local zero-failure GM estimate: `27.110422140236516`

- Submission ref: Kaggle `58299178`
- Submission state: `SubmissionStatus.PENDING`; public score pending.
