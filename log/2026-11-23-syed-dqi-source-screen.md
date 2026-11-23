# 2026-11-23 — Syed DQI source screen

I inspected the README, build script, manifest, and one D69 search receipt from
the Apache-2.0 Kaggle dataset
[`syed3000/vqcc-own-circuit-portfolio`](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio).
The exact file hashes and parsed results are in the
[evaluation receipt](../evals/2026-11-23-syed-dqi-v25-screen.json).

The source README reports that its `paired-plain` generator produced an
890-qubit DQI circuit scoring `336,559,961,203.1761` over 102,400 shots with
zero value and phase errors. This is a published result, not an independent
rebuild or verification. Compared with our current DQI cost of
`347,904,227,555.5428`, it is 3.26% lower. It remains 68.42% above the latest
rank-1-equivalent DQI target of `199,830,395,473.1763`; substituting only this
cost projects a local geometric mean of `28.45296`, not a Kaggle result.

The included D69 receipt scanned 690 generators and found 11 positions with a
combined saving of only 66 Toffolis versus its `p4bs` baseline. Close that
lookup route.

I downloaded a small source subset and read it as text or JSON. No downloaded
code ran, no compiled circuit was downloaded, and no submission was made. Keep
this source as an attributed measurement baseline; do not submit its public
circuit under the standing source-owned-circuit decision.
