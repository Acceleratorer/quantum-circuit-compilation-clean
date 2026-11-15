# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **27.28986** |
| Public rank (2026-11-14T18:53Z snapshot) | **590 / 3,056** |
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

`experiments/exp-033/` records the current public-best portfolio with Maoxin's 4,044-Toffoli chemistry loaders and a constrained refit. Kaggle submission `58348395` scored `27.28986`; the `2026-11-14T18:53:23Z` leaderboard snapshot lists it at rank `590 / 3,056`. The archive keeps the 46-qubit inverse `4560ac0c`, the 889-qubit DQI `821bf8d1`, and the refit chemistry member `06d67d21`; member hashes and the Kaggle round-trip are in the receipt. The local zero-failure GM is `27.2898566324`.

## DQI work still needed

The public DQI verifier reported PASS for `821bf8d1` at 102,400 shots, but a separate targeted audit flags rare weight-16/17 value counterexamples. That sampled PASS does not establish exhaustive correctness. The exact DQI member also is not reproducible from the generator currently committed in `src/dqi/`; the standing project rule requires future submissions to come from our own generator. See [the DQI module note](module/areebbb-retained-dqi.md) and [the latest frontier evaluation](evals/2026-11-15-frontier.json).

The score gap is `2.61885` points in the cited snapshot. If DQI alone closed that gap with the other members unchanged, its score would need to fall from `360.21e9` to about `273.63e9` (a `24.04%` reduction). This is the immediate optimization target, not a claim that the target is already achieved.

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
