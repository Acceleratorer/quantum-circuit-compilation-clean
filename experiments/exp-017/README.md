---
id: exp-017
title: Exact 64d0c2f9 DQI retention patch audit
task: dqi
tests: [C-021]
direction: D-004
status: negative_result
date: 2026-11-13
result: hash matched the published 64d0c2f9 patch, but full 102400-shot verification had 2 phase errors; hybrid GM 25.3778675 is below exp-016
---

# Exact 64d0c2f9 DQI retention patch audit

The public Pablo Diego starter notebook describes a six-edit retention patch for the 392k DQI decoder. I reproduced those edits against the local `tmp_v22_392k_dqi.kmx`, converted the result back to `.kmb`, and matched the notebook's expected circuit hash exactly.

## Reproduction

- Base DQI SHA-256: `4c81b7263c0b4856068a691295d945ae627aa6af4e62e45f2c40411b6d01e5d9`
- Patched DQI SHA-256: `64d0c2f9e0d677d588791b9d00b19edaf518aabf7e95214c50a03f685ee2ea56`
- Archive: `artifacts/submission_v13_64d0_hybrid.zip`
- Archive SHA-256: `9c793d3927ba7b2035f5517e6f84a8fa1d43a9d4b2457e5f47612a421d57ff5f`

## Official verification

The unmodified competition DQI verifier ran all `102,400` default-salt shots and returned `PASS`, but reported **2 phase errors** and zero value errors. The measured score was `374,726,585,644.2963`; mean Toffoli count was `392,013.9174`.

Combining that DQI result with the exp-016 invsqrt and chemistry receipts gives a local geometric mean of **25.3778675217**, versus **25.4495384012** for the unchanged exp-016 archive. The two phase errors dominate the tiny Toffoli reduction, so exp-016 remains the primary candidate. Keep this archive only as a private-leaderboard hedge after the quota resets.

The full verifier JSON is tracked at `logs/dqi_full_102400.json`; the exact line edits are in `patch_retention.py`.
