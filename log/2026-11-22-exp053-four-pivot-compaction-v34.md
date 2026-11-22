# Exp-053 four-pivot handoff compaction — 2026-11-22

Kernel v34 compiles `b1 = b3 XOR rank1[1]` after the four-pivot block. The identity was checked over all 16 branch histories. On 32 arbitrary GF(2^12) inputs, labels and the retained branch bits matched, the other payload stayed unchanged, 43 scratch qubits were clean, and phase flips were zero.

The compact handoff retains branch pivots 0, 2, and 3 and frees pivot 1. The prefix stays `Q=890`, `T=3,032`, but has one more clean scratch qubit than the explicit-history baseline (43 vs. 42). This is useful capacity at the 4+66 boundary; the remaining 66-point tail has not been integrated or measured.

The overall script still reports `FAIL` because it reruns the already-rejected v32 sentinel variants. The v34 four-pivot compact result passes its own correctness, cleanup, and phase checks. No official verifier or competition submission was run.

Reproduction: `kaggle kernels push -p kaggle/staging/exp053-four-pivot-compaction-v34`.

Receipt: [evals/2026-11-22-exp053-four-pivot-compaction-v34.json](../evals/2026-11-22-exp053-four-pivot-compaction-v34.json)

Normalized output: [experiments/exp-053/logs/kernel-v34-output.json](../experiments/exp-053/logs/kernel-v34-output.json)

Private run: [Kaggle kernel version 34](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/34)
