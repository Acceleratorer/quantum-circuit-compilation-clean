# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current status (2026-11-26)

| Item | Value |
|---|---:|
| Highest recorded account score (public archive; ineligible) | **33.17067**, submission `58771243` |
| Best source-owned submission | exp-072, Kaggle ref `58907057`, score **33.08169** |
| Latest source-built candidate | exp-073: all verifiers PASS with base DQI; **not submitted** because no public-score gain is established |
| Latest leaderboard snapshot | `Accelra` rank **719 / 3733**, score `33.17067`; source [`snapshot`](kaggle/snapshots/2026-11-25/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-25T202946Z.csv) |
| Rank 1 in that snapshot | **34.34445** (team `Entangled Team`); gap from source-owned best: **1.26276**; score-equivalent rank **1164** |

Submissions `58771243` and `58479383` used public circuit archives, so their
scores are historical Kaggle measurements only. Neither demonstrates our own
generator or counts as eligible evidence for the source-owned goal; see the
[provenance receipt](evals/2026-11-23-submission-58771243-provenance.json).

The latest persisted full leaderboard snapshot is from `2026-11-25T20:29:46Z`;
its CSV has 3,733 ranked teams. Accelra's 33.17067 score is from a public
circuit archive. The best scored source-owned result is exp-072's `33.08169`;
that score would place 1,164 by score in the same snapshot. The exp-072 archive
lowered chemistry cost by `608,050.42` and scored publicly. Its ten DQI rewrites
changed the final circuit hash from exp-071's `4b572141…` to `6f78ecdd…`;
exp-066 and exp-072 both observed four value errors on that rewritten circuit
locally. The raw local GM `32.91482` is not a public-score projection. See the
[`exp-072` evaluation](evals/2026-11-26-exp072-source-built-v19-chemistry.json).

The repository keeps generators, verifier evidence, provenance, and experiment
notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and
are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered experiments, resource screens, and verifier receipts.
- `src/` and `module/` — source-owned generators and module-level references.
- `evals/` — leaderboard snapshots and score-equivalence calculations.
- `tests/` — receipt and source-screen checks.
- `log/` and `milestone/` — dated progress records and resource gates.
- `knowledge/` — active directions, decisions, and claims.
- `kaggle/` and `literature/` — competition source notes and research papers.

## Latest public reference portfolio (not source-owned)

This reference portfolio combined the 44-qubit inverse and chemistry files from
[`Bori's Gap-3 / C43 kernel`](https://www.kaggle.com/code/boristown/qcc-gap-3-residue-repair-and-c43-native-compiler)
with the previously scored DQI from
[`Asterios's kernel`](https://www.kaggle.com/code/asteriospanoras/qcc-atlas-toolkit-in-notebook-chemistry-refit).
Its local zero-error geometric mean is `28.1402768383`; Kaggle submission
`58479383` scored `28.14028`. The `2026-11-20T17:14:49Z` snapshot ranked the
team **1079**; the `2026-11-21T12:55:34Z` snapshot ranked it **1202**; the
`2026-11-22T23:05:56Z` snapshot ranked it **1353**; the
`2026-11-23T00:16:46Z` snapshot ranked it **1356**; the
`2026-11-23T02:43:43Z` snapshot ranked it **1368**; and the latest
`2026-11-23T04:27:24Z` snapshot ranks it **1372**, with a `5.71251`-point gap
to rank 1.
The earlier `2026-11-20T01:43:00Z` snapshot ranked it 981.
The hash-verified 18-member archive has SHA-256
`4ccce01059e6d5c769e80a8091cc08a8c05a38588fc10a3877524412dd9e95cf`.
The downloaded archive was removed from local staging; its hash, member hashes,
and verifier evidence remain in [the evaluation record](evals/2026-11-18-bori-frontier-hybrid.json)
and [the cleanup manifest](cleanup/2026-11-19-staging-artifact-prune-manifest.json).
This public portfolio is a measurement reference, not a source-owned candidate.

This improves the previous public score `28.05962` by `0.08066`.

A later public portfolio's published verifier receipt reports three PASS
results and a local geometric mean of `28.23163`; it would fall near rank 72
in that leaderboard snapshot. It was not submitted: the standing user decision
requires our own generator for every submitted circuit.
Its receipts and source hashes are recorded in
[`evals/2026-11-18-ozertuu-282316.json`](evals/2026-11-18-ozertuu-282316.json).

This archive is a leaderboard probe assembled from public compiled circuit
files. The tracked source has not yet been shown to regenerate every exact
member, so this result is not treated as prize-ready. Future submissions must
be built by our own attributed generators and accompanied by exact-output
hashes.

## Source-owned member progress

The exp-062/063/064 members are source-built and verifier-checked. The exp-071
hybrid scored `33.05453` on Kaggle. exp-072 rebuilt every circuit input from
source, passed all three task verifiers, reduced chemistry cost by `608,050.42`,
and scored `33.08169` publicly as ref `58907057`. Its ten DQI rewrites changed
the exp-071 base hash `4b572141…` to `6f78ecdd…`; the rewritten circuit observed
four value errors in both exp-066 and exp-072 local verification. Rank 1
remains unmet. exp-073 is checking the same chemistry with unmodified base DQI.
See the
[source-owned archive milestone](milestone/2026-11-23-source-owned-archive.md),
[exp-071](experiments/exp-071/README.md), and
[exp-072](experiments/exp-072/README.md).

Rebuild the local archive with:

```powershell
python experiments/exp-014/package_candidate.py `
  --invsqrt <path-to-invsqrt.kmb> `
  --dqi <path-to-tagged-dqi.kmb> `
  --chem-dir <path-to-dfthcsos> `
  --out <path-to-submission.zip>
```

## Reproducibility rule

Every candidate that is submitted must have a receipt containing member hashes, the archive SHA-256, verifier status, and the exact salt/shot settings. Do not commit credentials or generated circuit binaries.
