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
