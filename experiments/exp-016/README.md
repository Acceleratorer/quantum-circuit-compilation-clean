---
id: exp-016
title: Hybrid 392k DQI with frontier invsqrt and 4089-angle chemistry
task: all
tests: [C-020]
direction: D-004
status: ready_for_submit_quota_exhausted
date: 2026-11-12
result: member-level PASS evidence combines into local geometric mean 25.4495384012; archive ready for next quota reset
---

# Hybrid 392k DQI frontier candidate

This candidate keeps the public 392k-Toffoli DQI decoder from `exp-015`, and swaps in the lower-cost public `invsqrt` and FeMoCo chemistry members from the 2026-11-12 Attabeezy frontier archive.

## Archive

- Local archive: `artifacts/submission_v22_392k_hybrid.zip` (kept outside Git)
- SHA-256: `11f7ddedb55441be5c4cc170d594f62afdd94cd59bfbcabf556103a945b75644`
- Size: 25,719,884 bytes

| Member | SHA-256 prefix | Source and evidence |
|---|---|---|
| `invsqrt.kmb` | `9c708f7b9abc7c7e` | Attabeezy frontier; official PASS, Q=62, cost 93,555.262676 |
| `dqi.kmb` | `4c81b7263c0b4856` | maoxin123 public 392k decoder; official PASS, Q=892, 102,400 shots, zero errors, cost 371,569,582,947.233 |
| `dfthcsos/*` | `f21b8a8725c342eb` for `submission.npz` | Attabeezy frontier / maoxin v22-4089 loaders; official PASS, Q=427, cost 297,237,077.470 |

## Local estimate

Using the official reference costs, the member-level verified costs give:

- invsqrt ratio: `22.1983689032`
- DQI ratio: `65.7735850976`
- chemistry ratio: `11.2893035313`
- geometric mean: **25.4495384012**

The hybrid composition has been packaged and preflighted. The three member verifications come from their source receipts; run the full archive verifier again if the Kaggle quota reset makes a submission slot available.

## Submission state

Kaggle reported five submissions today and zero remaining on 2026-11-12 17:37:33 UTC. The archive is ready for the next quota reset; append the submission reference and public score to `receipt.json` after upload.

## Eligibility

The DQI dataset publishes a compiled circuit without its generator. This is a strong leaderboard probe but still carries the source-delivery risk recorded in `kg-752010`.
