# Exp-053 compact branch history — 2026-11-22

Kernel v33 compiled the five-pivot compact-history transform. Across 32 arbitrary GF(2^12) inputs, labels and branch history matched the reference, the other payload stayed unchanged, 43 scratch qubits were clean, and there were no phase flips. The exhaustive 32-history identity check passed; branch pivots 2 and 3 were erased while 0, 1, and 4 remained.

The circuit measured `Q=891`, `T=4,500`, identical to v31. Compaction happens after the prefix peak, so it does not lower the resource maximum and still misses the `Q=890` gate by one qubit. Close this as a scoring candidate. Keep the relation only if the complete schedule can reuse those wires before its peak.

The Kaggle run's overall JSON says `FAIL` because the same script also reruns the previously rejected v32 sentinel variants. The compact-history result itself passes its correctness, scratch, and phase checks, with the independent resource gate failing.

Reproduction: `kaggle kernels push -p kaggle/staging/exp053-compact-history-v33`.

Receipt: [evals/2026-11-22-exp053-compact-history-v33.json](../evals/2026-11-22-exp053-compact-history-v33.json)

Normalized output: [experiments/exp-053/logs/kernel-v33-output.json](../experiments/exp-053/logs/kernel-v33-output.json)

Private run: [Kaggle kernel version 33](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/33)
