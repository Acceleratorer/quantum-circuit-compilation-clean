---
date: 2026-11-26
title: GF(2^12) 78-AND multiplier screen
status: no_go_before_build
---

# exp-078 — GF(2^12) 78-AND multiplier screen

## Finding

[Swapnil Jain's circuit repository](https://github.com/Swapnil-jain/gf2m-circuits)
publishes `multipliers/circuits/final_f12.slp` as a 210-gate GF(2^12)
multiplier over polynomial `0x1009`. Counting the source gives 78 AND gates and
132 XOR gates. The repository licenses its code and circuits under
Apache-2.0; the papers are CC BY 4.0.

This is not a credible drop-in improvement for the DQI. Prior analysis of an
older public decoder identified a generic 12×12 multiplier costing 42
Toffolis (`experiments/exp-005`). That is not a fresh count for the active
source, but it makes a 78-AND circuit a poor port candidate before accounting
for reversible cleanup. The active source's D16 substitutions are custom
bilinear maps, not general field multiplication; all four currently account
for only 850 static Toffoli-like gates. Removing that entire cost could not
close the 37,388.65 mean-Toffoli gap to the current leader tie gate.

The field polynomial also differs from the `0x1053` modulus used in prior DQI
analysis. A linear basis conversion is possible in principle, but does not
reduce the candidate's nonlinear gate count.

## Decision

No port, circuit build, verifier run, or submission. Close this multiplier
lead before implementation. A future DQI candidate must target the active
source directly and show a plausible path to at least 37,389 mean-Toffoli
savings before a full verifier run.

Numbers and scope are recorded in
[`evals/2026-11-26-exp078-gf2m-78and-screen.json`](../evals/2026-11-26-exp078-gf2m-78and-screen.json).
