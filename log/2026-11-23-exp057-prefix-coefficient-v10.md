# 2026-11-23 — exp-057 prefix-to-coefficient gate

Private Kaggle kernel version 10 completed all current exp-057 component
screens. The new compact-prefix-to-coefficient cell passed 32 cases across
both pivot paths, including the zero-`a1` inactive branch. It reconstructed all
four coefficients, preserved the rank/pivot and 66 spectator words, left 40
scratch qubits clean, and produced no phase flips. Its resource count is
`Q=889`, `T=22,954`, one qubit below the 890-qubit gate.

The width reduction reuses the already-clean `temp` word as borrowed inverse
workspace and uses the remaining clean borrowed words for scaling. Against the
preceding local screen, this reduced the peak from `Q=893`, `T=23,188` to
`Q=889`, `T=22,954` without changing the checked outputs.

The same Kaggle run repeated the decoder round trip (`Q=885`, `T=7,483`),
precomputed tail action (`Q=873`, `T=84`), coefficient-derived tail action
(`Q=889`, `T=822`), and in-place matrix setup (`Q=889`, `T=558`); all reported
zero output errors and phase flips. These remain separate cells and do not
measure an integrated 66-symbol schedule.

Receipt: [exp-057 prefix-to-coefficient v10](../evals/2026-11-23-exp057-prefix-coefficient-v10.json).
The run completed at [private Kaggle kernel version 10](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/10).

**Decision:** keep the competition submission blocked until the integrated
4+66 schedule passes the official verifier. No competition submission was
made.
