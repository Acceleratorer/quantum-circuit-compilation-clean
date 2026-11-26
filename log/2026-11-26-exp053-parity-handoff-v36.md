# exp-053 parity-controlled handoff — kernel v36

**Decision: close the 4+1 continuation.**

Version 36 stores the rank bit recovered at the four-pivot handoff and replaces
the temporary branch ancilla with parity-controlled rank reflections and
CSWAPs. Across 32 GF(2^12) cases, output labels and retained branch history
matched the reference; payload was preserved, scratch was clean, and phase
flips were zero. The circuit compiled at `Q=891`, unchanged from v35, with
`T=4,576` (`+76T`). This remains one prefix gate and does not cover the other
65 pivots.

The live leader score read at `2026-11-26T06:06:32Z` was `34.50408`, versus
the source-owned best `33.08634`. At `Q=890`, the score-equivalent tie gate is
`285,041.64` mean T. The width failure is unchanged, so this layout is closed.

Evidence: [evaluation](../evals/2026-11-26-exp053-parity-handoff-v36.json),
[normalized kernel output](../experiments/exp-053/logs/kernel-v36-output.json),
and [private kernel v36](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/36).
No official verifier was run and no competition submission was made.
