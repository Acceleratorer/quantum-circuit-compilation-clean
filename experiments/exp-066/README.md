---
id: exp-066
title: Rebuild the licensed 32.85306 source portfolio with verified DQI gate cuts
task: dqi
status: in_progress
date: 2026-11-25
---

# exp-066 — source-built DQI gate rewrites

This candidate rebuilds the 18-file portfolio from Tony Li's Apache-2.0
generator dataset, then applies the ten published DQI gate rewrites to the
generated DQI assembly and recompiles it. The base source DQI is pinned at
`4b572141…`; the rewritten output is expected to match `6f78ecdd…`.

The kernel input requests dataset version `2`. An earlier fingerprint
discrepancy (`50be321a…` locally and `e672ec5a…` in Kaggle) came from
platform-specific ordering of `Path` objects, not different source files; the
SHA-256 comparison confirmed all 88 files matched. Fingerprinting now sorts
normalized relative paths, giving the same result on Windows and Linux, and
records each mounted source-file hash. The build checks the rebuilt portfolio
member hashes, the rewritten DQI hash, and all three official verifiers. It
reads no public compiled circuit as input. The generator dataset's
`notices/RELEASE_NOTICES.txt` credits the
underlying Team ThemBones work and earlier contributors. The ten DQI edits are
credited separately in [UPSTREAM.md](UPSTREAM.md).

## Current gate

Kernel version 5 rebuilt the candidate and passed all three unmodified official
verifiers. Its archive was submitted as Kaggle submission `58878878` and scored
`32.85341`, only `0.00035` above the `32.85306` source baseline. Rank 1 was
`34.25544`; the team's leaderboard best remains `33.17067` (rank 615), so this
candidate did not improve its rank.

## Receipts

- [Kernel build and verifier results](receipts/kernel-v5-result.json)
- [Archive integrity and member hashes](receipts/archive.json)
- [Dataset source comparison](receipts/source-comparison.json)
- [Kaggle submission status](receipts/submission.json)
- [Submission evaluation record](../../evals/2026-11-25-exp066-submission-58878878.json)
