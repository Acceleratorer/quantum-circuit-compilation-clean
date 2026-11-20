---
id: exp-052
title: FMA sample-update reversibility screen
task: dqi
tests: exhaustive GF(4) tuples, exhaustive valid GF(8) errors, all 4,096 GF(8) four-sample inputs, sampled GF(2^12) DQI errors
direction: D-004
status: local_transition_feasibility
date: 2026-11-20
result: the fused four-point factorized state is injective in the GF(8) screen and uses at most four field words; its in-place reversible circuit remains open
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

## Pivot and branch replay

Step `j` updates only samples `i>j`; later steps also leave sample `j`
untouched. The final sample array therefore retains every pivot pair used by
the forward pass. Replaying the branch predicate from the initial ranks and
these pivots recovers the same branch sequence classically.

The checker counted distinct full `(d,g,rank1,rank2)` states after every
step. All 256 pristine GF(4) inputs remained distinct, as did all 97,119 valid
GF(8), eight-point error patterns through weight four. This is small-domain
evidence only; it does not provide a low-space reversible replay circuit or
show that its Toffoli cost fits the score gate.

### Storage gate for this replay idea

The classical checker keeps both 70-symbol `d` and `g` arrays. That pivot
array is 140 GF(2^12) values, or 1,680 qubits, so it cannot be the retained
state of a `Q<=890` circuit. Storing all 70 branch bits beside the 840-qubit
payload also needs 70 history qubits plus 16 rank qubits: 926 qubits before
arithmetic scratch. The direct replay schedule therefore fails the width gate.

Kickmix's measurement primitive is HMR, an X-basis measurement whose output is
random and carries phase kickback; it does not expose a computed branch value
as a classical bit. See the [Kickmix circuit format](https://github.com/quantumlib/Qualtran/blob/main/docs/kickmix/kickmix_format.md#semantics)
and [HMR instruction](https://github.com/tanujkhattar/zkp_ecc/blob/main/docs/kickmix_instruction_set.md#hmr-instruction).
The remaining option is a branch oracle derived from the compact FMA payload,
with a complete <=50-qubit and Toffoli schedule. No such oracle is known yet.

## Limits

This removes the need to keep an old copy of an individual right-side pair if
the pivot and branch are available. Pivot retention makes the branch sequence
replayable, but a reversible replay circuit and its cost are still missing.
The polynomial-basis state, full 70-symbol liveness, and `Q<=890`,
`T<=256,943` gates remain unproved. No circuit was built or submitted.

The naive replay from retained pivots is closed on width. Reopen branch replay
only with a branch oracle derived from the compact FMA payload and a complete
Toffoli, phase, and <=50-qubit liveness ledger.

### Local branch-window screen

`fma_branch_window.py` exhaustively checks all 97,119 valid GF(8), eight-point
error patterns through weight four. For each step it asks whether the branch
is determined by the two post-step ranks, the current pivot, and the nearest
previous/next pivot pairs. The minimum windows contain 1, 1, 1, 2, 4, 4, 5,
and 5 pair values for steps 0 through 7. Later steps need several retained
pairs; ranks plus the current pivot are insufficient. At GF(2^12), five raw
pairs plus two 8-bit ranks would be 136 feature bits. Exact counts are in
[`branch_window_results.json`](branch_window_results.json).

This closes the small local-window oracle. It does not rule out deriving a
branch directly from the compact polynomial payload; that would need its own
costed circuit. Run the screen with:

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_branch_window.py'
```

### Locator-support-only branch-history screen

`fma_locator_history.py` groups every valid GF(8), eight-point error pattern
through weight four by its error-location support, then checks all nonzero
magnitude assignments for that support. Branch history varies with magnitudes:
one of 35 weight-three supports has two histories, and seven of 35 weight-four
supports have multiple histories (up to five). This rejects a locator-support-
only branch oracle on this domain. It does not rule out a direct oracle that
uses the compact payload, and gives no 70-point circuit or Toffoli bound. Exact
counts are in [`locator_history_results.json`](locator_history_results.json).

The same exhaustive pass also grouped cases by the normalized final low row of
the composed basis. It found 99 rows; 8 occurred with multiple branch histories,
with up to 5 histories for one row. This rejects recovery from that row alone,
not an oracle that reads the complete compact payload. The witness and counts
are in [`locator_history_results.json`](locator_history_results.json).

The exact full 2x2 basis matrix was distinct for all 97,119 valid patterns and
never paired one matrix with multiple histories. At split `4+4`, a compact
left state consisting of the normalized low row and the common-zero exception
samples directly recovered all four original left samples and their branch
history in all 97,119 cases. This state used at most two exception samples;
adding the untouched right samples produced 97,119 distinct compact states.
This supports the small-domain encoding, but does not prove a reversible
GF(2^12) implementation or its Q/T cost. Detailed counts are in
[`locator_history_results.json`](locator_history_results.json).

An exhaustive screen over all 4,096 arbitrary GF(8) four-sample vectors at
points `{0,1,2,3}` recovered every input from the normalized low row and its
exception samples, with no compact-state collisions. The exception-count
distribution was 0: 2,570, 1: 1,232, and 2: 294. This screen removes the RS
weight restriction on the four local samples, but remains a small-field
information screen; counts are in
[`locator_history_results.json`](locator_history_results.json).

There is also a field-independent two-exception bound. For four FMA points,
the row ranks sum to 9, so the minimum row rank is at most 4. For its
normalized `(W,N)` row, this gives `deg(W) <= 2`; if `N` is nonzero,
`deg(N) <= 1`. Thus `gcd(W,N)` has degree at most 2 and can have at most two
distinct common-zero exception points.

### Fused four-point factorized state

The exception values need not be kept as a separate sidecar in the logical
state. Factor the normalized low row as `W=G*A`, `N=G*B`, and store the monic
`G` without its leading 1, the coefficients of `A` and `B`, and the original
`d_i` values at points where `G(x_i)=0`. Those point locations are derived from
`G`: the FMA basis determinant is the four-point node polynomial, so `G` divides
that polynomial and its roots lie among the four public points. This
representation needs no location mask. Every other sample is `B(x_i)/A(x_i)`.

The same 4,096-input GF(8) screen found 4,096 distinct factorized states, no
collisions, at most two common-root samples, and at most four field words in
the listed polynomial/sample coefficients. The reconstruction argument is
field-independent: at a nonroot of `G`, the sample constraint gives
`d_i*A(x_i)+B(x_i)=0`; since `A` and `B` are coprime, `A(x_i)` is nonzero and
`d_i=B(x_i)/A(x_i)`. At roots, the saved sample restores `d_i` directly.

Four GF(2^12) samples have a fixed-width 48-bit label: the four recovered
sample values in point order. The exhaustive GF(8) screen checks that every
factorized state maps to a distinct label. This avoids serializing the
variable-length polynomial tuple, but the in-place reversible circuit that
computes this mapping, its scratch liveness, phase cleanup, and Toffoli cost
remain undesigned.

The existing 840-qubit payload can therefore remain the width target if the
four-sample factorization is implemented in-place. Under the existing branch
cell assumption that its pivot pair is already in the payload, the branch
projection is `Q=880`, leaving ten qubits. This is an information-width lead,
not a verified schedule: the factorization's scratch, Toffoli cost, phase
cleanup, and pivot liveness are still uncounted.

### 4+66 explicit sidecar alternatives

The first block contains FMA points `{0,1,2,3}`. Verifier error locations are
nonzero field elements, so only points `1,2,3` can be common-zero exception
locations. The two-exception bound gives at most two 12-bit `d` samples. A
sorted record can use a 3-bit location mask and two 12-bit values: 27 qubits;
the reversible routing that packs values into those sorted slots is not
designed. Dense enumeration of all 50,343,937 possible support/value records
needs 26 bits, but its reversible encoder and decoder are also unbuilt. A
fixed-position representation remains 39 bits (3-bit mask plus three 12-bit
slots) and avoids sorting. These are fallback capacity counts; the fused
factorized state above is the current width lead.

For four left constraints, the two row ranks sum to 9, so the normalized
minimum-rank row has rank at most 4 and at most four stored field coefficients
after omitting its fixed leading 1. Together with the 66 untouched right
samples, that gives the existing 840-qubit persistent payload. The 27-bit
sorted sidecar projects to `Q=907` while live through the branch cell; the
26-bit dense capacity projects to `Q=906`, and the 39-bit fixed-position
sidecar to `Q=919`. The rank-invariant branch cell has 40 additional live
workspace qubits after its 24-qubit pivot pair is counted inside the payload.
All three projections exceed the 890 limit. The 27-bit sorted format is 17
qubits over the gate; its routing cost and liveness are still unproved.

**Decision:** keep explicit sidecars closed while they exceed the width gate.
Pursue the fused four-point factorization as the width lead, but do not count it
as a circuit until an in-place reversible encoder, decoder, and liveness/phase
ledger exist. This does not close the 4+66 FMA path.
At the latest 2,048-shot sample maximum of 246,831T, adding the 4,830T local
branch gate leaves 5,282T below the 256,943T gate for all still-unaccounted
work.

The explicit sidecar extractor has a six-test shape: three tests for `G(i)=0` and
three for `D_i=d_i*A(i)+B(i)=0`, at `i=1,2,3`. It needs three field products
to form the `D_i`, and three Toffolis for `exception_i = [G(i)=0] AND
[D_i!=0]`. A direct 12-bit zero test uses 42 Toffolis and 10 reusable clean
ancillas; six tests cost 252T in this construction. Holding two temporary
flags and those ancillas gives pre-field-register peaks of `Q=891` for the
39-bit fixed-position format, `Q=879` for the 27-bit sorted format, and `Q=878`
for the 26-bit dense format.

Recovering the four left samples can require up to four ratios. At the current
field costs, one inverse, one multiply, and inverse erasure is 153T, or 612T
for four samples. The fixed-position format writes three 12-bit slots (36T),
for a 1,029T listed subtotal including the three `D_i` products, six zero
tests, and three mask gates. The sorted two-slot format writes 24 bits, giving
1,017T before its uncounted value-routing cost. Neither subtotal is a
reconciled incremental cost: products may overlap the dynamic-taint ledger,
and output selection, phase correction, and cleanup remain uncounted.

Run the screen with:

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_locator_history.py' --four-sample-exceptions
```

### One branch/rank gate kernel

`fma_branch_gate.py` builds one reversible leaf operation in Kickmix: compute
the branch predicate, update both 8-bit ranks, and retain a one-bit selector
for the sparse lower row of the leaf matrix. The general rank-comparison cell
uses 95 Toffoli-like gates and 73 qubits including its 24-bit pivot pair and
ranks.
For a fixed point polynomial `L`, the selector represents either
`[L, 0]` or `[0, L]` in the lower row; `d` and `g` supply the top row.
Projecting the pivot pair into the existing 840-qubit payload gives `Q=889`.
Repeating the local count for 70 leaves costs 6,650T and leaves 3,138T of the
9,788T remainder for every omitted operation.

This is only a local gate count. It does not generate the pivot pairs, build
the FMA tree, or prove selector liveness through recursive composition. Exact
counts and assumptions are in
[`branch_gate_results.json`](branch_gate_results.json). The script checks the
compiled cell on all 65,536 rank pairs in each of the four `d/g` zero classes
(262,144 shots total); the selector/ranks match the reference, all 32 scratch
qubits return to zero, and no phase flips occur. This verifies the leaf kernel,
not its recursive composition or the data-pair matrix update.

### Rank-sum specialization

At step `j`, the rank invariant is `r1+r2=2j+1`, so `r1<r2` is equivalent to
`r1<=j`. Comparing `r1` to the public constant `j+1` and deriving `r2` by
reflection on the swap branch leaves one 8-bit rank register. The gate uses 69
Toffoli-like gates and 64 qubits per step. The exhaustive check covers all
19,880 valid rank/zero-class cases across `j=0..69`; the rank and selector
match, all 31 scratch qubits return to zero, and there are no phase flips.
Across 70 steps this is 4,830T, saving 1,820T against the general cell and
leaving 4,958T of the previous 9,788T margin. The projected total is `Q=880`
if the 24-bit pivot pair is already part of the 840-qubit payload.

This remains a local count. It excludes generating the pivot pairs, recursive
FMA composition, selector liveness, and other omitted work; it does not prove
the complete DQI circuit fits either score gate. Detailed counts are in
[`branch_gate_results.json`](branch_gate_results.json).

## Run

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_pivot_reversibility.py'
```
