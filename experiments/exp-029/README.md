---
id: exp-029
title: Kirderf 27.11056 chemistry portfolio
task: portfolio
tests: [C-032]
direction: D-011
status: verified_ready_for_submit
date: 2026-11-13
result: chemistry PASS; local portfolio GM 27.1105624616; submission held for quota reset
---

# Kirderf 27.11056 portfolio

This candidate keeps the verified v30 DQI and invsqrt members byte-for-byte and
uses the chemistry NPZ published by the Kaggle notebook
[`kirderf/vqcc-portfolio-2711-reproduced`](https://www.kaggle.com/code/kirderf/vqcc-portfolio-2711-reproduced).
The notebook labels the assembly `LB 27.11056`; the exact archive was downloaded
and rechecked locally.

- Source notebook: https://www.kaggle.com/code/kirderf/vqcc-portfolio-2711-reproduced
- Archive SHA-256: `dce2b52dcba789655ca3195f2b968e4ea511b76be3519f672203fc1032a79dba`
- Archive size: `49,144,713` bytes; 18 members; ZIP `testzip()` PASS
- DQI SHA-256: `821bf8d157c03c3e868a0099b0ab1438cfba664ab1bc6fec3210654099b672a3`
- Invsqrt SHA-256: `321aff83636214196daa9cbc9dcc9c5e12a155bcff8d9989e98b8cee40935177`
- Chemistry NPZ SHA-256: `f90d6c660bce3c6ce55143100ac9e71e0aa34c4911014934c4536ccc88c64679`
- Chemistry verifier: PASS, score `296010654.3285701`, Q `427`, 14,776 Toffoli-like gates, 78,080 verified shots
- Retained DQI verifier result: PASS, score `360209905486.0156`, Q `889`, 102,400 shots, zero value/phase errors
- Retained invsqrt verifier result: PASS, score `80162.73214111096`, Q `46`, 200,540,928 shots
- Local zero-failure GM: `27.1105624615787`
- Improvement over v30: `+0.0001403051876` GM; chemistry cost lower by `4,595.8759066`

This is a real but small improvement. It remains below the current public
leaderboard top (`29.90871`), so it must not be described as rank 1. No Kaggle
submission was attempted before the daily quota reset.
