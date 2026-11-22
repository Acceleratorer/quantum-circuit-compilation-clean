# Exp-053 five-pivot prefix — 2026-11-22T10:35:15Z

Private Kaggle kernel v31 compiled the measurement-recycle prefix for five arbitrary GF(2^12) samples. Across 32 simulated inputs, output labels and branch history matched the reference, all other payload words were preserved, scratch was clean, and there were zero phase flips.

The prefix measured Q=891, T=4500, with 41 clean scratch qubits. The four-pivot v30 baseline is Q=890, T=3032. The five-pivot prefix misses the Q=890 gate by one qubit and retains all five branch bits; it does not test the proposed tag eraser.

The score-equivalence mean-Toffoli gate is 215,175.987, but this prefix is not a candidate. The tag eraser, complete 4+66 schedule, and official verifier remain open.

Kernel: [private version 31](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/31)
Receipt: [evals/2026-11-22-exp053-five-pivot-prefix-v31.json](../evals/2026-11-22-exp053-five-pivot-prefix-v31.json)
Output: [kernel-v31-output.json](../experiments/exp-053/logs/kernel-v31-output.json)
Source SHA-256: ba0aeca158fa6b68090411cc9b666d70e0ff76d5b338dad8498315e79657df7e
