---
id: plan
updated: 2026-11-27
direction: D-005
status: closed_no_go
---

## Next experiments

None is queued. D-005 was closed before a kernel because its proposed BM state
could not be mapped to the pinned exp-063 generator; see the source-mapping
receipt linked from the direction record.

## Current gate

- No private kernel is running. A new DQI direction needs an eligible,
  source-level path to `Q<=890` and mean `T<=273,588.12` before a build.
- Any candidate still needs the official verifier at three salts and a
  refreshed leaderboard before a submission proposal.

## Not pursued

- Three non-best DQI generator profiles — higher reported cost than paired-plain; logged 2026-11-27.
- Direct port of the published complete reversible BM circuit — its width misses the limit; its `Q²T` cost is about 6.75x S-001's current conditional tie allowance (9.17x against the older exp-065 gate).
- Full private rebuild before a resource screen — no evidence yet that the required 83,089T savings fit at `Q<=890` with a 2% buffer.
