---
id: 2026-11-20-exp054-branch-mask
date: 2026-11-20
---

# exp-054 — branch-mask width screen

Screened the FMA rank-default exception mask as a possible encoding for the
branch history. Across all 4,095 nonzero single-error locations at magnitude 1,
only 70 masks appeared and none had more than two transitions. Selected
magnitude cross-checks matched.

Across 50,000 samples at each of weights 31 and 35, 258 distinct masks
appeared. Weight 31 reached nine transitions once; weight 35 reached four. A
generic enumerative code for the observed nine-transition cap needs 37 bits,
18 more than the optimistic 19-qubit room left by the current pair-cell
projection. A codebook for the 258 observed masks would take nine bits, but an
exact valid-domain encoder is still missing. Keep this as a width lead, not a
decoder candidate.

Reproduction: `python -I experiments/exp-054/branch_mask_screen.py`.
