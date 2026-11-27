---
id: plan
updated: 2026-11-27
direction: D-005
---

## Next experiments

| # | Claim | What it tests | Expected gain | Cost | Why now |
|---|---|---|---|---|---|
| 1 | C-001 | Measure and target exp-063's `decoder_return` with BM history recovery | 5–15% subjective success range; 0.147–0.441 expected points versus S-001 projection | Up to one workday | Only unresolved source-owned route with a plausible savings term near the gate |

## Waiting on

- User approval of proposed direction D-005. No experiment or kernel is running.
- A passed screen must project `T<=273,588.12` at `Q<=890`; a candidate then needs the full verifier at three salts and a refreshed leaderboard before a submission proposal.

## Not pursued

- Three non-best DQI generator profiles — higher reported cost than paired-plain; logged 2026-11-27.
- Direct port of the published complete reversible BM circuit — its width misses the limit; its `Q²T` cost is about 6.75x S-001's current conditional tie allowance (9.17x against the older exp-065 gate).
- Full private rebuild before a resource screen — no evidence yet that the required 83,089T savings fit at `Q<=890` with a 2% buffer.
