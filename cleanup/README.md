# Workspace prune — 2026-11-13

The Kaggle workspace contained 57.38 GiB of downloaded/generated files. A pre-delete
manifest was written to `2026-11-13-prune-manifest.json`; the listed targets were
verified to stay inside the competition workspace and were removed with their sizes
recorded. The prune removed 43.18 GiB across 7,911 files, leaving about 14.20 GiB.

## Preserved

- `artifacts/`: our verifier receipts, circuit builds, and research scripts.
- `somejoint_ds_/`: retained DQI source/search work that may still produce a better component.
- `competition_data/` and `.venv/`: official verifier and working runtime.
- `output_kirderf/submission.zip`: current best locally verified portfolio archive.
- `kernel_outputs/`: compact output receipts.
- `public_datasets/` lightweight metadata/provenance and selected sources.
- `tmp/github_publish/`: the clean evidence Git repository.

The removed directories were duplicate Kaggle downloads, old portfolio copies, extracted
verification copies, and temporary notebook outputs. Public sources remain downloadable
from Kaggle; the evidence repo keeps hashes, scores, provenance, and the exact deletion
manifest.

## Root cache prune — 2026-11-15

The remaining scratch workspace was measured at 16.99 GiB across 5,266 files.
The canonical evidence repository at `tmp/github_publish/` and the Python runtime
at `.venv/` are protected. The deletion manifest is
[`2026-11-15-root-prune-manifest.json`](2026-11-15-root-prune-manifest.json).
Within the repository, ignored downloaded outputs and Python caches totaling
about 205 MiB were also removed; the exp-036 submission ZIP in
`kaggle/staging/exp-036-atakan/` was preserved and its SHA-256 matches the
receipt.

## Staging prune — 2026-11-18

Removed one 505 MiB extracted dqi.kmb copy after its SHA-256 matched the member in the preserved submission.zip. The receipt records both hashes and sizes: [2026-11-18-staging-prune-manifest.json](2026-11-18-staging-prune-manifest.json).
