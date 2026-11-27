---
id: plan
updated: 2026-11-27
direction: D-005
status: qv2_measured_below_gate
---

## Next experiment

Audit the QV2 source used in exp-089 for one transformation that we can
implement as our own change. The measured baseline is 317.509B; it needs an
18.16% score reduction (about 60,521 mean T at Q=889 if the measured
repetition factor holds) before another private build. Exp-069's 305.042B is
only a measurement reference: exp-056 rejects its dataset because its
generators reconstruct released KMX stages. Do not inspect, copy, or run its
code or circuits. Do not open parallel DQI branches.

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

## Not pursued

- Three non-best DQI generator profiles — higher reported cost than paired-plain; logged 2026-11-27.
- Direct port of the published complete reversible BM circuit — its width misses the limit; its `Q²T` cost is about 6.75x S-001's current conditional tie allowance (9.17x against the older exp-065 gate).
- D-005 remains closed: its proposed BM state could not be mapped to the pinned exp-063 generator; see the source-mapping receipt linked from the direction record.
