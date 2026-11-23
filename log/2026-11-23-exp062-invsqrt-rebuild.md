# 2026-11-23 — exp-062 source-built invsqrt

## Execution

- Source: `syed3000/vqcc-own-circuit-portfolio`, dataset version 17, Apache-2.0.
- Private Kaggle kernel: `accelra/exp-062-syed-v17-invsqrt`, version 4.
- Command: `kaggle kernels push -p experiments/exp-062/kernel --timeout 7200`.
- The source archive named by the dataset manifest was unavailable. The
  kernel used the published extracted source tree, restored missing compressed
  JSON inputs from their same-path JSON sources, and recorded the source and
  derived hashes. It read no `.kmb` or `.kmx` input.

## Result

The from-source build reproduced SHA-256
`70fe5f79d56bd48cd8fc9602757a0520b4d11859967627906cccb3dec25b7692`.
The unmodified official verifier passed 200,540,928 shots at Q=43 and cost
`72,440.3509518131`. Build time was 469.23 seconds; verification time was
481.13 seconds.

See the [evaluation receipt](../evals/2026-11-23-exp062-invsqrt.json),
[experiment notes](../experiments/exp-062/README.md), and raw
[Kaggle kernel log](../experiments/exp-062/kaggle_output/kernel.log).

## Decision

Keep this as the verified source-owned invsqrt member. Do not submit it alone:
the competition requires a three-task archive, and this experiment did not
build or verify a complete `invsqrt` + `dqi` + `dfthcsos` portfolio.
