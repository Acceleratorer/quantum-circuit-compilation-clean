# 2026-11-22 — exp-057 prefix-cell width gate

## Gate result

The source-owned four-word prefix-state cell passes `Q <= 890`: local and
private Kaggle version 4 both measured `Q=885`, `T=7,483`. The private screen
covered 32 states, both pivot paths, and an `a1=0` inactive-branch case. It
reported zero round-trip errors, restored the rank tag, preserved 66 arbitrary
spectator words, left 36 scratch qubits clean, and had no phase flips.

Evidence: [evaluation receipt](../evals/2026-11-22-exp057-private-gate-screen.json)
and [experiment notes](../experiments/exp-057/README.md).

## Boundary

This gate covers only the four-word cell. It does not decode the 66 spectator
words, prove the integrated 4+66 schedule, or pass the official DQI verifier.
The top-leaderboard goal remains open; no competition submission was made.

## One-symbol tail algebra gate

The four-word prefix state now has a classical one-symbol continuation screen.
The canonical complementary row reconstructs the four-point FMA basis; its
matrix annihilates the four prefix samples, has determinant equal to the
four-point node polynomial, and maps the next pair invertibly.

The screen passes all 2,016 supported GF(8) prefixes and 32 seeded GF(2^12)
verifier-form prefixes at error weights 31 and 35. This validates only the
classical transition at point 4. It does not compile a Kickmix tail cell or
cover the remaining 65 symbols. See the
[evaluation receipt](../evals/2026-11-22-exp057-tail-transition-classical.json),
[test](../tests/test_exp057_tail_transition.py), and
[experiment notes](../experiments/exp-057/README.md).

## Next gate

The one-symbol matrix action has since passed as a reversible Kickmix cell
when its four matrix entries are precomputed: private version 5 measured
`Q=873`, `T=84`, 64/64 correct outputs, clean scratch, preserved payload/rank/
pivot, and zero phase flips. See the
[matrix-action receipt](../evals/2026-11-22-exp057-tail-matrix-gate.json).

The follow-up cell derives and applies the action from four supplied
polynomial coefficients. Private version 6 measured `Q=889`, `T=822` across
64 cases at point 4, with clean scratch, preserved payload/rank/pivot, and no
output or phase errors. It still does not generate coefficients from the
compact prefix state or amortize setup across symbols. See the
[coefficient-derived action receipt](../evals/2026-11-22-exp057-tail-bezout-action.json).

An exhaustive GF(8) screen found that the four evaluated matrix entries alone
collapse 2,016 supported coefficient states to 444 keys. Keeping `b1` as a
field-word discriminator restores all 2,016 states, and the same recovery had
zero errors on 32 seeded GF(2^12) verifier-form samples. See the
[tail-matrix encoding receipt](../evals/2026-11-22-exp057-tail-matrix-encoding.json).

Next, connect the compact prefix state to the `b1`-tagged setup, then reverse
that setup after reuse across an accounted 66-symbol schedule. Measure
`Q <= 890`, the full Toffoli count, clean workspace, zero phase errors, and a
pass from the official DQI verifier before any competition submission.

The coefficient-fed in-place setup now passes separately: private version 7
measured `Q=889`, `T=558` on 64 point-4 cases, with the `b1` tag and all 66
spectator words preserved, clean scratch, and zero phase errors. A local
64-case point-69 screen matched. The remaining gate is connecting this setup
to the compact prefix state and accounting for reuse across the schedule; see
the [matrix-state receipt](../evals/2026-11-22-exp057-tail-matrix-state-gate.json).

For branch-history compression, ratios, ranks, retained bits `b0/b4`, and the
one-bit tag still leave 1,920 ambiguous keys in the exhaustive five-word GF(8)
screen. The block eraser must include the compact-state low row or use a
different reversible state; see the
[screen receipt](../evals/2026-11-22-exp053-fifth-pivot-ratio-tag-screen.json).
