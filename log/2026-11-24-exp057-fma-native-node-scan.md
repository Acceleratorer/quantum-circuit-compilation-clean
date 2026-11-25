# 2026-11-24 — exp-057 native-node scan

## Hypothesis

The FMA numerator is already the evaluator for the 0–69 sample-node polynomial. Scanning it against that same polynomial might avoid the expensive CONVERT bridge.

## Result

The reversible scan ran weights 31 and 35 and observed one phase error.
Expected phase: `[0, 0]`; observed phase: `[1, 0]`. It used Q=851, T=43,593,
restored all input registers, and left 11 scratch qubits clean.

The circuit excluded all 69 field positions that are roots of the sample-node
polynomial, in addition to the first 70 scan positions. It does not test the
special sample-node error branch or the full DQI verifier.

## Decision

Reject the direct FMA-native-node scan shortcut. Continue from the existing FMA-to-DQI phase path.
