# exp-057 v15: integrated 66-symbol screen

## Gate

Compose compact-prefix decoding, reversible point-4 matrix setup, and all 66
tail actions under the 890-qubit limit, with both prefix pivots covered.

## Result

Passed in private Kaggle kernel v15: 32 cases, `Q=889`, `T=19,004`, zero
matrix/tag/checksum errors, 66 preserved tail words, 12 clean scratch qubits,
and zero phase flips. The full receipt is
[`evals/2026-11-23-exp057-prefix-matrix-stream-v15.json`](../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json).

## Remaining gate

This cell produces a checksum and uses the rank register as workspace. It does
not generate the DQI phase/output, restore the original prefix/matrix state,
or pass the official verifier. No competition submission was made. The next
milestone is the complete reversible DQI candidate and its official verifier
receipt.
