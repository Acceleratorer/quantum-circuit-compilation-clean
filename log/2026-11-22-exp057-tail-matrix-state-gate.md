# 2026-11-22 — exp-057 in-place tail-matrix setup

Private Kaggle kernel version 7 passed the in-place coefficient-to-matrix
setup at point 4 across 64 cases. The four coefficient words became the
evaluated matrix `(A,B,C,D)`; `b1` remained as the reversible discriminator.
The cell measured `Q=889`, `T=558`, preserved the other 66 payload words and
rank/pivot, left 28 scratch qubits clean, and had zero matrix errors, tag
errors, or phase flips. A local 64-case screen at point 69 passed with the
same resource counts.

This is a one-time setup from four supplied coefficients. It does not accept
the compact prefix state or measure repeated use across the 66-symbol tail.
Next, connect this setup to the compact prefix state and measure a reused
matrix in the actual tail schedule before invoking the official verifier.

Receipt: [exp-057 tail-matrix state gate](../evals/2026-11-22-exp057-tail-matrix-state-gate.json).
Raw Kaggle output is retained in ignored local staging.
