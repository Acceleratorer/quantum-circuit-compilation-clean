# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own submitted public score | **25.40482** |
| Best local candidate estimate | **25.44954** |
| Live leaderboard top observed | **29.90871** |
| Current candidate members | `9c708f7b` / `5778cdd5` / `e9cffb84` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-019/` records the current hybrid: the reproducible 5778cdd5 retained-product DQI, the 62-qubit invsqrt frontier, and the fresh Apache chemistry prefix `4a2db87b0c13`. Official verifier evidence at three salts implies a local geometric mean of 25.4495735281. The retained DQI is rebuilt from a public notebook and the public 4c81b726 binary; final prize eligibility remains a host decision.

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
