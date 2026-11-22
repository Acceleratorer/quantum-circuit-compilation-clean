# 2026-11-22 — exp-057 tail-matrix state encoding

Exhaustively checked the 2,016 supported GF(8) coefficient states at tail
point 4. The four evaluated matrix entries identify only 444 distinct keys,
with 1,572 collisions and a largest fiber of 7 states. Matrix entries alone
cannot replace the four-word coefficient state reversibly.

Keeping the full field element `b1` as a discriminator removed every
collision and reconstructed all four coefficients in the screen. The recovery
uses `b0 = B(x) + x*b1`, `a1 = (C(x)/D(x))*b1 + B(x)/b1`, and
`a0 = A(x) + x*a1 + x^2`. Here `(A,B;C,D)` are the evaluated matrix entries.
The GF(8) minimum is 3 bits, while the proposed discriminator is the complete
field word; do not treat the GF(8) bit count as a GF(2^12) result.

The same recovery had zero errors on 32 seeded GF(2^12) verifier-form samples
(16 each at error weights 31 and 35). This is a sample check, not an exhaustive
GF(2^12) injectivity count.

This is classical evidence only. The reversible in-place map, gate count,
scratch cleanup during setup, 66-symbol reuse, and official verifier remain
open. Next, encode and preserve `b1` while generating the matrix from
the compact prefix state, then reverse the setup after the tail schedule.

Receipt: [exp-057 tail-matrix encoding](../evals/2026-11-22-exp057-tail-matrix-encoding.json).
The result is included in the focused tail-transition test.
