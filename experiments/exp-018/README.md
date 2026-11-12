---
id: exp-018
title: Fresh Apache chemistry circuit swap on the 392k hybrid
task: dfthcsos
tests: [C-022]
direction: D-004
status: ready_for_submit_quota_exhausted
date: 2026-11-13
result: new public 4a2db87b0c13 chemistry member passes the full 78080-shot verifier and improves the hybrid estimate from 25.4495384012 to 25.4495393293; invsqrt and DQI unchanged
---

# Fresh Apache chemistry swap

The refreshed `manwithacat/vqcc-apache-public-circuits` dataset added chemistry prefix `4a2db87b0c13`. Its 15 ANGLE circuits and factorization were downloaded individually, verified with the official verifier, and combined with the unchanged exp-016 invsqrt and DQI members.

## Archive

- Local archive: `artifacts/submission_v23_392k_hybrid_e9cff.zip` (kept outside Git)
- SHA-256: `4158a63045123aca97c90fdc3f883bfa3924bc81e85df52ad37496f350bd2d8a`
- Size: 27,963,084 bytes

| Member | SHA-256 prefix | Evidence |
|---|---|---|
| `invsqrt.kmb` | `9c708f7b9abc7c7e` | exp-016 official PASS, cost 93,555.262676, Q=62 |
| `dqi.kmb` | `4c81b7263c0b4856` | exp-016 official PASS, 102,400 shots, zero errors, cost 371,569,582,947.233, Q=892 |
| `dfthcsos/submission.npz` | `e9cffb841c4b8bac` | new Apache prefix `4a2db87b0c13`; paired with 15 new angle loaders |

## New chemistry verification

Official `dfthcsos/verify.py` with default salt and `--shots-per-address 64`:

- PASS, 78,080 verified shots
- score: `297,237,044.9509761`
- lambda_eff: `46.907378146123214`
- Toffoli count: `14,840`
- Q: `427`
- brot/J: `8/5`
- error_1: `0.019999979999998616`
- error_2: `0.019999997000000005`

The new circuit is the same 4,089-Toffoli angle family as the current chemistry frontier and trims a small amount of heuristic cost through its factorization metrics. The improvement is only about 32.5 score units for this task.

## Portfolio estimate

Keeping the exp-016 invsqrt and DQI costs and replacing only chemistry gives a local geometric mean estimate of **25.4495393293**, an improvement of `+0.0000009281` over exp-016.

The DQI candidate from the same dataset refresh (`8eccde65e8b7`) was rejected before submission: it has the same Q=892 but a higher static count (401,180 vs 392,346 Toffoli-like gates), so it cannot beat the verified 392k candidate without an implausibly lower dynamic ratio. The fresh invsqrt (`da4fbc102219`) was rejected because Q=90 vs the 62-qubit frontier.

## Submission state

Kaggle still reports five submissions today and zero remaining at the time of this experiment. Submit this archive after the UTC quota reset; keep exp-016 as a fallback.

## Eligibility

The DQI member remains a compiled public artifact without its generator. This is a leaderboard probe and carries the same source-delivery risk recorded in `kg-752010`.
