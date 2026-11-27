---
id: exp-085
title: Source-build the v155 inverse-square-root component
task: invsqrt
status: candidate_integrity_pass_hash_approval_pending
date: 2026-11-27
result: Rebuilt the pinned v155 generator with an exact output hash match and PASS evidence. Combined archive SHA-256 acad50cc8e1e059655ad0f0f7753ae1c9760ce694d508980644722ff9871152d; projected verifier GM 31.79818, not a Kaggle score.
---

# exp-085 — source-built v155 inverse-square-root

## Result

Private Kaggle kernel accelra/exp-085-v155-source-built-invsqrt completed
version 2. The build took 668.32 seconds and reproduced circuit SHA-256
b4ba2126a1ac435af2ab4e8e8394eb79bdf9dfae1ccb2aad06e5fad177e47608.
The rebuilt circuit has two published official verifier PASS results at
39 qubits and 200,540,928 shots each, with scores 62,993.51131 and
62,993.49991. The build receipt is in receipts/source-build-v2.json.

The private kernel ran with internet disabled. Its wrapper pins VERIFY=0 and
S5LEND=1, removes SSH-agent variables, checks the source archive hash, and
refuses to use the released compiled circuit as a build input.

## Candidate portfolio

Proposal S-001 combines this Invsqrt circuit with the source-built exp-065 DQI
and the source-built V20 chemistry component from exp-074. The deterministic
18-member archive passed member-hash and CRC checks. Its SHA-256 is
acad50cc8e1e059655ad0f0f7753ae1c9760ce694d508980644722ff9871152d; the
integrity receipt is in receipts/archive-integrity.json.

The component receipts give a local verifier geometric-mean projection of
31.79818. This is not a Kaggle score. The live leader read on 2026-11-27 is
34.50408, so the projection is 2.70590 points short. The current DQI component
would need to fall from 356,677.49 to about 279,171.55 mean Toffolis at Q=890
to tie that leader with the other components fixed.

## Provenance

The source archive is the Apache-2.0 dataset
dziyanavalenta/q2026-v155-isr-generator. Its pinned file is
isr_source_targz.bin, SHA-256
5d34399e677402091cd18505637c88711dcce9a64ad66e594f1dd1e8651ef405.
The dataset's complete LICENSES directory is preserved under licenses/.
See source.json and NOTICE.md for attribution and lineage.

No generated circuit binaries or candidate ZIPs are committed. Proposal S-001
is staged locally at submissions/S-001.zip and awaits the exact-hash file
required by approvals/README.md before a Kaggle submission.
