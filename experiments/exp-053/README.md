---
id: exp-053
title: Pivot-normalized FMA recurrence screen
task: dqi
tests: exhaustive GF(8) four-sample inputs; 48 seeded GF(2^12) 70-symbol DQI samples
direction: D-004
status: normalized_recurrence_screened
date: 2026-11-20
result: one variable product per in-place pair update; branch history, row ranks, and normalized low row match the reference on screened domains
---

# Pivot-normalized FMA recurrence

## Question

Can normalizing the selected pivot row lower the variable-product count while
preserving the FMA branch sequence and the locator row?

## Result

For pivot `(a,b)=(d_j,g_j)` and `delta=x_i+x_j`, the original matrices are

```text
no-swap: [[b, a], [0, delta]]    where b != 0
swap:    [[b, a], [delta, 0]]    where a != 0
```

Scale only the first row by the inverse of its selected nonzero pivot. With
`r=a/b` for no-swap and `r=b/a` for swap, the normalized matrices are

```text
no-swap: [[1, r], [0, delta]]
swap:    [[r, 1], [delta, 0]]
```

The rank is unchanged by a nonzero row scale. The pivot zero class is unchanged,
so this recurrence selects the same branches. Its data-pair updates can be
implemented in place:

```text
no-swap: d_i ^= r*g_i; g_i *= delta
swap:    g_i ^= r*d_i; d_i *= delta; swap(d_i, g_i)
```

Each pair update uses one GF(2^12) variable product and needs no clean output
field register. The ratio is computed once per pivot and reused across its
suffix. The screen exhaustively checked all 4,096 four-sample GF(8) vectors and
48 seeded valid GF(2^12), 70-symbol DQI samples. Branch histories, row ranks,
and the normalized low row matched the existing recurrence in every case.

The 70-symbol arithmetic count is 2,415 pair updates plus 70 pivot-ratio
products and 70 inversions. At 42T per product and 111T per computed-and-erased
inverse, the FMA arithmetic is 112,140T. Reusing the existing 71-product / 8-
inverse sampled reconstruction ledger, 45,045T scan, and 5,530T branch/rank
cell gives a projected subtotal of 166,585T, leaving 90,358T under the
256,943T screen gate.

## Limit

This count does not solve width. The direct sequential state holds 70 `d` words
and up to 69 variable `g` words, or 1,668 qubits before the ratio workspace;
the circuit limit is 890. The normalized recurrence is therefore a count lead,
not a candidate. It still needs a reversible compact-state schedule for the
4+66 split, including ratio liveness, branch/rank storage, and phase cleanup.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-053/normalized_fma.py'
```
