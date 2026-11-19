---
id: exp-052
title: FMA sample-update reversibility screen
task: dqi
tests: exhaustive GF(4) tuples, exhaustive valid GF(8) errors, sampled GF(2^12) DQI errors
direction: D-004
status: local_transition_feasibility
date: 2026-11-20
result: every tested pivot was nonzero and every checked sample update inverted exactly; branch-history cleanup and full resource counts remain open
---

# FMA sample-update reversibility screen

## Question

Can an FMA step update each remaining `(d,g)` pair in place without keeping an
extra copy of that pair?

## Result

At pivot `(a,b)=(d_j,g_j)` and distinct points `x_i != x_j`, the update is

```text
d_i' = b*d_i + a*g_i
g_i' = (x_i + x_j) * (d_i if swap else g_i)
```

Its matrix determinant is `(x_i+x_j)*a` on the swap branch and
`(x_i+x_j)*b` otherwise. The FMA branch rule chooses swap when `b=0` or when
`a!=0` and the rank condition holds. If the pivot is nonzero, the selected
determinant is therefore nonzero and the pair update has an exact inverse.

The pre-step basis determinant is a nonzero scalar multiple of the product of
the already-processed point factors. At the next distinct point that basis is
invertible; applied to a pristine sample `(d_i,1)`, it cannot produce a zero
pivot. Thus the local update is nonsingular throughout the pristine-input
FMA recurrence.

The checker found no zero pivots or singular data-pair updates across:

- all 256 pristine four-symbol inputs over GF(4);
- all 97,119 valid RS error patterns through weight four over GF(8);
- 192 seeded GF(2^12), 70-point DQI inputs, 64 each at error weights 1, 31,
  and 35.

It also checked the explicit inverse on representative pairs: 1,280 checks for
GF(4), 1,262,547 for GF(8), and 26,304 for GF(2^12); all passed. Exact counts are in
[`results.json`](results.json), and the checker is
[`fma_pivot_reversibility.py`](fma_pivot_reversibility.py).

## Limits

This removes the need to keep an old copy of an individual right-side pair if
the pivot and branch are available. It does **not** remove the need to preserve
or recompute branch decisions, implement the polynomial-basis state, or prove
that the full 70-symbol circuit fits `Q<=890` and `T<=256,943`. No circuit was
built or submitted.

The next gate is a reversible branch/rank schedule for the 4+66 path under the
50-qubit scratch limit, with a complete Toffoli and phase ledger.

## Run

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_pivot_reversibility.py'
```
