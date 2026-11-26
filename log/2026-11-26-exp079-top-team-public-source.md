---
date: 2026-11-26
title: Current top team's public source check
status: no_go_identify_current_top_source
---

# exp-079 — Current top team's public source check

The live Kaggle CLI leaderboard shows **Cat with 2 Qubits** at `34.50408`.
I checked the competition's public kernel listing and the four handles listed
for that team. The checked accounts' public kernels last ran on November 20;
none is tied to the team's November 26 result. This does not rule out reuse of
an older kernel or an unpublished source.

The downloaded notebook is only a packaging wrapper for a prebuilt submission
archive and three generator archives. It describes an existing ThemBones/Syed
invsqrt lineage and a Syed v12 DQI lineage. It contains no two-qubit inverse
square-root design. The notebook was read as untrusted text and never executed;
its SHA-256 and provenance are in
[`evals/2026-11-26-exp079-top-team-public-source.json`](../evals/2026-11-26-exp079-top-team-public-source.json).

**Decision:** this source check does not reveal the current leader's method.
The inspected packaging notebook is not itself the 2-qubit breakthrough; the
next high-upside work stays on a source-owned algorithm change with a measurable
route toward the score-equivalent gate.
