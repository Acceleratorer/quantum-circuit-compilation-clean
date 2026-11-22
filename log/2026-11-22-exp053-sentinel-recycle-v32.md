# Exp-053 sentinel/recycle screen — 2026-11-22T10:39:50Z

Private Kaggle kernel v32 combined the existing sentinel-label branch eraser with the measurement-recycle prefix.

The four-pivot combination passed 32 cases with correct labels, clean scratch, and zero phase flips, but measured Q=916, T=6044; it is 26 qubits over the 890 limit.

The five-pivot combination matched its sentinel labels but failed cleanup and phase: Q=917, T=7512, 2 dirty scratch qubits, and 15 phase flips in 32 cases. Close this layout.

The five-pivot ratio/history baseline remains Q=891, T=4500, with correct labels/history, clean scratch, and zero phase flips; it is one qubit over the gate and does not erase branch history. The one-bit compact-state tag has not been compiled.

Receipt: [evals/2026-11-22-exp053-sentinel-recycle-v32.json](../evals/2026-11-22-exp053-sentinel-recycle-v32.json)
Output: [kernel-v32-output.json](../experiments/exp-053/logs/kernel-v32-output.json)
Kernel: [private version 32](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/32)
