# 2026-11-23 — exp-057 MBU FMA pair update, v18

Private Kaggle kernel v18 measures the existing normalized FMA pair update
with measurement-based uncomputation (MBU) for the product workspace. Across
64 seeded cases (32 per swap branch), outputs matched, the ratio and branch
were preserved, 13 scratch qubits were clean, and there were no phase flips.
The cell measured `Q=50`, `T=54`.

This improves on v17's `210T` cell. The exp-053 recurrence ledger contains
2,415 pair updates, so repeating this component gives `130,410T`, leaving
`81,700.59T` under the current full DQI gate of `212,110.59T`. This is only a
component sum: each cell receives its ratio and branch as inputs, and the
ratio generation, complete schedule, DQI output/phase, cleanup, and official
verifier are not included. It does not establish a candidate.

## Verification

- Private Kaggle kernel `accelra/exp057-streaming-prefix-state`, version 18:
  `COMPLETE`.
- Source SHA-256:
  `ADD41F6806CEAD8151C73DDFB91DCED98F3DC882C9CDD3479D499A90A073BA61`.
- Submitted script SHA-256:
  `CBDCDAA2BD092669ADAC76D9306968F7EFBAFF8E43EC4BF4C477B4AAF44E1BC6`.
- Raw log SHA-256:
  `08D8ECA3320A7721D53BFE8DDBF063A7AC0BC69292651F0356DF41A4773C384E`.
- [Kernel v18](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/18),
  [evaluation receipt](../evals/2026-11-23-exp057-fma-pair-update-mbu-v18.json),
  and [raw output](../experiments/exp-057/kaggle-v18-output.log).

## Next gate

Compose ratio generation with the 70-symbol recurrence and this MBU update in
one source-owned circuit. Measure full `Q`, `T`, DQI phase/output, and clean
workspace. Continue only if the integrated schedule stays within the complete
resource gate; otherwise close this route. No new algorithm branch is opened
by this component result.
