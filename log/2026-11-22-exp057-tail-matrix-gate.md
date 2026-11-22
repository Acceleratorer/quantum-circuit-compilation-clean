# 2026-11-22 — exp-057 precomputed-matrix action gate

Private Kaggle kernel `accelra/exp057-streaming-prefix-state`, version 5,
completed the source-owned one-symbol matrix-action screen. It compiled 873
qubits and 84 Toffoli-like gates. All 64 invertible-matrix cases matched the
expected outputs; the 70 payload words, rank, and pivot were preserved, with
zero dirty scratch qubits and zero phase flips.

This cell receives all four matrix entries as inputs. Matrix generation from
the compact prefix, generation-workspace cleanup, in-place use across the 66
remaining symbols, and the official verifier are not covered. The projected
`84T × 66` cost may overlap the existing FMA projection and is not an added
measured cost.

The screen was built from
[`build_private_kernel.py`](../experiments/exp-057/build_private_kernel.py)
and [`streaming_prefix_kernel.py`](../experiments/exp-057/streaming_prefix_kernel.py).
Source hashes and the complete receipt are in
[`the evaluation record`](../evals/2026-11-22-exp057-tail-matrix-gate.json);
the raw Kaggle output is retained in local staging. The next gate is to build
and erase the four matrix entries from the compact prefix state, then measure
that cell with the prefix gate before attempting the complete 66-symbol
schedule.
