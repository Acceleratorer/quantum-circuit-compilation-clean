# 2026-11-23 — exp-057 private 66-symbol matrix stream, v14

Private Kaggle kernel version 14 compiled the point-to-point matrix recurrence
and applied all 66 tail actions. It XOR-accumulated both row outputs into one
12-bit checksum so the action workspace was reused for the full stream.

Across 32 cases covering both prefix pivots (`a0`: 31, `a1`: 1), the checksum
matched direct polynomial evaluation. All 70 payload words and three stream
tags were preserved, the matrix recurrence was reversed back to point 4, and
there were no phase flips. The circuit measured `Q=888`, `T=5,544` (84T per
tail action and zero Toffolis for recurrence updates), two qubits under the
890-qubit gate.

This component starts from a supplied point-4 matrix and its `K`, `b1`, and
`a1` tags. The compact-prefix decoder, reversible matrix setup and cleanup,
per-symbol DQI output, and official verifier are not included. No competition
submission was made.

Receipt: [v14 evaluation](../evals/2026-11-23-exp057-matrix-stream-v14.json).
