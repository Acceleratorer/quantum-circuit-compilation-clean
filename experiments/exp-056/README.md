---
id: exp-056
title: Public-source candidate provenance screen
task: all
tests: static inspection only; no downloaded code executed
direction: D-004
status: source_dataset_rejected
date: 2026-11-21
result: 32.85306 generators reconstruct released circuits from recovered KMX; provenance reference only.
---

# exp-056: public-source candidate screen

## Decision

This was a static provenance screen, not a circuit build. Notebook and dataset
files under `external/` were read as JSON/text only. No downloaded notebook or
generator was executed, no external circuit was copied into `src/`, and no
submission was made. The exact local file inventory and SHA-256 digests are in
[`provenance-manifest.json`](provenance-manifest.json); raw downloads stay in
the ignored `external/` directory. The Kaggle metadata returned here omitted
numeric source revisions; the manifest records that gap explicitly instead of
guessing.

| Public item | Static finding | Decision |
|---|---|---|
| [Maoxin, 33.135 chemistry loaders](https://www.kaggle.com/code/maoxin123/qcc-33-135-3-375-toffoli-chemistry-loaders) | Public portfolio reference; this screen did not establish a source-owned generator for the exact full portfolio. | Measurement reference only. |
| [Rithvik, 32.86114](https://www.kaggle.com/code/rithvikredrouthu/shut-up-and-calculate-vqcc-32-86114) | Kernel metadata declares the `rithvikredrouthu/qcc-milestone-set` dataset input. | No candidate promoted from this static screen. |
| [Syed, own-circuit portfolio](https://www.kaggle.com/code/syed3000/vqcc-own-circuit-portfolio-notebook) | Small public notebook and dataset reference; not independently validated for reproducible exact outputs in this pass. | No candidate promoted. |
| [Tony Li, 32.85306 generators](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators) | Dataset metadata declares license `other`. Its READMEs say the DQI builder uses recovered native KMX decoder stages, Invsqrt reassembles released v90 assembly, and Chemistry uses original plus disassembled released loaders. The generator reconstructs the released files byte for byte. | Rejected as a candidate under the source-owned-circuit rule. Keep only as a measurement/provenance reference; do not port, execute, copy, or submit its circuits. |

## Active work

Public-source discovery is paused. The only active performance direction is the
source-owned FMA decoder. Its projected `202,075T` is below the current
`221,529T` score gate, but the complete 4+66 schedule has no proven
`Q <= 890` width, phase, and cleanup ledger. That schedule is the next gate.
