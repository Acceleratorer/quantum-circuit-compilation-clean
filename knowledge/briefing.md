---
id: briefing
updated: 2026-11-27
---

# Competition status

## Where we stand

| Task | Our best source-owned cost | Live frontier / target | Status |
|---|---:|---:|---|
| Invsqrt | 62,993.51 (exp-085) | Fixed in S-001 projection | Rebuilt and official-verifier clean |
| DQI | 356,677.49 mean T (exp-063, Q=890) | <=279,171.55 mean T to tie | 21.73% reduction still needed |
| Chemistry | 249,853,852.96 (exp-074) | Fixed in S-001 projection | Source-built and verifier clean |
| Portfolio | 31.79818 projected (S-001) | Live leader 34.50408 | Not submitted; projection only |

## What changed

- The 2026-11-27 leaderboard snapshot puts Accelra at rank 889 with a best
  public score of 33.17067; its latest submission scored 33.08801. The best
  score is a public reproduction, outside our source-owned target. Rank 1 is
  34.50408, and Kaggle lists the deadline as 2027-01-20 23:59
  ([full snapshot and receipt](../evals/2026-11-27-live-leaderboard-045600Z.json)).
- The public DQI profile screen found `paired-plain` already best among the
  four published profiles. Re-running the other three cannot close the gap.
- D-005 is closed before a kernel: its `109,515` return-stage count came from
  a measurement-only dataset, and the pinned exp-063 builder screen did not
  identify a corresponding BM state or stage. See the
  [source-mapping receipt](../evals/2026-11-27-d005-source-mapping.json).
- The full released reversible BM circuit is not a candidate at its published
  `Q=1,837`, `442,397T` (`lit-reversible-bm-fit`).

## Current focus

- No experiment is queued. Select the next source-owned construction only
  after it has an identified state and a credible estimate against
  `Q<=890`, `T<=273,588.12`.

## Worth reading

- [D-005 proposal](directions/D-005-width-preserving-bm-history.md) — the
  bounded next step and its kill gate.
- [Reversible BM paper note](../literature/papers/lit-reversible-bm-fit.md) —
  the algorithmic invariant and why its published circuit is too large.
- [S-001 evaluation](../evals/2026-11-27-exp085-v20-portfolio.json) — exact
  component receipts and the current score projection.
