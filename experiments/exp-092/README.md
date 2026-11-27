---
id: exp-092
title: Public chemistry lead audit
task: portfolio
tests: experiments/exp-092/audit_public_kernel.py
status: closed_no_go_gate
date: 2026-11-28
result: The public notebook declares only a 0.323% chemistry reduction, far short of the 18.16% gate; no private kernel was launched.
---

# exp-092 — Public chemistry lead audit

This experiment audits the public notebook
`goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-29000` as text only. The
notebook is parsed as JSON; none of its cells, imports, circuits, or
downloaded source are executed.

## Gate

The source-built chemistry baseline is `249,853,852.96`. With QV2 and
Invsqrt held fixed, the current DQI gate requires about `204,476,813.83`, or
an `18.16%` chemistry reduction.

## Result

The notebook reports:

- public score `33.29000`;
- chemistry cost `249,046,453.34`;
- 13,108 Toffolis per two-pass chemistry circuit;
- `lambda_eff = 46.912535431`;
- Apache-2.0 for the notebook and rewrites, with upstream terms retained.

That is only a `0.323%` reduction from the local chemistry baseline, far
short of the gate. The lead is therefore **closed without a private kernel**.

The experiment keeps the Kaggle public-kernel listing in `public-kernels.json` and records the declared Kaggle kernel inputs and the notebook
SHA-256 so the provenance check is reproducible.
