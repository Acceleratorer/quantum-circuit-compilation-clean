---
id: exp-028
title: Helios v116b chemistry refit on the v30 portfolio
task: dfthcsos
tests: [C-031]
direction: D-010
status: verified_ready_for_submit
date: 2026-11-13
result: chemistry PASS; portfolio GM 27.1104387521; submission quota was exhausted after v30
---

# Helios v116b chemistry refit

This experiment keeps the v30 DQI and invsqrt members byte-for-byte and swaps only
`dfthcsos/submission.npz` to the latest `heliosli/qcc-circuits-live` release
(`v116b_mx25_ay3`). The 15 angle circuits are also pinned by SHA-256.

- Source dataset: https://www.kaggle.com/datasets/heliosli/qcc-circuits-live
- Source portfolio manifest: `v116b_mx25_ay3`, salt `notebook-verification`
- Chemistry NPZ SHA-256: `865f52ce67b3d4908208699bf42806502aff6528b4d5ee682c0b3c18a87890bc`
- Chemistry verifier: PASS, score `296014706.5856464`, Q `427`, 14,776 Toffoli-like gates
- DQI retained from v30: `821bf8d157c03c3e868a0099b0ab1438cfba664ab1bc6fec3210654099b672a3`
- Invsqrt retained from v30: `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`
- Archive SHA-256: `19f6880d88ddf1c0fabba39f2133317d7fe172ef3ca2f80fd7b6a3a858608498`
- Archive size: `47,488,121` bytes, 18 members, ZIP integrity PASS
- Local zero-failure GM: `27.1104387521059`
- Improvement over v30 chemistry: `543.6188304` lower cost; GM delta `+0.0000165957`

The improvement is reproducible but small. It does not close the gap to the public
leaderboard frontier, so no new Kaggle submission was attempted while the daily
submission quota remained exhausted.
