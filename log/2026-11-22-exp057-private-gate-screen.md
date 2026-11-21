# 2026-11-22 — exp-057 private gate screen

The four-word prefix-state cell passed the local Kickmix screen and private
Kaggle kernel `accelra/exp057-streaming-prefix-state`, version 4. The 32 seeded
GF(2^12) cases covered both pivots and included one valid `a1=0` case with the
`a1` update branch inactive. The screen had zero round-trip errors, restored
the rank tag, preserved 66 arbitrary spectator words, left 36 scratch qubits
clean, and reported no phase flips.

Resources: `Q=885`, `T=7,483`; the cell is five qubits under the 890-qubit
gate. The private-kernel source bundle included the helper code, Apache
`LICENSE`, and `NOTICE`. Kaggle status was `COMPLETE`.

This is only the four-word cell. It does not decode the 66 spectator words and
does not establish the complete 4+66 schedule or pass the official verifier.
No competition submission was made. Keep the full-schedule gate open.

Run receipt: [evaluation](../evals/2026-11-22-exp057-private-gate-screen.json).
Private kernel: [version 4](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/4).
