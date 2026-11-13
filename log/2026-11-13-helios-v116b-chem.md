# 2026-11-13 — exp-028 Helios v116b chemistry

The latest `heliosli/qcc-circuits-live` release (`v116b_mx25_ay3`) was downloaded and
its 18-member portfolio manifest checked. The new chemistry NPZ and all 15 angle
circuits were copied into a v30 archive assembly; DQI and invsqrt were retained
byte-for-byte from v30.

Official chemistry verification passed at both the empty salt and
`notebook-verification` salt with score `296014706.5856464`, 78,080 shots, Q 427,
and 14,776 Toffoli-like gates. The DQI and invsqrt member hashes match the already
verified v30 receipt. ZIP `testzip()` passed and the archive contains exactly 18
members (SHA-256 `19f6880d88ddf1c0fabba39f2133317d7fe172ef3ca2f80fd7b6a3a858608498`).

Using the competition reference costs, the local zero-failure portfolio GM is
`27.1104387521059`, an increase of `0.0000165957` over v30. The Kaggle daily quota
was exhausted after ref `58299178`, so this candidate was recorded but not submitted.
