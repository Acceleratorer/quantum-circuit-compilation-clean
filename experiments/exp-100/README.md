---
id: exp-100
title: Screen Diana v150 source-owned DQI generator
task: dqi
status: closed_no_go_score_gate
date: 2026-11-28
result: Source build and official verifier PASS, but the measured cost misses the live tie-gate; no competition submission.
---

# exp-100 — Diana v150 DQI source screen

This is the single active lead after exp-099.  The source archive is the public
`dziyanavalenta/q2026-v150-dqi-generator` dataset, released with a traced build
recipe and attribution.  It is the DQI generator used in the public v154
submission notebook of the current rank-1 team.  The archive contains source
and build receipts, not a compiled circuit used as a build input.

The private Kaggle kernel extracts the archive, runs its `build.py` with the
competition Python runtime, and runs the official DQI verifier.  It records Q,
mean Toffolis, repetition factor, error counts, the exact output hash, and the
derived rank-1 tie gate.  The source archive is not copied into this
repository and no competition submission is made by this experiment.

## Gate

Continue only if the measured verifier cost is plausibly below the refreshed
rank-1 tie gate.  Otherwise close the lead and do not submit it.

## Result

Version 3 of the private Kaggle kernel rebuilt the exact source hash
`4426ca10776fcfaf3ecb75211a812a68c37228f0d3f95fd1207383d5a308deca` and passed
the official verifier on 102,400 shots.  It measured Q=890, mean T
`360,290.2447`, verifier cost `341,530,299,301.27`, one value error, zero
phase errors, and repetition factor `1.1967315`.

At the live rank-1 score `34.77295`, the derived DQI tie gate is
`257,362,135,701.19`; this candidate is `32.70%` above it.  Holding the other
components fixed would project S-001 to `31.64317`.  The lead is closed as a
score no-go and was not submitted.

Receipt: [`evals/2026-11-28-exp100-diana-v150-dqi.json`](../../evals/2026-11-28-exp100-diana-v150-dqi.json).

## Reproduce

```powershell
py -3.14 experiments/exp-100/package_kernel.py ..\\exp100-kernel
uvx --with six --from kaggle kaggle kernels push -p ..\\exp100-kernel
```

