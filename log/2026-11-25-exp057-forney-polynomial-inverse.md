# 2026-11-25 — exp-057 Forney polynomial inverse screen

## Result

An ordinary polynomial extended-Euclid implementation computed
`A = omega / sigma_prime mod sigma` correctly on 64 verifier-shaped cases
(32 each at error weights 31 and 35), including all 2,112 error-root residue
checks.

The first formulation materializes the polynomial inverse, then multiplies by
`omega`: 4,355 field products and 19 field inversions on average, or
**184,164T mean, 206,364T maximum**. A direct right-hand-side Euclid recurrence
avoids materializing the full inverse and lowers this to 4,129 products and 19
inversions: **174,672T mean, 195,612T maximum**. Both formulations passed all
2,112 residue checks. The 36,183.74T replacement allowance is still exceeded
by 4.83x on average before reversible branches, workspace, or cleanup.

## Decision

Do not build either ordinary EEA formulation as a circuit. This closes only
these direct polynomial-Euclid implementations; a faster or integrated
transform remains unproven. Receipt:
[`2026-11-25-exp057-forney-polynomial-inverse.json`](../evals/2026-11-25-exp057-forney-polynomial-inverse.json).

Reproduce with:

```powershell
..\..\.venv\Scripts\python.exe -B experiments\exp-057\forney_polynomial_inverse_screen.py
```
