---
id: exp-047
title: Packed BM field-quadratic feedback screen
task: dqi
tests: experiments/exp-047/feedback_field_degree_screen.py (exhaustive GF(4)/GF(8) prefixes)
direction: D-004
status: negative_result
date: 2026-11-19
result: no degree-2 field predictor exists by prefix length 2 in GF(4) or GF(8)
---

# Packed BM field-quadratic feedback screen

## Question

Can the next Berlekamp–Massey feedback value be computed from the packed state
without the old syndrome symbols, using a sparse quadratic formula over the
field? This is the missing step for a low-space BM decoder: the direct Boolean
degree-4 transition failed in `exp-046`, while keeping the syndrome history
would exceed the DQI space budget.

## Hypothesis

The predictor `sum(C[i] * S[n-i])` may be a low-degree function of the packed
state fields `C`, `B`, `L`, `shift`, and `last_discrepancy`, even though its
Boolean representation is not low-degree. A field-quadratic expression would
be a plausible route to a reversible GF(2^12) transition.

## Prediction

I predict the predictor will fail to fit a degree-2 field polynomial by the
exhaustive GF(8), length-5 screen. If it fits, the number of nonzero monomials
must still be low enough to fit the length-70 multiplication budget below.

## Method

Enumerate sequences for GF(4) through length 3 and GF(8) through length 5.
For each prefix, compute the exact BM state and its next feedback value from
the original sequence. Incrementally fit a field polynomial of degree at most
2 over the padded coefficient arrays and scalar controls. Stop a length at
the first inconsistent row: one contradiction disproves a formula over the
full domain. Check that equal packed states never map to different feedback
values. This is a small-field feasibility screen, not a GF(2^12) circuit proof.

## Results

Length 1 fits in both fields. At length 2, the GF(4) feature span is already
inconsistent after 11 of 16 sequences, and the GF(8) span after 19 of 64. No
packed-state collisions appear in the checked rows. Longer lengths also fail
before the enumeration completes. The pre-registered prediction held, with a
counterexample much earlier than expected; see `results.json`.

## Conclusion

No-go for a degree-2 field-polynomial predictor of the packed BM feedback.
This closes the tested low-degree factored route; it does not rule out higher
degree formulas or a different decoder representation. Do not build a circuit
from this formulation.

## Resource gate

The current leader-equivalent DQI target is `245.285e9`. At `R=1.1912605` and
an optimistic `Q=860` (847 packed-state bits plus 13 inversion scratch bits),
the Toffoli ceiling is about `278.4k`. A rough reversible BM count is `261,345`
Toffolis: two 105,840-Toffoli BM passes, two sets of 35 66-Toffoli inversions,
and the existing 45,045-Toffoli Chien scan. This leaves only about `17.1k`
Toffolis for branch controls and all other transition overhead. The estimate
is optimistic and does not prove the state transition exists.

Do not build a circuit unless the fitted feedback formula and the complete
forward, phase, and uncompute count fit `R × Q² × T <= 245.285e9`.

## Status

- 2026-11-19: Exhaustive small-field screen complete; degree-2 route closed.

## Run

```powershell
..\..\.venv\Scripts\python.exe experiments\exp-047\feedback_field_degree_screen.py
```
