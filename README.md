# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **27.28986** |
| Public rank (2026-11-14T16:28Z snapshot) | **570 / 3,051** |
| Rank 1 public score in that snapshot | **29.90871** |
| Gap to rank 1 | **2.61885** |
| Current candidate members | `4560ac0c` / `821bf8d1` / refit `06d67d21` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-033/` records the current public-best portfolio with Maoxin's 4,044-Toffoli chemistry loaders and a constrained refit. Kaggle submission `58348395` scored `27.28986` and ranked `570` in the cited public snapshot. The archive keeps the 46-qubit inverse `4560ac0c`, the 889-qubit DQI `821bf8d1`, and the refit chemistry member `06d67d21`; its SHA-256 and Kaggle round-trip match are in the receipt. All three have PASS evidence. The local zero-failure GM is `27.2898566324`; the public rank remains far below the current rank 1.

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
