# 2026-11-23 — exp-057 66-symbol matrix stream

**Status:** The precomputed-state 4+66 checksum gate passed; prefix-to-matrix
setup and the official DQI verifier remain open.

Private Kaggle kernel version 14 streamed all 66 tail actions at `Q=888`,
`T=5,544`. Across 32 cases, both compact-prefix pivots were represented; the
checksum matched direct evaluation, all payload and stream-tag inputs were
preserved, and phase flips were zero. The recurrence contributes zero
Toffolis per point because it consists of fixed linear field maps.

The matrix and its three recurrence tags were supplied as inputs. This is not
the integrated 4+66 DQI decoder and does not produce the competition's DQI
output. The next gate is a source-owned reversible prefix-to-matrix setup and
cleanup composed with this stream, still under `Q <= 890`, then the official
verifier.

Evidence: [v14 evaluation](../evals/2026-11-23-exp057-matrix-stream-v14.json),
[run log](../log/2026-11-23-exp057-matrix-stream-v14.md), and
[experiment record](../experiments/exp-057/README.md).
