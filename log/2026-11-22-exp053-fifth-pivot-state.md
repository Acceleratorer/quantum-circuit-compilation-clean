# Exp-053 fifth-pivot state screen — 2026-11-22T10:01:24Z

## Result

Exhaustive enumeration of all 32,768 five-word GF(8) inputs found 46 collision groups in the compact key (five ratios, normalized low row, and final ranks), with at most 2 inputs per key. The single Boolean tag branch[1] AND NOT branch[4] made all 32,768 labels unique; no single branch bit or fixed parity did so.

A seeded GF(2^12) check found no collisions in 32 valid weight-31 and 32 valid weight-35 DQI samples. This is sample compatibility evidence, not a full-field proof.

## Gate

This is an information screen only. There is no reversible tag/eraser circuit, resource measurement, integrated 4+66 schedule, or official-verifier run. Keep it as one lead; promote it only after those gates pass. The current score-equivalence ceiling is Q=890, mean T<=215,175.99 at R=1.1912605.

Reproduce with the Python command recorded in the receipt.

Receipt: [evals/2026-11-22-exp053-fifth-pivot-state.json](../evals/2026-11-22-exp053-fifth-pivot-state.json). Source SHA-256: 75402093db3b1adcbed2a247bd45b25a02de2934a52962c7af2d62818d003c65.
