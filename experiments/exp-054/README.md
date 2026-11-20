---
id: exp-054
title: FMA rank-default exception-mask width screen
task: dqi
tests: all 4,095 single-error locations at magnitude 1; 21 scalar magnitude cross-checks; 1,280 seeded valid DQI samples at weights 1, 31, and 35
direction: D-004
status: width_screen
date: 2026-11-20
result: single-error masks have 70 values and at most 2 transitions; sampled weight-31 masks reach 5 transitions
---

# FMA rank-default exception-mask screen

## Question

Can the branch history be stored as a compact exception mask relative to the
default branch `rank1 < rank2`, within the DQI circuit's 50-qubit workspace?

## Result

For every nonzero error location in `GF(2^12)` at magnitude 1, the 70-bit
exception mask has only 70 distinct values and at most two transitions. The
screen cross-checked seven locations at three nonzero magnitudes each against
the scalar recurrence; those checks matched. This covers the enumerated
locations at magnitude 1 and selected magnitudes, not all single-error inputs.

For two seeded sets of 256 samples each at weights 31 and 35, the combined
sample has 12 distinct weight-31 masks and 15 distinct weight-35 masks. The
weight-31 sample includes two masks with five transitions; the weight-35
sample has at most two. One additional 256-case weight-1 screen gives 33
distinct masks across all 1,280 sampled errors. These counts are sample
evidence, not a bound on the valid DQI domain.

An enumerative code for any 70-bit mask with at most five transitions takes
25 bits. That is six bits above the current optimistic 19-qubit headroom after
the `Q=871` pair-cell projection. A sampled-mask lookup would need far fewer
bits, but no exact encoder for all valid DQI inputs is known. No reversible
encoding, decoder, or full-circuit liveness schedule was built.

## Reproduce

From the repository root:

```powershell
python -I experiments/exp-054/branch_mask_screen.py
```

The script writes the counts to `results.json`. It uses the existing NumPy
dependency to accelerate the exhaustive single-error support sweep.
