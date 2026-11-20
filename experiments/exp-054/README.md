---
id: exp-054
title: FMA rank-default exception-mask width screen
task: dqi
tests: all 4,095 single-error locations at magnitude 1; 21 scalar magnitude cross-checks; 100,000 seeded valid DQI samples at weights 31 and 35
direction: D-004
status: width_screen
date: 2026-11-20
result: single-error masks have 70 values and at most 2 transitions; 100,000 dense samples show 258 masks and up to 9 transitions
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

For 50,000 seeded samples at each of weights 31 and 35, the screen found 171
weight-31 masks and 87 weight-35 masks, with 258 distinct masks across both
weights. Weight 31 reached nine transitions once; weight 35 reached four.
These counts are sample evidence, not a bound on the valid DQI domain.

An enumerative code for any 70-bit mask with at most nine transitions takes
37 bits, 18 above the current optimistic 19-qubit headroom after the `Q=871`
pair-cell projection. A lookup for the 258 sampled masks would need nine bits,
but no exact codebook for all valid DQI inputs is known. No reversible
encoding, decoder, or full-circuit liveness schedule was built.

## Reproduce

From the repository root:

```powershell
python -I experiments/exp-054/branch_mask_screen.py
```

The script writes the counts to `results.json`. It uses the existing NumPy
dependency to accelerate the exhaustive single-error support sweep.
