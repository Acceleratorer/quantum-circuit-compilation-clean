---
id: exp-053
title: Pivot-normalized FMA recurrence screen
task: dqi
tests: exhaustive GF(8) four-sample inputs; all 97,119 valid GF(8) eight-point patterns; 48 seeded GF(2^12) DQI samples; 32 compiled pair-cell cases
direction: D-004
status: branch_label_screen
date: 2026-11-20
result: ratio plus history is injective on GF(8); sampled rank-default branch masks are not width-safe; pair cell compiles at Q=880, T=300
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
so this recurrence selects the same branches. A branch-controlled input swap
lets both branches use one in-place update:

```text
before:   if swap, swap(d_i, g_i)
update:   d_i ^= r*g_i; g_i *= delta
```

The shared update uses one GF(2^12) product and no clean output field register;
the controlled input swap costs 12T per pair. The swap branch leaves the update
in FMA output order, so there is no output swap. The ratio needs one product
to compute and one to clear. A compiled one-pair cell uses the existing
in-place GF(2^12) inverse (66T forward, 72T restore), preserves 8 rank bits
and the branch bit, compiles at Q=880 and 300T. Kickmix simulated 32 valid
pivot cases across both branches; the pivot was restored, all 31 scratch qubits were
clean, and there were no phase flips.

The classical screen exhaustively checked all 4,096 four-sample GF(8) vectors
and 48 seeded valid GF(2^12), 70-symbol DQI samples. Branch histories, row
ranks, and the normalized low row matched the existing recurrence in every
case.

## Pivot replay without the pair bank

For pivot `j`, start from its pristine sample `(d_j, 1)` and replay the prior
normalized updates using the earlier pivot ratios and branch choices. Across
all 70 pivots this uses `sum(j)=2,415` variable field products, the same count
as updating every suffix pair in the direct recurrence. The in-place payload
could hold one ratio per sample by replacing `d_j` after that pivot is formed.

The replay screen matched the direct ratios and branch history for all 4,096
arbitrary GF(8) four-sample vectors and 48 valid GF(2^12), 70-symbol DQI
samples. The ratio array alone is not an injective state: the GF(8) screen has
3,052 distinct ratio vectors, maximum input fiber 8, and up to 8 histories for
one ratio vector. Among the 48 DQI samples, zero-ratio counts reached 69 at
weight 1, 8 at weight 31, and 1 at weight 35.

Adding the full branch history made all 4,096 GF(8) ratio/history labels unique.
This still does not give a width-safe history encoding: taking `rank1 < rank2`
as the default branch left up to 69 exception positions in the 48 sampled
GF(2^12) DQI cases (weight 1; 8 at weight 31 and 1 at weight 35). The
screen saw 2, 1, and 3 distinct exception masks at weights 1, 31, and 35;
the final rank pair did not distinguish the masks at weights 1 or 35. This is
sample evidence only. A compact reversible encoding remains unbuilt.

### Rank-assisted branch labels

For all 4,096 arbitrary four-sample GF(8) inputs, the ratio vector plus final
rank has 3,790 distinct labels; 306 labels have two preimages. The second
branch bit separates every colliding pair, so one tag bit suffices on this
four-point screen.

The exhaustive valid eight-point GF(8) screen gives a larger fiber: among
97,119 error patterns through weight four, ratio plus final rank has 85,445
labels, with a maximum of ten inputs per label. At least four extra bits are
needed to distinguish the largest fiber, and no single branch bit resolves
all collisions. Ratio plus the full branch history is injective on this
screened domain.

This rejects extending the four-point one-bit result directly to longer FMA
sequences. It is still small-field information evidence; it gives no
GF(2^12), 70-point bound or reversible history decoder. Exact counts are in
[`results.json`](results.json).

This avoids materializing all `(d,g)` pairs only if the branch/phase label can
also be retained and replayed within the 50-qubit workspace. Its bound and
reversible encoding are still unknown, as are final basis generation and input
cleanup. It is a width lead, not a full schedule.

The corrected 70-symbol FMA count is 2,415 pair products, 140 ratio products,
70 in-place inversions at 138T each, 28,980T for pair input swaps, and 1,680T
for pivot-orientation swaps: 147,630T. Adding the existing sampled
reconstruction ledger, 45,045T scan, and 4,830T branch/rank cell projects
201,375T, leaving 55,568T under the 256,943T screen gate. This count still
excludes the 4+66 width schedule and uncounted phase work.

## Limit

The compiled one-pair cell does not solve width for the full recurrence. The
direct sequential state holds 70 `d` words and up to 69 variable `g` words, or
1,668 qubits before ratio workspace. A complete 4+66 schedule must generate
and consume each pair from the compact 840-qubit payload, keep ratio and rank
state live within Q=890, and account for all cleanup and phase work. The
55,568T margin is only a projection; no full circuit or submission exists.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-053/normalized_fma.py'
```
