---
id: exp-047
title: Packed BM field-quadratic feedback screen
task: dqi
tests: experiments/exp-047/feedback_field_degree_screen.py (exhaustive GF(4)/GF(8) prefixes)
direction: D-004
status: negative_result
date: 2026-11-19
result: no degree-2 predictor in GF(4)/GF(8); adjusted FIA remains syndrome-dependent with no demonstrated resource advantage
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

### Worst-case count

The current leader-equivalent DQI target is `245.285e9`. At `R=1.1912605` and
an optimistic `Q=860` (847 packed-state bits plus 13 inversion scratch bits),
the Toffoli ceiling is about `278.4k`. A rough reversible BM count is `261,345`
Toffolis: two 105,840-Toffoli BM passes, two sets of 35 66-Toffoli inversions,
and the existing 45,045-Toffoli Chien scan. This leaves only about `17.1k`
Toffolis for branch controls and all other transition overhead. The estimate
is optimistic and does not prove the state transition exists.

### Verifier-weighted BM budget

The official verifier distribution (`m=4095`, `n=70`, `degree=12`, `r=2016`)
has `E[e]=31.046737` and `E[e²]=968.605921`. Applying the conventional BM
field-multiplication ledger `M(e)=2e²+e+1` gives `1,969.259` products per
pass on average, or `82,709` Toffolis at 42 per product. Counting two passes,
`e` inversions per pass at 66 Toffolis each, and the existing 45,045-Toffoli
scan gives an optimistic mean of `214,561` Toffolis before transition,
control, and other decoder overhead. This leaves about `45.4k` Toffolis under
the `Q=890` gate, or `63.8k` under the `Q=860` gate. The BM multiplication
formula is from [Fossorier (2015)](https://doi.org/10.1109/LCOMM.2015.2436379);
the weight moments are computed from the verifier's `optimal_dqi_weights`.
The verifier also samples uniform nonzero field amplitudes; this estimate
averages only over error weight and does not assume unit amplitudes.

This opens a conditional route worth implementing only if the packed-state
transition can be built within that remaining budget. The estimate is not a
circuit result: there is still no reversible local transition that computes
the next discrepancy from the packed state without retaining the syndrome
prefix.

Do not build a circuit unless the fitted feedback formula and the complete
forward, phase, and uncompute count fit `R × Q² × T <= 245.285e9`.

## Follow-up screen: adjusted FIA

The adjusted Fundamental Iterative Algorithm (FIA) does not remove the missing
feedback step. On the syndrome matrix its discrepancy is still
`δ = sum_i Λ_i S_(...)`, and its locator update is
`Λ_new = Λ - (δ/δ_old) Λ_old x^shift`. Thus it still needs the next syndrome
row to compute `δ`; the packed locator state alone does not determine the next
state. Heydtmann and Jensen describe FIA on the syndrome matrix as equivalent
to Berlekamp–Massey, so this representation does not establish a lower
field-product count than the BM ledger above.

The paper's statement that only three generations of variables are needed is
a classical storage observation. It gives no reversible liveness schedule,
peak-qubit count, or compute/phase/uncompute Toffoli count for this instance.
It also treats generating the evaluator polynomial alongside the locator,
which adds state and work. FIA therefore does not clear either resource gate
and is a no-go as a direct replacement for the packed-state transition. No
circuit or new experiment directory was created.

Source: A. E. Heydtmann and J. M. Jensen, “On the Equivalence of the
Berlekamp-Massey and the Euclidean Algorithm for Decoding,” §§2.3.3–2.3.4
([DTU-hosted paper](https://backend.orbit.dtu.dk/ws/portalfiles/portal/3024053/Decoding%20Algebraic%20Codes.pdf)).

## Status

- 2026-11-19: Exhaustive small-field screen complete; degree-2 route closed.
- 2026-11-19: Adjusted FIA screen complete; it retains the syndrome-dependent
  discrepancy and supplies no resource advantage over BM for this circuit.

## Run

```powershell
..\..\.venv\Scripts\python.exe experiments\exp-047\feedback_field_degree_screen.py
```
