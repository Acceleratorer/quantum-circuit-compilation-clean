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

## Portfolio screen prune — 2026-11-19

Removed the 1.05 GB temporary Ozertuu portfolio after retaining its verifier
receipt, member hashes, archive hashes, and no-submit decision in `evals/`.
Also removed the Kaggle leaderboard download ZIP after extracting and retaining
the CSV snapshot. Targets and hashes are in
[`2026-11-19-portfolio-screen-prune-manifest.json`](2026-11-19-portfolio-screen-prune-manifest.json).

## Staging artifact prune — 2026-11-19

Removed 26 ignored files (1,474,546,514 bytes, about 1.37 GiB): downloaded
public submission archives, leaderboard ZIP wrappers whose CSV snapshots are
already tracked, and two FCIDUMP copies byte-identical to the canonical verifier
input. The manifest records each path, size, and SHA-256. The official verifier,
canonical input, source archives, source code, and compact evaluation receipts
remain in place.

See [`2026-11-19-staging-artifact-prune-manifest.json`](2026-11-19-staging-artifact-prune-manifest.json).

## Source-owned archive staging prune — 2026-11-26

Removed one extracted DQI circuit after its SHA-256 matched the `dqi.kmb`
member of the preserved source-owned `submission.zip`. Also removed the
byte-identical `source-owned-submission.zip` copy: Kaggle rejected that
filename, while the retained `submission.zip` completed as submission
`58832495`. The archive receipt and source/evaluation records remain in Git.

Removed 2 files (`938,135,322` bytes, about `0.87 GiB`). See
[`2026-11-26-staging-prune-manifest.json`](2026-11-26-staging-prune-manifest.json).
