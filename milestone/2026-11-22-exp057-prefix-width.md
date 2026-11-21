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

Do not spend the next cycle on weight-0/1 shape patches: their combined default
sampler probability is about `3.25e-24`, or `3.32e-19` expected draws in
102,400 shots. First remove the 12-qubit overage from the general in-place
prefix in exp-053 by changing the forward ratio-workspace schedule; the
measurement-based eraser left peak width unchanged, and direct sample output
failed spectator preservation. Then integrate one prefix path with the
remaining 66 symbols and measure the full `Q <= 890`,
`T <= 221,529`, cleanup, phase, and official-verifier gates before preparing
any submission.
