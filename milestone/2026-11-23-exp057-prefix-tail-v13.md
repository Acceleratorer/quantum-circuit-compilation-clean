# exp-057 prefix-to-tail composition

**Status:** The 4+1 component gate passed; the full 4+66 schedule remains open.

Private Kaggle kernel version 13 composes compact-prefix decoding with one
coefficient-derived tail action at `Q=889`, `T=10,084`. Across 32 cases, both
prefix pivots were covered; coefficients and tail outputs matched, 66 tail
words and rank/pivot were preserved, 16 scratch qubits were clean, and phase
flips were zero.

The next gate is to reuse the tail workspace across all 66 symbols, then
measure the complete schedule and run the official verifier. No competition
submission was made.

Evidence: [evaluation](../evals/2026-11-23-exp057-prefix-tail-v13.json),
[run log](../log/2026-11-23-exp057-prefix-tail-v13.md).
