# Exp-053 ratio/rank/tag erasure screen — 2026-11-22

The exhaustive five-word GF(8) pass checked all 32,768 sample vectors. It
grouped states by five ratios, final ranks, retained branch bits `b0` and `b4`,
and the tag `b1 AND NOT b4`.

The key has 30,848 groups; 1,920 leave `b1` ambiguous, with maximum fiber 2.
So the one-bit tag does not erase `b1` from ratios, ranks, and the two retained
branch bits alone. This exact small-field screen points the reversible eraser
at the compact-state low row (or a different state encoding).

This gives no GF(2^12) bound, gate count, full 4+66 schedule, or verifier
result. The source screen and evaluation receipt are
[fifth_pivot_state.py](../experiments/exp-053/fifth_pivot_state.py) and
[2026-11-22-exp053-fifth-pivot-ratio-tag-screen.json](../evals/2026-11-22-exp053-fifth-pivot-ratio-tag-screen.json).

Decision: do not implement an eraser from ratios/ranks/tag alone. The next
gate-level attempt must include the compact-state low row and stay within the
current DQI resource margin.
