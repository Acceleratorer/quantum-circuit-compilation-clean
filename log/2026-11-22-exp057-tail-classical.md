# 2026-11-22 — exp-057 full tail algebra

Reconstructed the canonical complementary row from the four-word prefix
state, then checked its matrix and inverse action across the tail schedule.

All 2,016 supported GF(8) prefixes passed at the four distinct tail points
4–7: 8,064 matrix/tag reconstructions and pair round-trips, including both
pivot branches. Thirty-two seeded verifier-form GF(2^12) cases (16 each at
error weights 31 and 35) passed at every tail point 4–69: 2,112 checks with
zero reconstruction or round-trip errors. All sampled GF(2^12) cases used the
`a0` pivot.

This is classical algebra evidence, not a compiled circuit or a verifier pass.
The next gate remains the compact-prefix-to-matrix circuit, then measured reuse
across all 66 symbols.

Receipt: [classical tail evaluation](../evals/2026-11-22-exp057-tail-transition-classical.json).
Code and tests: [exp-057 decoder](../experiments/exp-057/streaming_fixed_shape_decoder.py),
[unit test](../tests/test_exp057_tail_transition.py).
