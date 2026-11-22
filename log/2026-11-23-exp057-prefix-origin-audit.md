# 2026-11-23 — exp-057 prefix origin support audit

## Result

On a fixed comparison across discovery and holdout samples, prefix origin 24
had 55 unsupported four-point shapes in 49,152 shots; origin 0 had 75. That is
0.112% versus 0.153%. The discovery scan's best origin varied by seed (8, 20,
32), so origin 24 was not a universal best.

The script uses the official DQI weight probabilities and the official
70-syndrome-to-FMA map. It checks 17 non-overlapping prefix blocks at origins
0, 4, …, 64 on three discovery seeds, then compares only origins 0 and 24 on
three fresh holdout seeds. The direct FMA map matched the reference, and 40
scalar decoder cases per origin and seed matched the vectorized classification.

## Decision

Do not change the integrated circuit from this result alone. The reported
repetition overhead is a plug-in estimate that treats unsupported shapes as
final failures; no quantum circuit or official verifier ran. Moving the prefix
also requires coordinated changes to the reversible four-sample decoder and
the 66 tail actions, which currently use points 0–3 and 4–69. Keep origin 0
while completing the full output, phase, and cleanup path; revisit origin 24
only when that path can be measured end to end.

Evidence: [machine-readable receipt](../evals/2026-11-23-exp057-prefix-origin-audit.json),
[audit script](../experiments/exp-057/prefix_support_audit.py).
