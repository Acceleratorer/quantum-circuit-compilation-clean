# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **28.05962** |
| Latest observed public rank | **893 / 3271** (submission `58478432`) |
| Rank 1 public score in the same snapshot | **31.44520** |
| Score gap to rank 1 | **3.38558** |
| Current candidate members | `09000960` / `46446af1` / `8c9a3020` |

The score and rank are from the authenticated Kaggle public leaderboard snapshot
at `2026-11-17T18:36:17Z`; the complete CSV and SHA-256 are recorded in
[`evals/2026-11-18-asterios-28059.json`](evals/2026-11-18-asterios-28059.json).

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

The best submitted archive came from the public kernel
[`asteriospanoras/qcc-atlas-toolkit-in-notebook-chemistry-refit`](https://www.kaggle.com/code/asteriospanoras/qcc-atlas-toolkit-in-notebook-chemistry-refit).
Its local zero-error geometric mean is `28.0596332502`; Kaggle submission
`58478432`
scored `28.05962` and was rank **893** in the latest saved snapshot. The
18-member archive passed CRC and receipt-hash checks and has SHA-256
`670f496db8d83ec5dde474b737eece0f825145c123acd09e4ede9f1af4a67ab5`.
The ZIP and circuit binaries remain in ignored `kaggle/staging/`; the tracked
evaluation contains the verifier and leaderboard evidence.

This improves the previous public score `28.05810` by `0.00152`. The gain is
real but small relative to the current leaderboard gap.

## DQI work still needed

The current DQI circuit (`46446af1`) passed the official local verifier at
102,400 shots with zero observed value or phase errors. This is sampled
verification, not an exhaustive correctness proof. The public notebook output
is hash-locked, but the exact circuit is not yet reproduced by the local DQI
generator; future submissions should come from a reproducible local generator.

With the other two task costs held fixed, matching the current rank-1 score
`31.44520` requires DQI cost near `247.20e9`, about a `28.95%` reduction from
`347.90e9`. The target is estimated from the geometric-mean score formula and
is not an achieved result. The next useful work is a concrete DQI construction
that can be reproduced and verified, rather than another small chemistry
refit.

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
