---
id: exp-093
title: Public H8 live-search lead audit
task: portfolio
tests: experiments/exp-093/audit_h8_search.py
status: closed_no_go_gate
date: 2026-11-28
result: The public H8 script exposes a stochastic 2,400-second search but no declared chemistry cost, score, leaderboard result, or near-gate resource estimate; no private kernel was launched.
---

# exp-093 — Public H8 live-search lead audit

This experiment audits the public script
`toshiaki517/qcc-prv-h8-live-search-v3` as source text only. The source is
parsed with Python's AST; its embedded Apache loader archive, generators,
verifiers, circuits, and subprocesses are not executed.

## Gate

The source-built chemistry baseline is `249,853,852.96`. With QV2 and
Invsqrt held fixed, the current DQI gate requires about `204,476,813.83`, or
an `18.16%` chemistry reduction.

## Result

The script declares:

- a `2,400` second H8 search budget;
- ten loader ids (`2,3,4,6,9,10,12,8,13,14`);
- existing frontier and `prv_chem` inputs;
- reference constants used only after runtime verification to compute a GM.

It does **not** declare a chemistry cost, Toffoli count, leaderboard score,
or resource estimate near the gate. Any useful result would require launching
the private GPU kernel and waiting for stochastic search output, so this lead
is closed without that spend.

The machine-readable receipt is in
`evals/2026-11-28-exp093-h8-search-audit.json`.
