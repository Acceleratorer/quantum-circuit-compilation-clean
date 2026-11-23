# 2026-11-23 — exp-057 CONVERT cost split

Tagged circuit counts split the v19 path into forward `CONVERT` at `69,220T`,
scan at `44,275T`, and reverse `CONVERT` at `70,342T`. The scan count is
`45,045T` for all 4,095 points minus 11T for each of the 70 skipped points.
The three parts sum to the v19 measured `183,837T` exactly.

Skipping reverse `CONVERT` alone is a no-go. Even assuming a zero-cost direct
FMA uncompute, the forward converter, scan, and v18's repeated pair updates
total `243,905T`. A fresh Kaggle CLI check at 06:12 UTC found the leader at
`33.90122` and our latest scored submission at `28.14028`, tightening the
score-equivalent gate to `210,868.74T`. The optimistic path is now
`33,036.26T` over that gate before integration, DQI output/phase, or cleanup.
The v18 update subtotal alone would need a 25.33% reduction. The existing
unsynthesis expects the original FMA output coordinates, so applying it to the
converted state is not a valid uncompute. We did not build that composition.

The v19 control still passes with a canonical DQI residue pair, while direct
use of the padded FMA pair still fails phase. This closes the
"remove only reverse CONVERT" route. A future DQI attempt needs a lower-cost
integrated schedule or a different scan-ready output map. See the
[evaluation receipt](../evals/2026-11-23-exp057-convert-cost-split.json) and
[reproducible converter count](../experiments/exp-057/convert_cost_split.py).
