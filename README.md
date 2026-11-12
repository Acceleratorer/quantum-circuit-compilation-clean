# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own submitted public score | **25.40482** |
| Best local candidate estimate | **25.44954** |
| Live leaderboard top observed | **29.90871** |
| Current candidate members | `9c708f7b` / `4c81b726` / `f21b8a87` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-016/` records the hybrid frontier candidate: public 392k-Toffoli DQI plus the lower-cost 62-qubit invsqrt and 4,089-Toffoli chemistry portfolio. Member-level official verifier receipts imply a local geometric mean of 25.4495384012. The compiled DQI dataset does not include a generator, so prize eligibility remains a separate source-delivery question.

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
