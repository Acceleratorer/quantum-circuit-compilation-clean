id: exp-025
title: Use Areeb's same-qubit retained-product DQI
task: dqi
tests: [C-028]
direction: D-007
status: submitted_pending
date: 2026-11-13
result: public source receipt PASS; local 1024-shot smoke PASS; Kaggle score pending
---

# Areeb retained-product DQI

This portfolio keeps the v12 46Q invsqrt and refined chemistry from exp-024,
and swaps only the DQI circuit for Areeb's published same-qubit retention
rewrite. The public source receipt reports 241 retained products, 889 qubits,
and a full official verifier PASS with zero errors.

- Source kernel: https://www.kaggle.com/code/areebbb/qai-fewer-toffolis-same-qubits-lb-27-08407
- DQI SHA-256: `0958baa6e5327cd71a30ff237329fb8590c7a0ef46c4394029ce231923ac5c05`
- Full source receipt: `kernel_outputs/areebbb_2708407/receipt.json`
- Full source result: score `360506288134.75055`, 102400 shots, 0 value errors, 0 phase errors
- Local smoke: 1024 shots, 0 value errors, 0 phase errors (relaxed `log2_delta=-1`)
- Archive SHA-256: `b3a4e0e2736007e24d8d99693b53ab5666bb05d5af34547a3d6b467fbca8a12`

- Submission ref: Kaggle `58292102`
- Submission state: pending at commit time; update after Kaggle returns the public score.
