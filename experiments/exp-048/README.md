---
id: exp-048
title: Static audit of the claimed 25% DQI rewrite
task: dqi
tests: static notebook, paper-table, and scan-source inspection; no code or circuit executed
direction: D-004
status: negative_result
date: 2026-11-19
result: the claimed rewrite is not cheaper; the 70-symbol FMA candidate has no demonstrated Toffoli or qubit advantage
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

## Fast modular approach gate at 70 symbols

The paper recommends its frequency-domain modular approach (FDMA) for short
codes and its fast modular approach (FMA) for medium or long codes. The
published FDMA comparisons closest to this 70-symbol instance use parity
lengths 32 and 128. Their key-equation multiplication counts are nearly the
same as reformulated BM: 3,233 vs. 3,136 at 32, and 49,921 vs. 49,408 at 128.
The FMA's larger advantage is reported at parity length 512 (239,616 vs.
787,456), outside this instance's size. These are classical field-operation
counts, not Toffoli or reversible-circuit counts; they do not show a useful
key-equation product reduction at length 70.

The local DQI scan has a separate Toffoli cost: it checks the 12-bit value
`B(β)` for zero at each of 4,095 points, using an 11-workspace-bit zero ladder
(`src/dqi/pro_q2_897/exp/scan/scan.py` and `exp/decoder/common.py`). Its recorded
cost is 45,045 Toffolis. The scan's polynomial evaluation uses fixed field
constants, which are linear maps; reducing their classical field-multiply
count does not remove the zero checks. The paper does not give a reversible
schedule or peak-qubit count for this 70-symbol case.

**Gate result:** do not build a direct FDMA/FMA replacement from the paper's
classical counts. It has not shown the required `Q ≤ 890` and complete
forward/phase/uncompute `T ≤ 259,947`, nor a path to the score target. Revisit
only with a concrete reversible design that changes the zero-test or dynamic
key-equation cost.

Source: Tang and Han, [*New Decoding of Reed–Solomon Codes Based on FFT and
Modular Approach*](https://arxiv.org/abs/2207.11079), §IV-A, Tables I–III.

## Provenance

- Kaggle source: [varianceofx's notebook](https://www.kaggle.com/code/varianceofx/a-25-cheaper-dqi-decoder-is-not-a-rewrite), kernel ID `145743784`.
- Pulled on 2026-11-19. Kaggle's pull metadata did not expose a version number; the notebook ID and hashes below pin the inspected content.
- Notebook SHA-256: `1bc6ae1b401c21a4878f3eaecf0e4b20da900fe16b09e1160e334b8171e5d67e`.
- Metadata SHA-256: `2ef661d6fd6e6c05efa96ae5b22f7a1450f508a3ddf4f434d9cc919dde2653fa`.
- Related paper: [New Decoding of Reed–Solomon Codes Based on FFT and Modular Approach](https://arxiv.org/abs/2207.11079).
