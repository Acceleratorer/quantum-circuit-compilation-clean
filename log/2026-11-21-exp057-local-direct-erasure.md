# 2026-11-21 — exp-057 local direct-erasure screen

The current source edit erases the inverse scratch after a controlled swap by
recomputing from the swapped value, using inversion's involution property. The
32-case local Kickmix screen covered both pivot paths, round-tripped all four
words, restored the rank tag, left 56 scratch qubits clean, and reported zero
phase flips.

It measured `Q=905`, `T=6,993`: an improvement over the earlier private Kaggle
version 2 (`Q=909`, `T=7,125`), but still 15 qubits over the 890-qubit gate.
The current edit has not been run on Kaggle and was not submitted.

Run receipt: [local evaluation](../evals/2026-11-21-exp057-local-direct-erasure.json).
