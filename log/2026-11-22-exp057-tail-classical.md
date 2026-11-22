# 2026-11-22 — exp-057 one-symbol tail algebra

Reconstructed the canonical complementary row from the four-word prefix
state, applied the resulting 2x2 polynomial matrix at point 4, and verified
the determinant, four-point annihilation, and inverse action.

The classical gate passes all 2,016 supported GF(8) prefixes and 32 seeded
verifier-form GF(2^12) cases (16 each at error weights 31 and 35). The GF(2^12)
cases all took the `a0` pivot; exhaustive GF(8) includes both pivots.

This is not a compiled circuit or a 66-symbol schedule. The next gate is a
single-symbol Kickmix implementation with `Q <= 890`, a measured Toffoli count,
clean scratch, zero phase errors, and arbitrary spectator preservation.

Receipt: [classical tail evaluation](../evals/2026-11-22-exp057-tail-transition-classical.json).
Code and tests: [exp-057 decoder](../experiments/exp-057/streaming_fixed_shape_decoder.py),
[unit test](../tests/test_exp057_tail_transition.py).
