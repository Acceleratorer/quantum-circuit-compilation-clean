# 2026-11-25 — exp-057 Forney polynomial inverse screen

## Result

An ordinary polynomial extended-Euclid implementation computed
`A = omega / sigma_prime mod sigma` correctly on 64 verifier-shaped cases
(32 each at error weights 31 and 35), including all 2,112 error-root residue
checks.

The optimistic arithmetic count averaged 4,355 field products and 19 field
inversions: **184,164T mean, 206,364T maximum** at 42T per product and 66T per
inverse. The current replacement allowance is 36,183.74T, so this direct route
is over budget by 5.09x on average before reversible branches, workspace, or
cleanup.

## Decision

Do not build this ordinary EEA route as a circuit. This closes only the direct
polynomial-inverse implementation; a faster or integrated transform remains a
separate, unproven possibility. Receipt:
[`2026-11-25-exp057-forney-polynomial-inverse.json`](../evals/2026-11-25-exp057-forney-polynomial-inverse.json).

Reproduce with:

```powershell
..\..\.venv\Scripts\python.exe -B experiments\exp-057\forney_polynomial_inverse_screen.py
```
