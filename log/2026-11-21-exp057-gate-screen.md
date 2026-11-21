# 2026-11-21 — exp-057 gate screen

The coherent pivot-control implementation for the four-word prefix-state cell
passed the source-owned gate screen on Kaggle kernel version 2. All 32 seeded
GF(2^12) cases round-tripped, both pivot branches were covered, 60 scratch
qubits were clean, and the circuit reported zero phase flips.

It compiled to `Q=909`, `T=7,125`. The 909-qubit cell exceeds the 890-qubit
gate by 19. Since this is a prefix-state cell rather than the complete 4+66
schedule, its Toffoli count is not a schedule-level score estimate. Close this
layout; no competition submission was made.

Run receipt: [evaluation](../evals/2026-11-21-exp057-gate-screen.json). Private
kernel: [version 2](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state).
