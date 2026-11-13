id: exp-024
title: Rebuild the DQI decoder with cutoff 17
task: dqi
tests: [C-027]
direction: D-006
status: submitted_pending
date: 2026-11-13
result: official DQI verifier PASS; cutoff-17 lowers the verified DQI score and raises the local portfolio GM estimate
---

# Syed v12 DQI cutoff 17

This experiment reproduces the public `ozertuu/27-083-vqcc-dqi-cutoff-17`
change against the pinned Syed v12 source. Only `dqi.kmb` changes; the 46Q
invsqrt circuit and refined chemistry files remain byte-identical to exp-023.

- Source kernel: https://www.kaggle.com/code/ozertuu/27-083-vqcc-dqi-cutoff-17
- Archive: `artifacts/submission_syed_v12_cutoff17.zip` (kept outside Git)
- Archive SHA-256: `af3f851f98a7e9a2d35049b80408981ed57f06320bb511202e80bf368b9dcc92`
- DQI SHA-256: `cc0d7d25db72e90130c7c739f874a7ac611751791ee6e6c765d4d881c01b7a52`
- DQI build: 889 qubits, 840 allocated qubits, 383,771 static Toffoli-like ops

The official verifier passed all `102400` shots with zero value errors and zero
phase errors. Verified DQI score is `360535516958.67847`, down from
`360733280431.94055`. The local zero-failure GM estimate is `27.0833379048`.

- Submission ref: Kaggle `58291268`
- Submission state: pending at commit time; update this file after Kaggle returns the public score.
