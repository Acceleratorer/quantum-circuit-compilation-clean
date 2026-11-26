# 2026-11-26 — exp-057 root-conditioned Forney phase gate

## Result

Private Kaggle kernel version 23 completed. It tested all denominator roots in
one seeded weight-31 and one seeded weight-35 verifier-shaped case (66 root
positions in their union).

| Weight | Phase | Input restore | Scratch | Q | Added simulator-counted T |
| ---: | --- | ---: | --- | ---: | ---: |
| 31 | 0 expected, 1 observed | 0 errors | dirty | 892 | 573,144 |
| 35 | 1 expected, 1 observed | 0 errors | dirty | 892 | 573,144 |

The remaining score-equivalent allowance is 34,837.57 T at Q=900. This gate
adds 16.45 times that allowance before the full scan, misses the 890-qubit
screen by two qubits, leaves scratch dirty, and has one phase mismatch. The
root-conditioned derivative correction is a no-go; do not integrate or
submit it.

## Method and limits

At a simple root beta, the FMA numerator is `omega(beta) * padding(beta)` and
the derivative of the denominator is `sigma_prime(beta) * padding(beta)`, so
their quotient supplies the needed error residue. The circuit applies this
correction only to the union of tested denominator roots. The compiled
controlled arithmetic remains in the measured gate count; the two cases report
the same T count despite different root weights.

This is a narrow phase gate only. It does not cover the full 4095-position
scan, sample-node branch, integrated decoder, official verifier, or submission.

## Reproduction

- Private kernel: [version 23](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/23)
- Push: `kaggle kernels push -p tmp/github_publish/tmp/exp057-root-conditioned-v23`
- Status: `kaggle kernels status accelra/exp057-streaming-prefix-state`
- Receipt: [evaluation](../evals/2026-11-26-exp057-root-conditioned-phase-gate.json)
- Raw script and output log: `experiments/exp-057/out/kaggle-v23/` (ignored)
