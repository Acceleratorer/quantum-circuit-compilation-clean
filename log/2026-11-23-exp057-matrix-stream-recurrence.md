# 2026-11-23 — exp-057 streaming matrix recurrence

The evaluated Bezout matrix can advance from tail point `x` to `y` using a
small state `(A,B,C,D,K,b1,a1)`, where `K=D/b1` and `P` is the four-point node
polynomial:

```text
delta = x + y
scale = P(y) / P(x)
A' = A + delta*a1 + delta^2
B' = B + delta*b1
C' = scale * (C + delta*K)
D' = scale * D
K' = scale * K
```

All variable operands enter only through XOR. Every multiplication is by a
point-dependent constant, so the transition is CNOT-only after the initial
matrix and tags have been built. This removes per-point matrix regeneration
from the classical schedule; the quantum circuit and its live workspace are
still unmeasured.

The check matched direct polynomial evaluation on all 8,064 supported GF(8)
tail cases and 2,112 seeded GF(2^12) verifier-form cases, with zero recurrence
errors. Both existing tail transition tests pass. This does not compile the
4+66 circuit, verify output cleanup or phase, or pass the official verifier.

Receipt: [matrix recurrence evaluation](../evals/2026-11-23-exp057-matrix-stream-recurrence.json).
