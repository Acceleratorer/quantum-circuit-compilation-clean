---
id: exp-048
title: Static audit of the claimed 25% DQI rewrite
task: dqi
tests: static notebook and metadata inspection; no code or circuit executed
direction: D-004
status: negative_result
date: 2026-11-19
result: the notebook presents a mechanical-rewrite audit, not a cheaper decoder; it leaves a different key-equation algorithm as the only plausible route
---

# Static audit of the claimed 25% DQI rewrite

## Finding

The public notebook title is easy to misread. It documents five failed attempts
to remove 25% of the Toffolis from a reference DQI circuit; it does not provide
a 25%-cheaper circuit or generator. Its author reports a 367,993 static-Toffoli
circuit, 367,118 mean executed Toffolis, and 890 qubits. The reported rewrite
routes save at most 875 of 367,993 Toffolis (0.24%). The remaining proposed
route is a different key-equation algorithm.

The notebook's `submission` section verifies and copies a public circuit bundle
into `submission.zip`. That conflicts with this project's source-owned-generator
gate. The notebook and its submission code were inspected as text only; the
bundle was not downloaded, its code was not run, and no circuit was copied.

For the current local rank-1 target, the saved score model gives
`R × Q² × T <= 245.285e9`. At `R=1.1912605` and `Q=890`, that requires
`T <= 259,947`, about 29% below the notebook's reference circuit. Treat this
as a screening target, not a score prediction for the notebook's bundle.

The notebook's high-level conclusion agrees with the completed BM screens:
stop trying mechanical rewrites and low-degree packed-state feedback formulas.
Any next DQI work must change the key-equation algorithm and pass a reversible
resource count before circuit generation. The paper's fast modular approach is
one literature candidate, but its field-multiplication and qubit counts for
this 70-symbol instance have not been established.

## Provenance

- Kaggle source: [varianceofx's notebook](https://www.kaggle.com/code/varianceofx/a-25-cheaper-dqi-decoder-is-not-a-rewrite), kernel ID `145743784`.
- Pulled on 2026-11-19. Kaggle's pull metadata did not expose a version number; the notebook ID and hashes below pin the inspected content.
- Notebook SHA-256: `1bc6ae1b401c21a4878f3eaecf0e4b20da900fe16b09e1160e334b8171e5d67e`.
- Metadata SHA-256: `2ef661d6fd6e6c05efa96ae5b22f7a1450f508a3ddf4f434d9cc919dde2653fa`.
- Related paper: [New Decoding of Reed–Solomon Codes Based on FFT and Modular Approach](https://arxiv.org/abs/2207.11079).
