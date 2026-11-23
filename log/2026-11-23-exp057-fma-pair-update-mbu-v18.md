# 2026-11-23 — exp-057 MBU FMA pair update, v18

Private Kaggle kernel v18 measures the existing normalized FMA pair update
with measurement-based uncomputation (MBU) for the product workspace. Across
64 seeded cases (32 per swap branch), outputs matched, the ratio and branch
were preserved, 13 scratch qubits were clean, and there were no phase flips.
The cell measured `Q=50`, `T=54`.

This improves v17's isolated `210T` cell to `54T`. Across 2,415 pair updates,
the measured subtotal is `130,410T`, matching the existing ledger's `42T`
product plus `12T` controlled swap per update. The prior full-DQI projection
of `202,075T` already includes that subtotal and `71,665T` of other estimated
work, leaving only `10,035.59T` under the current `212,110.59T` gate. The
projection still omits unmeasured integration, width, DQI output/phase,
cleanup, and official verification; v18 does not create `81,700T` of new
headroom or establish a candidate.

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
