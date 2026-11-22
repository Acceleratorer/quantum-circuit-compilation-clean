# 2026-11-23 — exp-057 compact-prefix coefficient gate

## Result

The compact-prefix-to-coefficient reversible cell passed its 890-qubit width
gate in private Kaggle kernel version 10: `Q=889`, `T=22,954`. It passed 32
cases over both pivot paths, preserved 66 arbitrary spectator words and the
rank/pivot, left 40 scratch qubits clean, and had zero coefficient errors and
phase flips.

The same private run repeated the existing decoder and three tail component
screens successfully. The receipt and detailed run notes are in
[`evals/2026-11-23-exp057-prefix-coefficient-v10.json`](../evals/2026-11-23-exp057-prefix-coefficient-v10.json)
and [`log/2026-11-23-exp057-prefix-coefficient-v10.md`](../log/2026-11-23-exp057-prefix-coefficient-v10.md).

## Boundary and next gate

These are component screens. Compact prefix decoding, matrix setup, and the
tail action have not yet been combined into a measured 4+66 schedule. Run that
integrated circuit through the official verifier before considering a
competition submission. No competition submission has been made.
