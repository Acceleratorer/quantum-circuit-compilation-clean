---
id: exp-072
title: Source-built V19 chemistry loaders
task: portfolio
status: submitted_pending
date: 2026-11-26
result: All verifiers PASS; chemistry 3,328 Toffolis/pass; Kaggle submission 58907057 is pending
---

# exp-072 — source-built V19 chemistry loaders

This experiment ports Goodpjw2008's V19 chemistry loader construction into a
source-only build. It uses the published raw Maoxin parameter table, Goodpjw's
compact loader programs and refitted weights, and the pinned Tony Li generator
dataset. The Maoxin archive is scanned only for `submission.npz`; the builder
never reads a compiled circuit from it.

The 15 baseline loader files used to obtain register metadata are built from the
pinned editable KMX sources. Loader 0 is source-built and retained. Loaders 1–14
are rebuilt from Goodpjw's compact loader programs. The DQI and Invsqrt members
are also rebuilt from the pinned source dataset before the DQI rewrites are
applied.

## Lead and evidence

Goodpjw2008's [V19 notebook](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25057)
claims 3,310 Toffolis per chemistry pass and a public score of 33.25057. The
score in its title is not an independently confirmed result. Our source-only
build passed all verifiers at 3,328 Toffolis per pass, 18 above the notebook's
claim. Chemistry cost was `249,967,854.72`, a `608,050.42` reduction from
exp-071's `250,575,905.14`.

The build uses the source-built exp-071 DQI and Invsqrt components. The DQI
verifier observed four value errors on its default draw; exp-071's exact same
DQI hash observed zero, so the raw local geometric means are salt-sensitive.
Replacing only the DQI score with exp-071's result gives a diagnostic local
GM of `33.08134`; this is not a public-score projection. After rechecking the
archive and its member hashes, one public measurement was submitted as Kaggle
ref `58907057`. It is currently pending; exp-071 remains the best scored
source-owned submission at `33.05453`.

All official verifiers passed: chemistry on 78,016 shots at default and salt
42; Invsqrt on 200,540,928 shots; DQI on 102,400 shots with zero phase errors.
The source-built portfolio has 18 members, archive SHA-256
`6fb21b160f87ebeff80a9b506e7335e5a4d0803db5ca6e2ba61257010e084a5e`, and
local verifier GM `32.91482` on the default DQI draw. Full details are in the
[evaluation record](../../evals/2026-11-26-exp072-source-built-v19-chemistry.json).

## Reproduction

The private Kaggle script in `main.py` builds and runs the official verifiers.
`package_kernel.py` bundles its separated source module into Kaggle's single
script file. `kernel-metadata.json` pins the public competition, the Tony Li
generator dataset and the Maoxin kernel output that carries the raw parameter
table. The script checks dataset fingerprints, source hashes, output hashes,
archive membership and CRC.

The small `module/` directory contains the chemistry build code and the two
compressed public source payloads. Generated circuits and archives are not
tracked in Git. The private kernel completed as version 4 at
`accelra/exp-072-source-built-v19-chemistry`.

## Attribution and license

- Goodpjw2008, [Shorter Chemistry Loaders, V19](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25057),
  Apache-2.0. The embedded refitted weights, compact loader programs and loader
  builder are from this notebook; its SHA-256 is recorded in `evals/`.
- Maoxin123, [3,357-Toffoli chemistry loaders](https://www.kaggle.com/code/maoxin123/qcc-33-17-3-357-toffoli-chemistry-loaders),
  source of the raw parameter table (`ec85d969…`). No compiled loader circuit is
  read from this output.
- Tony Li, [Quantum AI 32.85306 task generators](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators),
  Apache-2.0. The editable KMX sources, DQI and Invsqrt builders, and pinned
  Kickmix SDK are checked before use.
- The DQI simplifications retain the upstream credits documented in
  [exp-066](../exp-066/UPSTREAM.md).

The notebook states that its own code and loader work are Apache-2.0 and that
upstream files retain their authors' terms. This experiment preserves that
attribution and keeps the upstream source URLs next to the implementation.
