---
id: plan
updated: 2026-11-28
direction: D-005
status: qv2_and_chemistry_rank99_screens_closed_no_gate
---

## Next experiment

The exp-090 audit closed the current public-lead route. The measured QV2
baseline is 317.509B; even zero observed errors at the same cost would be
313.736B, still 20.68% above the current DQI tie gate. Do not launch another
private kernel until a new algorithmic construction or source-level
transformation has an explicit resource screen that can plausibly clear the
roughly 18% reduction. Exp-069's 305.042B is only a measurement reference:
exp-056 rejects its dataset because its generators reconstruct released KMX
stages. Do not inspect, copy, or run its code or circuits. Do not open
parallel DQI branches.

Exp-091 also closed the cheap chemistry rank-99 matrix-pencil route: the
tracked V22 payload has 1,281 unique product terms across ten custom loaders,
and 128 seeded output-slice trials found no invertible slice for any loader.
This is not a tensor-rank lower bound; an explicit decomposition is required
before a chemistry kernel is justified.

## Current gate

- Exp-089 rebuilt QV2 exactly and passed the official verifier, but its score
  is 22.19% above the refreshed tie gate. The S-001 substitution projection is
  `32.42186`, not a Kaggle score.
- Exp-069 measured `305.042B` with zero observed errors, but exp-056 rejects
  its dataset; it is not an eligible source or optimization base. Its
  `32.85767` S-001 substitution projection is measurement-only.
- The current live rank-1 gate is derived from the 2026-11-27 15:36 UTC
  leaderboard snapshot. A future candidate needs a credible resource screen
  before another private build, then official verification at three salts and
  a refreshed leaderboard before a submission proposal.
- Exp-090 audited the public QV2Beat and zero-test-cut leads; neither clears
  the source-owned gate. See
  [the audit receipt](../evals/2026-11-27-exp090-public-lead-audit.json).

## Not pursued

- Three non-best DQI generator profiles — higher reported cost than paired-plain; logged 2026-11-27.
- Direct port of the published complete reversible BM circuit — its width misses the limit; its `Q²T` cost is about 6.75x S-001's current conditional tie allowance (9.17x against the older exp-065 gate).
- D-005 remains closed: its proposed BM state could not be mapped to the pinned exp-063 generator; see the source-mapping receipt linked from the direction record.
