---
date: 2026-11-27
title: D-005 source mapping screen
status: no_go_source_mapping
---

# D-005 source mapping screen

The proposed `decoder_return` cost of `109,515` came from the Tony Li profile
in `evals/2026-11-26-dqi-stage-profile.json`. Exp-056 classifies that source as
measurement-only, so this is not an exp-063 cost measurement.

I downloaded only three files from Syed's Apache-2.0 dataset v17 and read them
as text. Their hashes match the exp-063 package pin or source manifest. The
emitter selects the D70 Lane B builder and its shear, quotient, norm-handoff,
elliptic-tensor, and converter operations. This screen found no mapped BM
state or matching `decoder_return` stage. The mean return cost and complete
resource projection therefore remain unmeasured.

**Decision:** close D-005 before a private kernel. No submission was made.
This rejects the proposed mapping, not every possible BM redesign. See the
[evaluation receipt](../evals/2026-11-27-d005-source-mapping.json).
