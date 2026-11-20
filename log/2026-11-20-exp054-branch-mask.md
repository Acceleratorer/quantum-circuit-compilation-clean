---
id: 2026-11-20-exp054-branch-mask
date: 2026-11-20
---

# exp-054 — branch-mask width screen

Screened the FMA rank-default exception mask as a possible encoding for the
branch history. Across all 4,095 nonzero single-error locations at magnitude 1,
only 70 masks appeared and none had more than two transitions. Selected
magnitude cross-checks matched.

Across 512 samples at each of weights 31 and 35, weight 31 reached five
transitions (two cases); weight 35 reached two. A generic enumerative code for
the observed five-transition cap needs 25 bits, six more than the optimistic
19-qubit room left by the current pair-cell projection. Sampled masks have low
cardinality, but an exact valid-domain encoder is still missing. Keep this as a
width lead, not a decoder candidate.

Reproduction: `python -I experiments/exp-054/branch_mask_screen.py`.
