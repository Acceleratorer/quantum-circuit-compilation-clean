---
id: 2026-11-22-exp053-mbu-screen
date: 2026-11-22
---

# exp-053 — measurement-based sample erasure screen

Private Kaggle kernel version 23 compiled and simulated the full-input
four-pivot ratio/history prefix on 32 arbitrary GF(2^12) cases. Labels and
branch history matched the reference, the 66 spectator words were preserved,
scratch was clean, and there were no phase flips.

The measured resources were `Q=902`, `T=4,700`, versus `Q=902`, `T=3,200`
for the unitary sample eraser. Measuring the sample after the forward ratio
workspace is live did not change peak width and added 1,500 Toffoli-like gates.
This closes the measurement-erasure variant; it is not an integrated decoder
or official verifier result.

Evidence: [evaluation receipt](../evals/2026-11-22-exp053-mbu-prefix-v23.json),
[captured kernel output](../experiments/exp-053/logs/kernel-v23-output.json),
[exp-053 notes](../experiments/exp-053/README.md), and
[private kernel version 23](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/23).

Next: remove the ratio-workspace peak in the forward prefix schedule.

The direct-output attempt in kernel version 25 failed the spectator-payload
check: payload word 4 changed in shots 1 through 8. It produced no resource
result and was dropped. See the
[failure receipt](../evals/2026-11-22-exp053-direct-output-v25.json).
