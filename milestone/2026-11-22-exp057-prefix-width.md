# 2026-11-22 — exp-057 prefix-cell width gate

## Gate result

The source-owned four-word prefix-state cell passes `Q <= 890`: local and
private Kaggle version 4 both measured `Q=885`, `T=7,483`. The private screen
covered 32 states, both pivot paths, and an `a1=0` inactive-branch case. It
reported zero round-trip errors, restored the rank tag, preserved 66 arbitrary
spectator words, left 36 scratch qubits clean, and had no phase flips.

Evidence: [evaluation receipt](../evals/2026-11-22-exp057-private-gate-screen.json)
and [experiment notes](../experiments/exp-057/README.md).

## Boundary

This gate covers only the four-word cell. It does not decode the 66 spectator
words, prove the integrated 4+66 schedule, or pass the official DQI verifier.
The top-leaderboard goal remains open; no competition submission was made.

## Next gate

Integrate the current cell into the full 4+66 schedule, prove all 70 syndrome
inputs and ancillas satisfy the official verifier, and measure the complete
DQI cost against the existing `Q <= 890` and `T <= 221,529` target before
preparing any submission.
