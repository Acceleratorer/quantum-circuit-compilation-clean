---
id: exp-066
title: Rebuild the licensed 32.85306 source portfolio with verified DQI gate cuts
task: dqi
status: in_progress
date: 2026-11-25
---

# exp-066 — source-built DQI gate rewrites

This candidate rebuilds the 18-file portfolio from Tony Li's Apache-2.0
generator dataset, then applies the ten published DQI gate rewrites to the
generated DQI assembly and recompiles it. The base source DQI is pinned at
`4b572141…`; the rewritten output is expected to match `6f78ecdd…`.

The kernel input is explicitly pinned to dataset version `2`; its mounted
version is also checked by the 88-file fingerprint
`50be321af83901e46476b55c7b1faedf60510f971abc495c02aa41f8c9b87e42` and the
hash of `expected_sha256.json`. The build reads no public compiled circuit as
input. The generator dataset's `notices/RELEASE_NOTICES.txt` credits the
underlying Team ThemBones work and earlier contributors. The ten DQI edits are
credited separately in [UPSTREAM.md](UPSTREAM.md).

## Current gate

Build and run all three unmodified official verifiers in the private Kaggle
kernel defined in `kernel/`. If all pass, the resulting `submission.zip` is a
complete candidate and may be submitted for a real score. The base source
portfolio scored `32.85306`; rank 1 is currently `34.25544`.

The build and verifier receipts will be linked here after the kernel finishes.
