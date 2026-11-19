---
id: exp-052
title: FMA sample-update reversibility screen
task: dqi
tests: exhaustive GF(4) tuples, exhaustive valid GF(8) errors, sampled GF(2^12) DQI errors
direction: D-004
status: local_transition_feasibility
date: 2026-11-20
result: sample updates invert exactly; expanded pivot replay fails the width gate; local-window and support-only branch oracles fail GF(8) screens; one branch/rank cell costs 95T
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

Run the screen with:

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_locator_history.py'
```

### One branch/rank gate kernel

`fma_branch_gate.py` builds one reversible leaf operation in Kickmix: compute
the branch predicate, update both 8-bit ranks, and retain one branch output
tag. The compiled cell uses 95 Toffoli-like gates and 73 qubits including its
24-bit pivot pair and ranks. Projecting the pair into the existing 840-qubit
payload leaves 49 additional qubits (`Q=889`), assuming the branch tag is part
of the base matrix output. Repeating the cell for 70 points costs 6,650T and
leaves 3,138T of the 9,788T remainder for every other omitted operation.

This is only a local gate count. It does not generate the pivot pairs, build
the FMA tree, show how all branch tags fit into the compact matrix, or clean
multi-step history. Exact counts and assumptions are in
[`branch_gate_results.json`](branch_gate_results.json). The script checks the
8-bit comparator and rank update logic exhaustively over their small domains.

## Run

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -I `
  'experiments/exp-052/fma_pivot_reversibility.py'
```
