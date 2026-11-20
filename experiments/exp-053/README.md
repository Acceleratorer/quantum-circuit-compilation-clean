---
id: exp-053
title: Pivot-normalized FMA recurrence screen
task: dqi
tests: exhaustive GF(8) four-sample inputs; all 97,119 valid GF(8) eight-point patterns; 655,360 transformed GF(8) block states; 48 seeded GF(2^12) DQI samples; 64 arbitrary GF(2^12) 70-symbol sentinel-label vectors; 32 compiled pair-cell cases; fixed-determinant transition counterexample
direction: D-004
status: in_place_ratio_screen
date: 2026-11-20
result: >-
  The full-input four-pivot encoder is Q=902, T=3,200. The constant-aware
  factorized-state proxy peaks at 3,114T across 48 seeded prefixes. Sentinel
  labels alone do not erase branch history.
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
to compute and one to clear. The ratio register is allocated after the
in-place GF(2^12) inverse's temporary output is freed, so those wires are
reused. A compiled one-pair cell uses the existing inverse (66T forward, 72T
restore), preserves 8 rank bits and the branch bit, and compiles at Q=871 and
300T. Kickmix simulated 32 valid pivot cases across both branches; the pivot
was restored, all 22 scratch qubits were clean, and there were no phase flips.

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

The four-point ratio/history label now has an explicit classical inverse. For
pivot `j`, the branch bit selects projective coordinates `[r_j:1]` or
`[1:r_j]`; reversing each earlier normalized update recovers `d_j` as the
final coordinate ratio. This decoded all 4,096 arbitrary GF(8) four-sample
inputs and the first four samples of all 48 GF(2^12) DQI cases. The four
branch bits fit in the five rank-register bits unused after the prefix. This
proves classical reversibility, but the in-place gate circuit and full 4+66
resource schedule remain unbuilt.

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

I also applied 16 sampled four-point left bases to every one of the 4,096
right four-sample GF(8) inputs, at all ten rank states with `r1+r2=9`
(`655,360` cases). The worst ratio/final-rank fiber has three inputs, so at
least two tag bits are needed there. No single branch bit separates every
collision across these setups, but two fixed parities do; their masks are
`[1,2]`, which correspond to retaining the first two local branch bits. A
one-bit tag per four-point block therefore does not extend to these transformed
right blocks. This remains a GF(8) screen, not a GF(2^12) bound. Repeating two
tag bits across 17 blocks would add about 34 qubits to the current `Q=871`
projection, giving `Q=905`, 15 qubits over the limit. This encoding still
needs a width reduction or a schedule that does not keep all tags live.

This avoids materializing all `(d,g)` pairs only if the branch/phase label can
also be retained and replayed within the 50-qubit workspace. Its bound and
reversible encoding are still unknown, as are final basis generation and input
cleanup. It is a width lead, not a full schedule.

The corrected 70-symbol FMA count is 2,415 pair products, 140 ratio products,
70 in-place inversions at 138T each, 28,980T for pair input swaps, and 1,680T
for pivot-orientation swaps: 147,630T. Adding the existing sampled
reconstruction ledger, 45,045T scan, and 5,530T rank-invariant branch cell
projects 202,075T, leaving 54,868T under the 256,943T screen gate. This count
still excludes the 4+66 width schedule and uncounted phase work.

### Four-point compact-state recovery cost screen

`compact_basis_cost.py` exhausts all 4,096 four-sample GF(8) inputs. It recovers
the original samples, reconstructs a valid complementary row with matching
row ranks, and reproduces branch history. The full arithmetic-call proxy peaks
at 8,430T: 1,560T for sample recovery, 168T to compose the low row, 5,946T for
the complementary row, and 756T for branch replay.

A branch-history-only round trip does not need the complementary row. It
normalizes and factors the low row, recovers the four samples from the
factorized state, and replays their branch history. Across the same exhaustive
GF(8) domain, the factorized state uses at most four field words; this path
peaks at 5,118T (median 4,488T). The proxy charges every field-multiplication
call at 42T and every inverse call at 138T, including operations that may
simplify to linear gates. The full block transform still needs a complementary
row; adding the separate 252T low-row composition and 6,138T complement-row
maxima gives an 11,508T arithmetic-only screen. Charged additively against the
54,868T projected margin, that leaves 43,360T before other omitted work. This
is only a feasibility screen: it may overlap the FMA ledger and is not a
compiled reversible circuit or a width, phase, or cleanup bound.

The seeded GF(2^12) DQI screen samples 48 valid four-symbol prefixes from
weight-1, weight-31, and weight-35 errors. The raw arithmetic proxy charges
every field multiply 42T and every inverse 138T; after the low row is formed
and normalized, factorization, sample recovery, and branch replay cost a mean
4,822.25T and a maximum 5,238T. A constant-aware pass treats multiplication by
the public evaluation points as a linear map and divides by the monic gcd
without variable work for its leading `1`. It returns the same factorization,
samples, ratios, and branches at a mean 2,876.125T and maximum 3,114T. This
pass does not count CNOTs, excludes low-row construction, and is not a compiled
circuit or a full 4+66 resource bound. Both results are stored as
`gf12_dqi_cost_proxy` in `results.json`.

The direct shape ID uses four bits, which fits in the unused high bits of the
8-bit rank1 register at the four-point split (rank1 is at most 7), with one
high bit left over. An exhaustive conflict graph over all 4,096 GF(8) inputs
has 9 edges and chromatic number 3, so a two-bit shape color distinguishes all
factorized labels with zero collisions. That color map also had zero collisions
on the 48 seeded GF(2^12) DQI prefixes. The GF(2^12) check is sample-only, and
the two-bit decoder has not been built as a reversible circuit. The direct
four-bit pack/unpack still round-trips all 4,096 GF(8) inputs and 2,048 seeded
GF(2^12) inputs; neither check proves the full 4+66 schedule. A conservative
support-pattern audit of every shape accepted by the generic packer needs
seven colors (three bits). It ignores the arithmetic restrictions on actual
FMA states, so the two-bit map remains an image-specific lead, not a safe
GF(2^12) width reduction.

The same exhaustive sweep finds a full four-point basis with 11 polynomial
coefficient words (`3/2` and `3/3` across the two rows). Replacing the four
input words with those coefficients would make the 840-qubit payload 924
qubits, 34 over the limit before any workspace. Direct full-matrix storage is
therefore rejected for this screened input; the 4+66 path has to stream basis
evaluations or use a more compact representation.

This is not a reversible circuit or a resource bound. It omits branch controls,
degree framing, phase, scratch liveness, and cleanup, and some branch replay
work overlaps the 70-symbol arithmetic ledger. The existing 3,870T sampled
reconstruction assumption is still unvalidated; the two figures cannot be
subtracted or added safely without a circuit schedule. One four-point prefix
does not hit the remaining Toffoli margin by this proxy, but the full 4+66
schedule remains unproven.

Reproduce the focused screen with:

```powershell
python -I .\experiments\exp-053\compact_basis_cost.py
```

### In-place coordinate-label screen

The source-owned `screen_fixed_shape_streaming_labels()` exhausts all 1,568
GF(8) states for monic irreducible quadratic `A` and degree-1 `B`. It checks
every choice of three sample points and either retained `A` coefficient. Each
three-samples-plus-coefficient key has a maximum fiber of four. Branch history
has same-history collisions in every layout, and any side label that depends
only on the discarded coefficient needs at least three bits (the conflict
graphs have chromatic numbers 6 or 7).

This closes the simple branch-history and coefficient-only tags for this
coordinate layout. A second exhaustive screen checked all 4,096 GF(8)-linear
forms of the three retained samples and retained coefficient, with every
possible fixed 2-bit linear projection of `discarded * u(key)`. None labels
the collision fibers in any of the eight layouts. I also searched all 32,768
affine GF(8)-field-linear kernel functions `v(key)=c+Σ λᵢ keyᵢ`, allowing the
two-bit projection to vary with the key; none works in any layout. Arbitrary
GF(2)-linear or nonlinear kernels, higher-degree tags, another residual
representation, and a GF(2^12) circuit remain open.

The source-owned in-place encoder for four pivot ratios and their branch
history remains unbuilt. The inverse label is classically reversible, and its
sample eraser now fits the Q=890 width gate; the forward computation and the
complete 4+66 schedule still need a measured width, Toffoli, phase, and cleanup
ledger.

### Fixed-shape decoder circuit screen

The private Kaggle run of [`fixed_shape_decoder.py`](fixed_shape_decoder.py)
measured the out-of-place decoder for `G=1`, `deg(A)=2`, `deg(B)=1`. Across 32
valid coefficient cases, it recovered all four samples, preserved the inputs
and rank/branch registers, cleared all scratch, and produced no phase flips.
It compiled at `Q=952`, `T=612`, which is 62 qubits over the `Q=890` gate.
The breakdown is 840 payload + 8 rank + 1 branch + 48 fresh output + 55
scratch qubits. This closes the out-of-place layout only; an in-place or
streamed decoder is still needed.

The gate helper is the unchanged Apache-2.0 port documented in
[`src/dqi/NOTICE`](../../src/dqi/NOTICE); gate code must run only in a private
Kaggle kernel. The measured run is [kernel version 5](https://www.kaggle.com/code/accelra/exp053-fixed-shape-decoder).

### In-place ratio/history sample eraser

[`inplace_ratio_history.py`](inplace_ratio_history.py) compiles the inverse
label step for pivots 0 through 3. For each pivot, it initializes projective
coordinates from the ratio and branch bit, reverses the earlier normalized
updates, and XORs the recovered sample into its existing payload word. It
then uncomputes the field-pair workspace. The test preserves all ratio/history
bits and rank state, clears all scratch, and reports zero phase flips for 32
arbitrary GF(2^12) four-sample vectors per pivot.

Each circuit compiles at `Q=890` with 42 clean scratch qubits. The three low
rank bits and one unused high rank bit are temporarily borrowed: branch
history determines rank1, so the circuit resets those bits, uses the same
physical wires as clean arithmetic workspace, then restores rank1. The
Toffoli-like counts for pivots 0 through 3 are 208, 320, 432, and 540. Results
come from [private Kaggle kernel version 9](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history).

Kernel version 9 closes only the sample-erasure half of the 4-pivot label map.
Version 14 composes that eraser with the forward computation, as recorded
below; neither version establishes the full 4+66 schedule.

### Compiled 4-pivot prefix encoder

[`inplace_ratio_history.py`](inplace_ratio_history.py) now composes the forward
ratio/history calculation with the verified sample eraser. Starting with four
samples in payload words 4 through 7 and four clean ratio words in slots 0
through 3, it computes each normalized pivot update, records the branch bit,
writes the ratio, and clears that source sample. The branch-based rank1 state
and the other 62 payload words are preserved.

Private Kaggle kernel version 14 checked 32 arbitrary GF(2^12) four-sample
vectors, including the all-zero vector. Ratios and history matched the
classical recurrence; samples and scratch were cleared; untouched payload was
preserved; and no phase flips occurred. It compiled at `Q=890` with 42 clean
scratch qubits and 3,200 Toffoli-like gates. Use
[`build_private_kernel.py`](build_private_kernel.py) to package the source and
the unchanged arithmetic helper for the private kernel.

This verifies only the four-pivot prefix. The remaining 66-point schedule,
complete circuit resource ledger, and competition submission are still open.

### Full-input prefix compatibility

The in-place option in [`inplace_ratio_history.py`](inplace_ratio_history.py)
starts with all 70 payload words arbitrary and overwrites the first four source
words with their ratios. Private Kaggle kernel version 16 checked 32 random
GF(2^12) prefixes, preserved the other 66 words and branch/rank outputs, cleared
all scratch, and reported zero phase flips. It compiled at `Q=902`, `T=3,200`
with 54 clean scratch qubits.

This closes the four-pivot input-layout mismatch, but costs 12 more qubits than
the `Q=890` clean-slot subroutine while saving no gates. It is not a scoring
candidate and has not been submitted. The complete 4+66 decoder remains open.

### Projective sentinel label screen

[`inplace_ratio_codec.py`](inplace_ratio_codec.py) tests an in-place label for
each pivot. The prefix matrix maps `[x:1]` to `[d:g]`. When both matrix
coefficients for `x` are nonzero, finite inputs contain both zero-coordinate
cases: the raw oriented ratio maps both to zero and omits the ratio of the
matrix's image of infinity. Replacing the `d=0` label with that missing value
makes the local map a permutation. If either coefficient is zero, the raw map
is already a permutation.

For any fixed invertible prefix matrix and rank-order flag, the local map from
the next sample to its sentinel label is a permutation of the field. If both
first-column entries `a,c` are nonzero, the two roots of `a*x+b` and `c*x+d`
are distinct; the raw oriented ratio duplicates zero at those roots and omits
the projective ratio at infinity. Replacing the no-swap zero with `a/c` (or
the swap zero with `c/a`) restores a permutation. If either `a` or `c` is
zero, the raw map is already a permutation. Each prefix matrix stays
invertible because its determinant is a product of nonzero point differences.
Earlier labels determine that matrix and the rank-order flag, so induction
makes the full sample-vector-to-label-vector map a permutation over any finite
binary field and any distinct evaluation points.

The exhaustive GF(8) screen round-tripped all 4,096 arbitrary four-sample
vectors and verified all 585 local prefix contexts. In GF(2^12), 48 valid
70-symbol DQI vectors and 64 seeded arbitrary 70-symbol vectors round-tripped;
ratios and branches matched the independent direct recurrence. These checks
support the proof and exercise the implementation; they do not compile the
permutation. The reversible circuit, branch oracle, liveness, phase cleanup,
and full resource schedule remain unbuilt. Results are in
[`results.json`](results.json).

The fixed-determinant GF(8) counterexample remains a real local collision:
`(matrix, sample) -> (updated matrix, label)` is not injective when the matrix
is treated as an independent input. It does not contradict the full
triangular label map, because the prefix matrix is determined by the earlier
labels. It does rule out treating the updated matrix and current label alone
as the complete reversible state.

## Limit

The compiled one-pair cell does not solve width for the full recurrence. The
direct sequential state holds 70 `d` words and up to 69 variable `g` words, or
1,668 qubits before ratio workspace. A complete 4+66 schedule must generate
and consume each pair from the compact 840-qubit payload, keep ratio and rank
state live within Q=890, and account for all cleanup and phase work. The
54,868T margin is only a projection; no full circuit or submission exists.

## Reproduce

`normalized_fma.py` also imports the ported gate arithmetic from `src/dqi`;
run its circuit checks only in a private Kaggle kernel. Its classical screens
and the compiled fixed-shape result are recorded in `results.json`.
