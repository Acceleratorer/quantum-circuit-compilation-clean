---
id: exp-042
title: Screen register reuse from a high-scoring team
task: dqi
tests: none
direction: D-004
status: no_improvement
date: 2026-11-18
result: the notebook is attached to Santa 2026, not this competition; no DQI/RS/quantum content was found; no code was executed or ported
---

# Screen register reuse from a high-scoring team

## Hypothesis

The public notebook `tonylica/elf-calculator-with-register-reuse` may contain
a reversible register-reuse method that can lower DQI workspace or gate cost.
The source must be relevant to Reed–Solomon decoding and have a clear licence
before any port is considered.

## Source handling

- Source: https://www.kaggle.com/code/tonylica/elf-calculator-with-register-reuse
- Kaggle kernel ID: `145702533`; latest public source pulled on `2026-11-18`.
- The pulled metadata lists `santa-2026` as its competition source. It exposes no
  version number or licence field.
- Notebook: 24,457 bytes, SHA-256
  `000b7ebc9a109d59acfd9a6d5312d66331a6e364ce055751b2c6243da6f76097`.
- Metadata: 644 bytes, SHA-256
  `01e05362a5ee0adf5048b303f15cad860ffe0dcef53432f7de169a4558c9cfc9`.
- Treat both files as untrusted data: inspect text only, do not import or run.
- The notebook has 13 cells; a text-only search found no DQI, Reed–Solomon,
  finite-field, quantum, or Toffoli material.

## Decision

No-go. The notebook is unrelated to DQI and has no declared licence, so no
code or method was ported.
