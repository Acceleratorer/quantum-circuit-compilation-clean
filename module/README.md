# Reusable modules

The repository keeps reusable generators under `src/`. This directory is the small operational layer for packaging, hashing, and preflight checks that should stay independent from any one experiment.

Current module boundary:

- `src/dqi/` — DQI generator and experiments.
- `src/invsqrt/` — inverse-square-root generator.
- `src/angleload/` — chemistry angle-loader helpers.
- `tests/test_submission_receipt.py` — receipt invariant check.

Large compiled circuits remain local and are referenced by SHA-256 receipts.
