---
id: exp-064
title: Rebuild Syed's dfthcsos candidate from source
task: dfthcsos
status: source_rebuilt_and_officially_verified
date: 2026-11-23
result: Score 295006518.96994764; official verifier PASS on 78,080 shots; 15 generated circuits match the pinned manifest hashes.
---

# exp-064: source-built dfthcsos

## Result

Private Kaggle kernel [`accelra/exp-064-dfthcsos-source-audit`](https://www.kaggle.com/code/accelra/exp-064-dfthcsos-source-audit), version 1, rebuilt all 15 ANGLE circuits from the pinned compiler and plans, then passed the unmodified official verifier.

- Score: `295,006,518.96994764`
- Resources: Q=`427`, Toffoli=`14,718`, ANGLE width=`128`
- Verification: `78,080` shots, `brot=8`, 15 circuits
- Submission digest: `e3dd5a3eb24b6947efd225b9973d9a71d15c540a3c341450589da667325e5275`
- Build / verification time: `10.60s` / `27.69s`

The accuracy and gap checks pass very close to their limits: `error_1` and `error_2` are each about `0.019999988` against `0.020`, and `E_gap=3.914898003000417` against the strict floor `3.914898`. The recorded result is the official verifier's default hash-seeded run.

## Provenance

- Source: [`syed3000/vqcc-own-circuit-portfolio`, version 17](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio/versions/17)
- License: Apache-2.0; the upstream license and notice are retained in [`upstream/`](upstream/).
- Pinned source tree SHA-256: `61c2b9db025e13dac7192e436d6354a9892ffde0a719e1fb3a81734cfad9da83`
- Source `submission.npz` SHA-256: `07f81f5f31341785821c773483e7bbeb7b7b087512dd65dc8c38589285373dbf`
- Official verifier SHA-256: `0775be7a528922367caebe9e4d051d6199811f1aefeaa4b793eaaa4621b8ec9d`
- All 15 generated `.kmb` files matched the pinned `manifest.json` hashes. The kernel read zero public `.kmb`/`.kmx` inputs; an audit hook blocked such reads.
- Kernel internet access was disabled. Credentials were removed from the process environment before building.

The rebuild code is in [`kernel/`](kernel/). Hashes and verifier output are in [`receipts/`](receipts/); raw build and kernel logs are in [`kaggle_output/`](kaggle_output/).

## Archive status

This verifies the third member only. The complete source-owned archive has not yet been assembled, rescored, or submitted. See the [archive milestone](../../milestone/2026-11-23-source-owned-archive.md).
