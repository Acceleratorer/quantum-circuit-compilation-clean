# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own submitted public score | **27.11042** |
| Best local candidate estimate | **27.28986** |
| Live leaderboard top observed | **29.90871** |
| Current candidate members | `4560ac0c` / `821bf8d1` / refit `06d67d21` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-033/` records the current portfolio with Maoxin's 4,044-Toffoli chemistry loaders and a constrained refit. The archive keeps the 46-qubit inverse `4560ac0c`, the 889-qubit DQI `821bf8d1`, and the refit chemistry member `06d67d21`. All three have PASS evidence; the zero-failure local geometric-mean estimate is `27.2898566324`. The archive remains outside Git and awaits the next Kaggle quota reset.

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
