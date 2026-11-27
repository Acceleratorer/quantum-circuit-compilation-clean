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

- The public DQI profile screen found `paired-plain` already best among the
  four published profiles. Re-running the other three cannot close the gap.
- The full released reversible BM circuit is not a candidate at its published
  `Q=1,837`, `442,397T`; only its shared-update/history-recovery invariant
  remains a possible, untested adaptation (`lit-reversible-bm-fit`).

## Open decision

- Approve or reject D-005, a one-day maximum local resource screen. It stops
  before a private kernel unless the complete estimate reaches `Q<=890` and
  saves at least `83,089T` (2% below the tie gate) with phase and cleanup
  included.

## Worth reading

- [D-005 proposal](directions/D-005-width-preserving-bm-history.md) — the
  bounded next step and its kill gate.
- [Reversible BM paper note](../literature/papers/lit-reversible-bm-fit.md) —
  the algorithmic invariant and why its published circuit is too large.
- [S-001 evaluation](../evals/2026-11-27-exp085-v20-portfolio.json) — exact
  component receipts and the current score projection.
