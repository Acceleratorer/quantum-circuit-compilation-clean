# 2026-11-21 — branch-history erasure screen

Kernel `accelra/exp053-inplace-ratio-history` version 22 compiled the
source-owned four-pivot sentinel-label circuit. On 32 arbitrary GF(2^12)
four-sample inputs, labels and final rank matched; all four branch registers
were erased; scratch was clean; and phase flips were zero.

The circuit measured `Q=928`, `T=6,212`, with 84 clean scratch qubits. It removes
four persistent branch bits but peaks 9 qubits wider and 310T higher than the
version 21 sentinel layout. The 890-qubit gate is missed by 38. Close this
all-fields-live circuit layout as a candidate; the 4+66 FMA schedule remains
open only if it reuses payload storage enough to prove `Q <= 890`.

Raw output remains in ignored Kaggle staging. The source hash and compact run
receipt are recorded in [`results.json`](../experiments/exp-053/results.json).
