# 2026-11-22 — exp-057 coefficient-derived tail action

Private Kaggle kernel version 6 measured the one-symbol tail action after
deriving its matrix from four supplied polynomial coefficients. Across 64
cases at point 4, it compiled `Q=889`, `T=822`, preserved the 70-word payload,
rank, and pivot, left all 16 scratch qubits clean, and had zero output errors
or phase flips.

The same run repeated the prefix gate (`Q=885`, `T=7,483`) and the
precomputed-matrix action (`Q=873`, `T=84`). Those are separate cells; their
costs are not a measured integrated schedule.

This cell still receives the coefficients directly. It does not generate
them from the compact prefix state, amortize its setup over later symbols,
cover the 66-symbol schedule, or run the official verifier. The next gate is
to separate reusable coefficient-dependent setup from the per-symbol action,
then measure that setup from the compact state with clean workspace.

Receipt: [exp-057 coefficient-derived tail action](../evals/2026-11-22-exp057-tail-bezout-action.json).
Raw Kaggle output is retained in ignored local staging.
