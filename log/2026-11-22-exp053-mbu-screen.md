---
id: 2026-11-22-exp053-mbu-screen
date: 2026-11-22
---

# exp-053 — prefix width screens

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

The next screen targeted the forward ratio-workspace peak.

The direct-output attempt in kernel version 25 failed the spectator-payload
check: payload word 4 changed in shots 1 through 8. Kernel version 26 added
measurement erasure and reproduced the same failure. Neither produced a
resource result; the layout was dropped. See the
[failure receipt](../evals/2026-11-22-exp053-direct-output-v25.json).

## Follow-up — measurement recycling, kernel version 30

Version 30 fixed the clean-slot scratch regression seen in the
[version 29 output](../experiments/exp-053/logs/kernel-v29-output.json) and
tested the in-place measurement-recycle path. Across 32 arbitrary GF(2^12)
cases, the full-input prefix matched labels and branch history, preserved
spectator payload, left 42 scratch qubits clean, and produced zero phase flips.
It measured `Q=890`,
`T=3,032`, meeting the prefix width gate and saving 168 Toffoli-like gates
against the full-input unitary prefix.

Evidence: [version 30 output](../experiments/exp-053/logs/kernel-v30-output.json),
[evaluation receipt](../evals/2026-11-22-exp053-measurement-recycle-prefix-v30.json),
and [private kernel version 30](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/30).

Next: integrate this one prefix path with the remaining 66 symbols, then run
the full resource and official-verifier gates. No submission is ready.
