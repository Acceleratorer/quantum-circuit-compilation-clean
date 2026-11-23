# 2026-11-23 — exp-061 7-bit chemistry score gate

The current 7-bit balanced-tree loader emits 18,255 static Toffolis per pass
(1,217 × 15). Its builder's 3,468 target gate failed before output generation.
A separately staged family passed the official DFTHC-SOS verifier: 78,016
shots, `Q=405`, `T=43,010`, score `817,512,097.94`. Receipt hash:
`c79a1249b28a1364f3664d6f94e428b957afdc43c79bf13ae552751bff983e6a`.

The retained best chemistry score is `294,642,305.56`. Holding the same
factorization metrics fixed, the family must use at most 4,500 static
Toffolis per pass to beat it. The corrected whole-task SelectSwap screen
projects `551.2M` at block size 2 and `475.4M` at block size 3; larger blocks
exceed the 128-qubit ANGLES cap. No submission was made. Keep this route closed
unless an actual XOR-loader construction clears the 4,500 gate and passes the
official verifier.

See [the experiment](../experiments/exp-061/README.md),
[the evaluation receipt](../evals/2026-11-23-exp061-qrom-score-gate.json), and
[the corrected source screen](../literature/papers/lit-select-swap-qrom-fit.md).
