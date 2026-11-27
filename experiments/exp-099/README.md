---
id: exp-099
title: Conditional shared-control merge screen on source-built QV2
task: dqi
status: closed_no_go_static_screen
date: 2026-11-28
---

# exp-099 — conditional shared-control merge screen

This screen asks whether the existing `rankmerge` idea can be extended from
top-level unconditional CCX gates to CCX gates inside `PUSH_CONDITION` /
`POP_CONDITION` MBUC blocks. A successful merge would preserve the condition
while folding one shared control with CNOTs.

The input was the QV2 circuit rebuilt from the pinned Apache source in
exp-089. Its SHA-256 is
`3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3`.
The circuit was converted to text for a static pass only; no downloaded
notebook or compiled circuit was executed by this experiment.

## Result

The QV2 text contains 2,143,570 condition blocks and 42,970 CCX gates inside
them. Only 114 blocks contain two or more CCX gates (2,150 CCX total). The
linear value-fingerprint screen found **zero mergeable shared-control
clusters** and therefore a projected saving of **0 Toffoli-like gates**.

This is far below the current DQI tie gate, so no modified circuit was built,
verified, or submitted. The route is closed.

Reproduce with the source-built `.kmx` outside Git:

```powershell
.venv/Scripts/python.exe experiments/exp-099/scan_conditional_rankmerge.py ..\\qv2-static.kmx
```
