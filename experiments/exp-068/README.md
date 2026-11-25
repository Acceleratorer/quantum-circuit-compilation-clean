---
id: exp-068
title: DQI zero-test rewrite ablation
task: dqi
status: verified_partial_gain
date: 2026-11-25
result: DQI cost 306.441B, 1 observed value error, projected portfolio 32.96928
---

# exp-068 — DQI accuracy ablation

## Hypothesis

The eight zero-test rewrites in exp-066 may account for its four observed DQI
value errors. This run keeps only the two previously published edits and
rebuilds DQI from the pinned Apache-2.0 source. It does not read compiled
circuits as inputs and does not create a competition submission.

## Decision gate

Continue only if the official DQI verifier reports zero value errors and a
lower DQI cost than exp-066 (309694874626.0435). The eight removed edits add
at most eight static Toffolis; clearing the error penalty could be worth much
more.

## Result

The official verifier passed 102,400 shots with one value error and no phase
errors. DQI cost fell to 306441080139.99805 from exp-066's 309694874626.0435.
With the other task members fixed, the geometric-mean projection is about
32.9692, roughly 0.116 points above exp-066. This is not enough to submit as
the next portfolio. The no-edit baseline is being checked separately.

See the [evaluation receipt](../../evals/2026-11-25-exp068-dqi-zero-test-ablation.json)
and receipts/exp068/.

## Files

- kernel/ablate_zero_test_edits.py — source rebuild, two-edit ablation, and
  official DQI verification.
- kernel/kernel-metadata.json — private Kaggle kernel definition.
- receipts/ — verifier output after the run.
