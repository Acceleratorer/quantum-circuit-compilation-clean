# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **28.14028** |
| Latest observed public rank | **505 / 3273** (submission `58479383`) |
| Rank 1 public score in the same snapshot | **31.44520** |
| Score gap to rank 1 | **3.30492** |
| Current candidate members | `563d0583` / `46446af1` / `0bd9c68f` |

The score and rank are from the authenticated Kaggle public leaderboard snapshot
at `2026-11-17T19:25:10Z`; the CSV and SHA-256 are recorded in
[`evals/2026-11-18-bori-frontier-hybrid.json`](evals/2026-11-18-bori-frontier-hybrid.json).

The repository keeps generators, verifier evidence, provenance, and experiment
notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and
are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

The current portfolio combines the 44-qubit inverse and chemistry files from
[`Bori's Gap-3 / C43 kernel`](https://www.kaggle.com/code/boristown/qcc-gap-3-residue-repair-and-c43-native-compiler)
with the previously scored DQI from
[`Asterios's kernel`](https://www.kaggle.com/code/asteriospanoras/qcc-atlas-toolkit-in-notebook-chemistry-refit).
Its local zero-error geometric mean is `28.1402768383`; Kaggle submission
`58479383` scored `28.14028` and ranked **505** in the latest saved snapshot.
The hash-verified 18-member archive has SHA-256
`4ccce01059e6d5c769e80a8091cc08a8c05a38588fc10a3877524412dd9e95cf`.
The archive stays in ignored `kaggle/staging/`; tracked verifier and
leaderboard evidence is in the evaluation record.

This improves the previous public score `28.05962` by `0.08066`. The score is
still `3.30492` points below rank 1.

## DQI work still needed

The submitted DQI circuit (`46446af1`) passed the official verifier at
102,400 shots with zero observed default-salt errors. A separate seven-salt
audit of this same hash observed one value error on one salt, so the sampled
PASS is not an exhaustive correctness proof. The newer DQI candidate in
Bori's kernel was not selected: its own audit leaves weight-16/17
counterexamples open.

With the submitted inverse and chemistry held fixed, matching rank 1's current
`31.44520` would require DQI cost near `249.33e9`, about a `28.33%` reduction
from `347.90e9`. This is an estimate from the geometric-mean score formula,
not an achieved result. The remaining high-value work is a reproducible DQI
construction that resolves the known error cases.

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
