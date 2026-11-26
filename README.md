# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current status (2026-11-27)

| Item | Value |
|---|---:|
| Highest recorded account score (public archive; ineligible) | **33.17067**, submission `58771243` |
| Best source-owned submission | exp-082, Kaggle ref `58958257`, score **33.08801** |
| Latest source-built result | exp-082: all task verifiers PASS; local GM `33.08804`; Kaggle score `33.08801` |
| Latest leaderboard snapshot | `Accelra` rank **719 / 3733**, score `33.17067`; source [`snapshot`](kaggle/snapshots/2026-11-25/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-25T202946Z.csv) |
| Rank 1 in that snapshot | **34.34445** (`Entangled Team`); gap from the then-best source-owned score: **1.26276**; score-equivalent rank **1164** |
| Current CLI leader (read `2026-11-26T17:42:19Z`) | **34.50408** (`Cat with 2 Qubits`); gap from source-owned best: **1.41607** |
| DQI tie gate at `Q=900` | **278,784.97 mean T** (score-equivalent estimate using exp-082) |

Submissions `58771243` and `58479383` used public circuit archives, so their
scores are historical Kaggle measurements only. Neither demonstrates our own
generator or counts as eligible evidence for the source-owned goal; see the
[provenance receipt](evals/2026-11-23-submission-58771243-provenance.json).

The latest persisted full leaderboard snapshot is from `2026-11-25T20:29:46Z`;
its CSV has 3,733 ranked teams. Accelra's 33.17067 score is from a public
circuit archive. The best source-owned public result is exp-082's `33.08801`
(ref `58958257`), from a source build with local verifier GM `33.08804`; the
submission is complete. A fresh CLI top-five read shows the live leader at
`34.50408`, a `1.41607` gap. The DQI gate at `Q=900` is derived from the
scoring formula and is not the leader's measured component cost. Exp-072's
ten DQI rewrites changed the final circuit hash from exp-071's `4b572141…` to
`6f78ecdd…`; exp-066 and exp-072 both observed four value errors on that
rewritten circuit locally, so it is not the current base.
See the [exp-082 evaluation](evals/2026-11-26-exp082-source-built-v22-chemistry.json)
and [updated DQI gate](evals/2026-11-26-dqi-score-equivalent-gate.json).

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

The exp-062/063/064 members are source-built and verifier-checked. The current
source-owned best is exp-082 at `33.08801`, up `0.00167` from exp-074. Earlier
DQI rewrites were rejected after local value errors; the best valid DQI remains
at `316,131.22` mean T. Rank 1 is still `1.41607` ahead. See the
[source-owned archive milestone](milestone/2026-11-23-source-owned-archive.md),
[exp-082 evaluation](evals/2026-11-26-exp082-source-built-v22-chemistry.json),
and [current DQI gate](evals/2026-11-26-dqi-score-equivalent-gate.json).

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
