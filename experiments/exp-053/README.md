---
id: exp-053
title: Pivot-normalized FMA recurrence screen
task: dqi
tests: exhaustive GF(8) four-sample inputs; 48 seeded GF(2^12) 70-symbol DQI samples; 32 compiled pair-cell cases
direction: D-004
status: normalized_pair_cell_compiled
date: 2026-11-20
result: recurrence screens match the reference; two-branch pair cell compiles at Q=888, T=312 with clean scratch and phase
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
so this recurrence selects the same branches. Canonicalizing each pair with a
branch-controlled swap gives one shared in-place update:

```text
before:   if swap, swap(d_i, g_i)
update:   d_i ^= r*g_i; g_i *= delta
after:    if swap, swap(d_i, g_i)
```

The shared update uses one GF(2^12) product and no clean output field register;
the two controlled swaps cost another 24T per pair. The ratio needs one product
to compute and one to clear. A compiled one-pair cell uses the existing
in-place GF(2^12) inverse (66T forward, 72T restore), preserves 16 rank bits
and the branch bit, and peaks at Q=888. Kickmix simulated 32 valid pivot cases
across both branches; the pivot was restored, all 31 scratch qubits were
clean, and there were no phase flips.

The classical screen exhaustively checked all 4,096 four-sample GF(8) vectors
and 48 seeded valid GF(2^12), 70-symbol DQI samples. Branch histories, row
ranks, and the normalized low row matched the existing recurrence in every
case.

The corrected 70-symbol FMA count is 2,415 pair products, 140 ratio products,
70 in-place inversions at 138T each, 57,960T for pair-orientation swaps, and
1,680T for pivot-orientation swaps: 176,610T. Adding the existing sampled
reconstruction ledger, 45,045T scan, and 5,530T branch/rank cell projects
231,055T, leaving 25,888T under the 256,943T screen gate. The prior
166,585T estimate omitted ratio cleanup and controlled swaps.

## Limit

The compiled one-pair cell does not solve width for the full recurrence. The
direct sequential state holds 70 `d` words and up to 69 variable `g` words, or
1,668 qubits before ratio workspace. A complete 4+66 schedule must generate
and consume each pair from the compact 840-qubit payload, keep ratio and rank
state live within Q=890, and account for all cleanup and phase work. The 25,888T
margin is only a projection; no full circuit or submission exists.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-053/normalized_fma.py'
```
