---
id: exp-043
title: Audit rank-1 public source leads
task: dqi
tests: static notebook and provenance review; no code executed
status: no_improvement
result: the claimed rank-1 notebook only copies a public archive; the current leader's username has no public notebook or dataset; neither source provides a verified candidate
---

# Audit rank-1 public source leads

## Source handling

- Source: [Kaggle notebook](https://www.kaggle.com/code/rishabhbafnaiiitd/quantum-circuit-compilation-rank-1-breakthrough).
- Kernel ID: `143492566`; the latest-source pull did not expose a version number. Kaggle listed its last run as `2026-11-09T06:40:52Z`.
- Pulled on `2026-11-18` into ignored `external/rishabh-rank1-breakthrough/`.
- Notebook: 12,213 bytes, SHA-256 `de722a449c3742f3a9a860fa73b6c789fe1fe8fe2fbfd8f9bd97beed1fdc308a`.
- Metadata: 918 bytes, SHA-256 `4818512e26e154cd427fc4ac3ccbe018ddc5fa7c167c39e9fe06fc15b31eea79`.
- The download was inspected as JSON/text only. It was not imported or run. The metadata has no license declaration.

## Findings

The notebook's code does not implement its claimed destructive continued-fraction decoder, 52-qubit inverse, or chemistry rank truncation. It scans Kaggle inputs for a ZIP containing 18 files, copies those files after matching hard-coded SHA-256 pins, and packages them. The cached notebook has no executed outputs or verifier receipt.

Its claimed 780-qubit DQI is inconsistent with the required 840-qubit syndrome input alone. The numbers therefore do not establish a valid candidate. The archive-copy workflow also conflicts with our standing rule that submissions must come from our own generators.

## Decision

No-go: do not run or submit this notebook. The title and projected score are unsupported by its code and cached evidence.

## Current leader source search

The `2026-11-18T04:15:43Z` public leaderboard CSV lists the leader team as `aadi_stonks` and its member username as `aadistonks`. Kaggle CLI searches for that exact username returned no public notebooks and no public datasets at capture time. The account search is therefore exhausted for now; the leader's source remains unavailable publicly.

The separate primary-source BM decoder in [Andi Gu et al.](https://arxiv.org/abs/2610.22367) is real and has Apache-2.0 code at [andigu/uncompute](https://github.com/andigu/uncompute). It reports 440,000 Toffolis and 1,837 qubits using a `T × Q` objective; under this competition's `Q² × T` cost, that is about 4.3 times the current DQI cost, so porting it unchanged is not a useful score direction. No code from that repository was downloaded or executed in this audit.
