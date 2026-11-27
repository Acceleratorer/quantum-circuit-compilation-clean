---
id: D-005
title: Test width-preserving BM history recovery for source-owned DQI
decision: close
status: closed_no_go
tasks: [dqi, all]
claims: [C-001]
date: 2026-11-27
---

## What are we trying to do?

Lower the source-owned DQI mean Toffoli enough to move the current portfolio
from a 31.79818 projection to the live leader at 34.50408, while keeping
`Q <= 890`, exact outputs, correct phase, and clean scratch.

## How is it done today?

Exp-063's paired-plain DQI is source-built and official-verifier clean at
`Q=890`, mean `356,677.49T`. With v155 Invsqrt and V20 chemistry fixed, a tie
requires `T <= 279,171.55`, a `21.73%` reduction. The public four-profile
screen is closed in the 2026-11-27 DQI log.

## What's new in our approach?

Test whether the shared reversible BM update and discrepancy-recovery
invariant from `lit-reversible-bm-fit` can replace enough of exp-063's
`decoder_return` work without importing the paper's high-width architecture.
The stage profile counts `109,515` static Toffoli-like gates there; reaching
the target would require `77,506` mean-T savings, about 70.8% of that static
count. Static and mean counts are not interchangeable. The paper's separate
reverse-BM stage costs `86,176T`, but that cross-design number is not a
prediction for exp-063.

## Options

1. **Recommended — bounded local resource screen.** Measure the exp-063
   `decoder_return` stage's actual mean cost, map the invariant onto its
   state and return path, then produce a complete width and Toffoli estimate.
   No private kernel unless the full projection is at most `273,588.12T` at
   `Q<=890`—a 2% cost buffer below the current `279,171.55T` tie gate—with
   output, phase, and cleanup accounted for.
2. **Do not reopen DQI now.** Keep the verified S-001 archive as a
   below-leader learning candidate and wait for a better source-owned lead.
   This avoids further compute but has no path to top-1 today.

The strongest argument against option 1 is that the released complete BM
circuit is `442,397T` at `Q=1,837`; its `Q²T` cost is about `6.75x` S-001's
current conditional tie allowance (or `9.17x` against the older exp-065
eligible-score gate). Its history invariant alone may not transfer to exp-063
or save enough once reverse cleanup is counted.

**Critic dissent (light review):** `109,515` is a static stage count, not its
mean contribution; a top-20 team would first measure the actual return stage
with HMR-conditioned gates accounted for. **Response:** that measurement is
the first screen, and the 2% pre-kernel margin plus three-salt final check
guard against a fragile estimate.

## Expected score impact

The tie gate is `279,171.55T`; the screen uses a 2% lower-cost buffer at
`273,588.12T`. At fixed width and other component costs, this projects to
`34.737`, about `0.233` above the current leader. The required saving is
`83,089T`, or `23.30%` of exp-063's mean; that is 75.9% of the return stage's
static count, not a mean-cost attribution. Use a subjective `5–15%` success
range for ranking only: it is uncalibrated, reflecting this demanding stage
reduction and the published circuit's poor width/cost fit. If success only
reaches the buffered projection and failure changes nothing, that range
implies `0.147–0.441` expected score points; leaderboard movement is unknown.
These expected points are relative to S-001's `31.79818` projection; the
`0.233` lead over today's rank 1 is a separate conditional margin.
The first screen can stop this direction before a full circuit build.

## Risks and kill criteria

Kill if the complete resource estimate misses either the `Q<=890` width limit
or the `83,089T` savings target, or if the invariant cannot be applied to the
valid DQI input domain without retaining extra syndrome/history state.

## Cost

One local semantic/resource screen, estimated at up to one workday. A private
Kaggle build and official verification are a separate follow-up and require
the screen to clear both gates.

## Midterm check

The first screen must identify the exact exp-063 state being replaced, prove
the forward/reverse map on verifier-form syndromes, measure the target stage's
mean cost on representative inputs, account for HMR-conditioned gates and
every cleanup action, and project at least a 2% margin below the refreshed
tie gate.

## Final check

Either reject C-001 with a reproducible lower-bound/resource receipt, or
produce a source-owned circuit at `Q<=890`, at least 2% below the refreshed
tie gate, and with zero errors across at least three official-verifier salts
before assembling a new proposal.

## Critic review

Light review complete on 2026-11-27; see the dissent and response in Options.

## 2026-11-27 source-mapping result

**No-go for D-005 as proposed.** Its `109,515` return-stage count comes from
`evals/2026-11-26-dqi-stage-profile.json`, whose Tony Li source is marked
measurement-only under exp-056. It is not an exp-063 cost measurement.

I read the pinned exp-063 v17 `emit.py`, `d70_laneB_builder.py`, and
`d70_laneB_upgrades.py` as text only. Their hashes match the exp-063 pin and
source manifest. The emitter selects the D70 Lane B builder, which composes
shear, quotient, norm-handoff, elliptic-tensor, and converter operations.
This screen did not identify a Berlekamp–Massey state or a corresponding
`decoder_return` stage in that generator. Therefore it cannot estimate an
eligible return-stage mean or support the `Q<=890`, `T<=273,588.12` gate.

No private kernel or submission was made. This closes the proposed mapping;
it does not prove that every new BM-based DQI construction is impossible.
The source hashes and scope limit are in
[`evals/2026-11-27-d005-source-mapping.json`](../../evals/2026-11-27-d005-source-mapping.json).
