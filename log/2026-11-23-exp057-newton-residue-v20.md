# exp-057 v20: Newton residue insertion

## Decision

No-go for the straightforward Newton insertion path. It exactly maintains the
scan-ready numerator when given every error root and desired residue, but those
are not the inputs produced by the current FMA sample stream. Its coefficient-
array operation count also exceeds the available converter budget before
inversions and uncomputation.

## Evidence

- Command: `python experiments/exp-057/newton_residue_screen.py`
- Result: PASS on 97,118 exhaustive GF(8) cases (weights 1–4); Newton and direct
  Lagrange interpolation had zero coefficient or root-value mismatches.
- At weight 35, the straightforward recurrence counts 2,415 variable field
  products, or 101,430T using the project's 42T multiplier cost.
- Remaining converter allowance: 36,183.74T after the v18 updates and scanner.
- The 65,246.26T overage excludes inversions and uncomputation. It is an
  operation-count estimate, not a lower bound.
- No reversible circuit, official verifier, or Kaggle submission was run.

The reproducible details and source hashes are in
[`evals/2026-11-23-exp057-newton-residue-v20.json`](../evals/2026-11-23-exp057-newton-residue-v20.json).

## Next gate

Reopen only with one exact recurrence that consumes the existing
syndrome-derived FMA state directly and fits within 36,183.74T including its
uncomputation. Do not compile the screened Newton route.
