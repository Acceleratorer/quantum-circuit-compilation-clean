# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **28.14028** |
| Latest live rank | **1368 / 3603 ranked teams** (team `Accelra`, Kaggle CLI snapshot at 2026-11-23 02:43 UTC) |
| Latest observed rank 1 public score | **33.85279** (team `Entangled Team`) |
| Score gap to rank 1 | **5.71251** |
| Current best submission members | `563d0583` / `46446af1` / `0bd9c68f` |

The latest persisted full leaderboard snapshot is from `2026-11-23T02:43:43Z`;
its CSV has 3,604 rows, including Kaggle's unranked sample row. Its hash is in
[`evals/2026-11-23-live-leaderboard-024343Z.json`](evals/2026-11-23-live-leaderboard-024343Z.json).

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
`2026-11-23T00:16:46Z` snapshot ranked it **1356**; and the latest
`2026-11-23T02:43:43Z` snapshot ranks it **1368**, with a `5.71251`-point gap
to rank 1. The earlier `2026-11-20T01:43:00Z` snapshot ranked it 981.
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

## DQI work still needed

The submitted DQI circuit (`46446af1`) passed the official verifier at
102,400 shots with zero observed default-salt errors. A separate seven-salt
audit of this same hash observed one value error on one salt, so the sampled
PASS is not an exhaustive correctness proof. The newer DQI candidate in
Bori's kernel was not selected: its own audit leaves weight-16/17
counterexamples open.

With the submitted inverse and chemistry held fixed, matching the current
leader's `33.85279` requires DQI cost at or below `199.830e9`, a `42.56%`
reduction from `347.904e9`. At `Q=890` and `R=1.1912605`, this means mean
`T <= 211,775.05`. The FMA projection is `202,075T`, leaving `9,700.05T`
before the still-unproven full schedule, width, phase, and cleanup.
This is score-equivalence math, not a measured leader cost or candidate. See
the [latest leaderboard evaluation](evals/2026-11-23-live-leaderboard-024343Z.json).
The remaining high-value work is a reproducible candidate that clears its
task's exact verifier and resource gates.

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
