---
id: exp-053
title: Pivot-normalized FMA recurrence screen
task: dqi
tests: prior GF(8) and GF(2^12) screens; private Kaggle kernel screens through version 36
direction: D-004
status: four_pivot_prefix_only; four_plus_one_closed_on_width
date: 2026-11-26
result: v34 four-pivot prefix passes at Q=890/T=3,032. v35/v36 four-plus-one continuation stays at Q=891, one over limit, with clean phase and scratch. The remaining 65 pivots are unbuilt; close this route.
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
97,119 error patterns through weight four, ratios alone have 69,956 distinct
vectors and a maximum fiber of 42. Ratio plus final rank has 85,445 labels,
with a maximum fiber of ten; no single branch bit resolves all collisions.
The fixed-projection scan finds that six branch bits (positions 2–7) separate
every ratio fiber, while four bits suffice alongside final rank (nine
four-position sets work). Ratio plus the full branch history is injective on
this screened domain. These are GF(8) information counts, not a GF(2^12)
bound or a reversible decoder; see the [projection evaluation](../../evals/2026-11-22-exp053-valid-ratio-history.json).

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
projects 202,075T, leaving 13,101T under the latest 215,175.99T score-equivalence
gate. This count still excludes the 4+66 width schedule and uncounted phase work.

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
13,101T projected margin, that leaves 1,593T before other omitted work. This
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
full 70-symbol permutation. The four-pivot branch eraser is measured below;
the complete 4+66 resource schedule remains unbuilt. Results are in
[`results.json`](results.json).

The fixed-determinant GF(8) counterexample remains a real local collision:
`(matrix, sample) -> (updated matrix, label)` is not injective when the matrix
is treated as an independent input. It does not contradict the full
triangular label map, because the prefix matrix is determined by the earlier
labels. It does rule out treating the updated matrix and current label alone
as the complete reversible state.

### Compiled four-pivot sentinel-label encoder

[`inplace_ratio_history.py`](inplace_ratio_history.py) now computes the
sentinel labels for pivots 1 through 3 after the explicit ratio/history encoder.
The private Kaggle kernel [version 21](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/21)
compiled and simulated 32 arbitrary GF(2^12) four-sample inputs, including the
all-zero vector. Labels matched the classical codec, branch history and the
other 66 payload words were preserved, all 71 scratch qubits were clean, and
there were zero phase flips.

The circuit measured `Q=919`, `T=5,902`, compared with `Q=902`, `T=3,200` for
the ratio/history baseline: 17 more qubits and 2,702 more Toffoli-like gates.
It still retains all four branch bits and exceeds the `Q=890` gate by 29
qubits. This proves the four-pivot relabeling circuit works, but this layout is
not a scoring candidate. It does not establish branch-history erasure or the
complete 4+66 schedule; see [`results.json`](results.json).

### Four-pivot branch erasure — kernel version 22

The source-owned encoder now derives each branch back from its sentinel label,
clears the branch bit, and frees that wire as reusable workspace. Private
[Kaggle kernel version 22](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/22)
simulated 32 arbitrary GF(2^12) four-sample inputs. All labels and final ranks
matched; the four branch registers were erased; the other 66 payload words were
preserved; all scratch was clean; and there were zero phase flips.

This version measured `Q=928`, `T=6,212`, with 84 clean scratch qubits. It
eliminates the four stored branch bits, but its peak is 9 qubits wider and 310T
higher than the version 21 explicit sentinel circuit. It misses `Q=890` by 38
qubits. Close this explicit all-fields-live layout as a scoring candidate;
carry forward only the reversible label/branch relation if a complete schedule
can reuse payload wires to fit the width gate. This result does not prove the
4+66 schedule.

### In-place measurement erasure — kernel version 23

The measurement-based sample eraser was tested on the full-input ratio/history
prefix in private [kernel version 23](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/23).
Across 32 arbitrary GF(2^12) cases, labels and branch history matched the
reference, the other 66 payload words were preserved, scratch was clean, and
there were no phase flips.

The circuit measured `Q=902`, `T=4,700`: the same 12-qubit overage as the
unitary prefix and 1,500 more Toffoli-like gates. The sample is measured only
after the forward ratio workspace is live, so this eraser does not lower peak
width. Close this variant; the next width work belongs in the forward prefix
schedule. The full screen output and receipt are in
[`logs/kernel-v23-output.json`](logs/kernel-v23-output.json) and
[`evals/2026-11-22-exp053-mbu-prefix-v23.json`](../../evals/2026-11-22-exp053-mbu-prefix-v23.json).

### Direct sample output attempt — kernel versions 25 and 26

The next width attempt wrote the ratio into its source payload word, then tried
to erase the duplicate sample from the temporary FMA pair. Private kernel
version 24 failed the spectator-preservation assertion; versions 25 and 26
identified payload word 4 as changed in shots 1 through 8. Version 26 repeated
the attempt with measurement erasure and hit the same failure. This fails
correctness before resource accounting, so the source change was discarded.
The failure receipt and raw log are in
[`evals/2026-11-22-exp053-direct-output-v25.json`](../../evals/2026-11-22-exp053-direct-output-v25.json)
and [`logs/kernel-v25-direct-output-failure.log`](logs/kernel-v25-direct-output-failure.log).

### In-place measurement recycling — kernel version 30

Kernel [version 30](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/30)
measures each source word before ratio generation and reuses those wires for
the ratio outputs. On 32 arbitrary GF(2^12) inputs, labels and branch history
matched the recurrence, the other 66 payload words were preserved, all 42
scratch qubits were clean, and there were no phase flips. The prefix compiled
at `Q=890`, `T=3,032`, down 12 qubits and 168 Toffoli-like gates from the
full-input unitary prefix.

This closes the prefix width gate only. The full 4+66 schedule, cumulative
resource count, and official verifier remain untested; there is no candidate
submission. See the [evaluation receipt](../../evals/2026-11-22-exp053-measurement-recycle-prefix-v30.json)
and [captured output](logs/kernel-v30-output.json).

## Fifth-pivot compact-state screen

The standalone screen in [fifth_pivot_state.py](fifth_pivot_state.py)
exhausts all 32,768 five-word GF(8) inputs. The key made from five ratios,
normalized low row, and final ranks has 46 collision groups, each of size two.
The Boolean tag `branch[1] AND NOT branch[4]` makes all labels unique; no
single branch bit or fixed parity does. A seeded sample of 32 valid
GF(2^12) DQI inputs at each of weights 31 and 35 found no collisions.

The branch-retaining prefix compiled in private kernel v31: 32 arbitrary
GF(2^12) cases matched the recurrence with clean scratch and zero phase flips,
at Q=891 and T=4,500. It misses the Q gate by one qubit. The sentinel/recycle
branch-erasure variant is closed: v32 measured Q=916/T=6,044 for four pivots;
its five-pivot form had Q=917/T=7,512, two dirty scratch qubits, and 15 phase
flips in 32 cases. Receipts:
[v31](../../evals/2026-11-22-exp053-five-pivot-prefix-v31.json),
[v32](../../evals/2026-11-22-exp053-sentinel-recycle-v32.json).

Final ranks plus the one-bit tag reduce the 32 possible histories to at most
four candidates across 14 signatures (candidate counts 1, 2, or 4). This
combinatorial bound is independent of field values and narrows a reversible
decoder design; it does not establish its gate cost or correctness.

On the 64 sampled valid GF(2^12) inputs, all four rank/tag candidates were
decoded and forward-replayed using only ratios, ranks, and tag; one history
matched each input. This does not prove uniqueness for the full DQI domain or
provide a reversible circuit.

An exact five-word GF(8) follow-up asks whether `b1` can be erased using only
the ratios, final ranks, retained bits `b0/b4`, and the one-bit tag. It finds
1,920 ambiguous keys among 30,848, so this reduced key is insufficient; the
compact-state low row or a different reversible state is required. This is
still an information screen, not a GF(2^12) bound or a gate circuit. See the
[follow-up receipt](../../evals/2026-11-22-exp053-fifth-pivot-ratio-tag-screen.json)
and [dated log](../../log/2026-11-22-exp053-fifth-pivot-ratio-tag-screen.md).

The v31 information result did not establish a GF(2^12) inverse or a reversible
tag eraser. Version 33 compiles a partial two-bit history compaction, but it
still does not establish the complete schedule or pass the official verifier.
The score-equivalence gate is `Q <= 890` and mean `T <= 215,175.99` at
`R=1.1912605`. See the [evaluation](../../evals/2026-11-22-exp053-fifth-pivot-state.json)
and [dated log](../../log/2026-11-22-exp053-fifth-pivot-state.md).

### Five-pivot history compaction — kernel version 33

The compiled rank identity erases branch pivots 2 and 3, retaining pivots 0,
1, and 4. All 32 arbitrary GF(2^12) cases preserved labels, branch history,
and spectator payload; scratch was clean and phase flips were zero. The
identity itself was checked over all 32 branch histories.

Compaction occurs after the prefix peak, so the circuit remains `Q=891`,
`T=4,500`, unchanged from v31. It misses the `Q=890` gate by one qubit and is
closed as a standalone scoring candidate. The identity is useful only if a
complete schedule can reuse the freed wires before its own peak. See the
[evaluation](../../evals/2026-11-22-exp053-compact-history-v33.json),
[dated log](../../log/2026-11-22-exp053-compact-history-v33.md), and
[captured output](logs/kernel-v33-output.json).

### Four-pivot handoff compaction — kernel version 34

After four pivots, final rank gives `b1 = b3 XOR rank1[1]` for every one of
the 16 branch histories. The compiled transform erases `b1` and retains branch
pivots 0, 2, and 3. On 32 arbitrary GF(2^12) cases, labels and retained
history matched, spectator payload was preserved, scratch was clean, and
phase flips were zero.

The prefix remains `Q=890`, `T=3,032`, but returns 43 clean scratch qubits
instead of 42. That gives the next 66-point stage one more clean wire at the
4+66 handoff; the tail itself remains unbuilt and unmeasured. See the
[evaluation](../../evals/2026-11-22-exp053-four-pivot-compaction-v34.json),
[dated log](../../log/2026-11-22-exp053-four-pivot-compaction-v34.md), and
[captured output](logs/kernel-v34-output.json).

The same local rank identity does not repeat by itself: across four-branch
blocks starting at points 2 through 66, exhaustive rank-state enumeration
found no branch bit recoverable from final rank1 and the other three local
bits. Tail compression must use the ratio or additional FMA state.

### Four-to-five-pivot handoff — kernel version 35

Version 35 compacts the four-pivot history at the handoff, reconstructs the
released branch bit for pivot 4, then compacts the five-pivot state. All 32
GF(2^12) cases matched the reference labels and retained history; payload was
preserved, scratch was clean, and phase flips were zero. The measured circuit
uses `Q=891` and `T=4,500`, so it misses the `Q=890` limit by one qubit before
the remaining 65 pivots. Close this 4+1 layout; do not integrate it as a
candidate. See the [evaluation](../../evals/2026-11-26-exp053-four-plus-one-handoff-v35.json),
[dated log](../../log/2026-11-26-exp053-four-plus-one-handoff-v35.md), and
[private kernel](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/35).

### Parity-controlled follow-up — kernel version 36

Version 36 stores the rank bit at the handoff and replaces the decoded-branch
ancilla with parity-controlled rank reflections and CSWAPs. The same 32-case
checks pass with clean scratch and zero phase flips, but width remains
`Q=891`; Toffolis rise by 76 to `T=4,576`. This closes the 4+1 continuation.
See the [evaluation](../../evals/2026-11-26-exp053-parity-handoff-v36.json),
[dated log](../../log/2026-11-26-exp053-parity-handoff-v36.md), and
[private kernel](https://www.kaggle.com/code/accelra/exp053-inplace-ratio-history/versions/36).

## Limit

The compiled one-pair cell does not solve width for the full recurrence. The
direct sequential state holds 70 `d` words and up to 69 variable `g` words, or
1,668 qubits before ratio workspace. A complete 4+66 schedule must integrate
the measured prefix, generate and consume each pair from the compact 840-qubit
payload, and stay within `Q=890` and the current score-equivalent threshold of
`T=285,041.64` at that width, including cleanup and phase. This threshold is
derived against the 2026-11-26 leaderboard and will move with the leaderboard;
see the [current gate receipt](../../evals/2026-11-26-dqi-score-equivalent-gate.json).
The measured 4+1 continuation misses width by one qubit, so exp-053 is closed
without a full circuit or submission.

## Reproduce

`normalized_fma.py` also imports the ported gate arithmetic from `src/dqi`;
run its circuit checks only in a private Kaggle kernel. Its classical screens
and the compiled fixed-shape result are recorded in `results.json`.
