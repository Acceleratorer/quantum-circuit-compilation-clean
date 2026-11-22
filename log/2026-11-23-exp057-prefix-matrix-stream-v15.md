# 2026-11-23 — exp-057 integrated prefix and matrix stream, v15

Private Kaggle kernel v15 composed the compact-prefix decoder, point-4 matrix
setup, and the full 66-symbol tail stream. It measured `Q=889`, `T=19,004`.

Across 32 cases covering both prefix pivots (`a0`: 31, `a1`: 1), the matrix,
tags, and checksum matched the classical reference. All 66 tail words were
preserved, 12 scratch qubits were clean, and no phase flips were detected.
The stream stores `K=D/b1` in the fourth matrix word and reconstructs the
`D` contribution as `K*b1` at each point. The rank register is reused as
workspace to keep the width below 890.

## Verification

- Private Kaggle `run_screen()` completed, including v15's integrated screen.
- Local tests: `..\\..\\.venv\\Scripts\\python.exe -m unittest discover -s tests -p 'test_exp057_tail*.py' -v`
  passed all 3 tests; `py_compile` and `git diff --check` passed.
- Kaggle CLI: pushed private kernel
  `accelra/exp057-streaming-prefix-state`, version 15; status `COMPLETE`.
- Output log SHA-256:
  `A8C77B81625F2E560EAB2B20D75FD7FEE22AA894475F9E3F4FDF0FFE77D57A6E`.
- [Raw Kaggle output](../experiments/exp-057/kaggle-v15-output.log).
- Full receipt: [v15 evaluation](../evals/2026-11-23-exp057-prefix-matrix-stream-v15.json).

## Scope and next gate

This is a checksum resource screen, not a complete DQI circuit. It reuses the
rank register and does not restore the prefix/matrix state, construct the DQI
phase/output, or run the official verifier. No competition submission was
made. Next, connect the per-symbol results to the actual DQI output/phase and
measure reversible cleanup before invoking the official verifier.
