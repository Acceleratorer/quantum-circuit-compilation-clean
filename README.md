# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own submitted public score | **25.40482** |
| Best local candidate estimate | **27.07839** |
| Live leaderboard top observed | **29.90871** |
| Current candidate members | `321aff83` / `7cbe8ecf` / refined `fe0bd93b` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-023/` records the current Syed v12 portfolio with a refined chemistry weight file. The archive keeps the 46-qubit invsqrt `321aff83`, the 889-qubit DQI `7cbe8ecf`, and the refined chemistry member `fe0bd93b`. All three pass the official local verifiers; the zero-failure local geometric-mean estimate is `27.0783877340`. The Kaggle submission watcher is recorded in the receipt and the archive remains outside Git.

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
