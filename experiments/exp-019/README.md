---
id: exp-019
title: Reproduce Asterios 5778cdd5 DQI retention build
task: dqi
tests: [C-023]
direction: D-004
status: ready_for_submit_quota_exhausted
date: 2026-11-13
result: rebuilt the public notebook's 2-product retention circuit byte-for-byte; Kaggle official logs show PASS at default, s1 and s2 salts with zero errors and score 371568084355.5092
---

# Asterios 5778cdd5 retention build

The public notebook `asteriospanoras/qcc-25-449-best-portfolio-392k-dqi-splice` contains a two-product retention planner that was described but not shipped in its archive. I ported its retention cell to a Windows-safe module and rebuilt the circuit from the public `4c81b726` DQI binary.

## Reproduction

```powershell
python src/dqi/retain_5778.py <path-to-4c81b726.kmb> <path-to-output.kmb>
```

The output hash is pinned to:

`5778cdd5d710567b970544b8929547cf3be37fe84f2a11643d49edc74eca96cc`

The planner selects exactly two retained product runs, adds two classical correction bits, and keeps the 892-qubit layout unchanged. The compiled output is 518,776,919 bytes.

## Official verification evidence

Asterios's Kaggle kernel ran the unchanged competition verifier on the exact hash:

| Salt | Status | Score | Mean Toffoli | Value errors | Phase errors |
|---|---|---:|---:|---:|---:|
| default | PASS | 371,568,084,355.5092 | 392,014.3507910156 | 0 | 0 |
| `s1` | PASS | 371,567,970,197.80865 | 392,014.2303515625 | 0 | 0 |
| `s2` | PASS | 371,568,012,869.2592 | 392,014.27537109377 | 0 | 0 |

The default-salt result is about 1.50 million lower than the exp-016 DQI member while preserving zero failures. The evidence is recorded in the kernel log and the exact hash is independently reproduced locally.

## New hybrid archive

- Archive: `artifacts/submission_v24_5778_retained_hybrid.zip` (kept outside Git)
- SHA-256: `531f7a4263a0595d634a448da8fa23c37ed834bbcdbf9e6b98de3bb2a5ff4a28`
- Size: 27,963,149 bytes
- Members: invsqrt `9c708f7b`, DQI `5778cdd5`, chemistry `e9cffb84`
- Local geometric mean estimate: **25.4495735281**

The estimate uses the same per-task reference costs as exp-016 and the default-salt DQI result above. It is a local estimate, not a leaderboard score.

## Submission state and eligibility

Kaggle still reports five submissions today and zero remaining. Submit v24 after the UTC quota reset; keep v23 as a fallback. The DQI source is now reproducible from a public notebook and the public `4c81b726` binary, which materially improves the source-delivery record, though the host's final eligibility interpretation remains external.
