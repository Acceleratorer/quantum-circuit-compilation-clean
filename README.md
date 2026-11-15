# Quantum Circuits

Research log and reproducible tooling for the Google Quantum AI Verifiable Quantum Circuit Compilation competition.

## Current verified frontier

| Item | Value |
|---|---:|
| Best own Kaggle public score | **27.31542** |
| Public rank | **Not captured for submission 58383886** |
| Rank 1 public score in that snapshot | **29.90871** |
| Gap to rank 1 (score snapshot) | **2.59329** |
| Current candidate members | `a4d46b17` / `821bf8d1` / `6f85dc86` |

The repository keeps generators, verifier evidence, provenance, and experiment notes. Large circuit binaries and Kaggle submission ZIPs stay outside Git and are addressed by SHA-256 receipts.

## Layout

- `experiments/` — numbered, reproducible experiments and verifier receipts.
- `src/` — generators and analysis tools.
- `kaggle/` — competition digests and public-source notes.
- `knowledge/` — claims, decisions, and research direction.
- `literature/` — paper notes.

## Latest candidate

`experiments/exp-036/` records the latest verified portfolio. Kaggle submission
`58383886` scored `27.31542`; the authenticated API session did not expose its
live rank, so no rank is claimed. The archive keeps inverse `a4d46b17`, DQI
`821bf8d1`, and chemistry `6f85dc86`; member hashes and verifier evidence are
in the receipt. The local zero-failure GM is `27.3154195993`.

`experiments/exp-038/` records a stronger local portfolio with chemistry
`0e26f057`. Its source notebook reports full verifier PASS and local GM
`27.3167386412`; Kaggle submission `58386039` is pending scoring. The exact
archive and member receipt stay outside Git under `kaggle/staging/`.

## DQI work still needed

The public DQI verifier reported PASS for `821bf8d1` at 102,400 shots, but a separate targeted audit flags rare weight-16/17 value counterexamples. That sampled PASS does not establish exhaustive correctness. The exact DQI member also is not reproducible from the generator currently committed in `src/dqi/`; the standing project rule requires future submissions to come from our own generator. See [the DQI module note](module/areebbb-retained-dqi.md) and [the latest frontier evaluation](evals/2026-11-15-frontier.json).

The score gap to the cited leader is `2.59329` points. If DQI alone closed
that gap with the other members unchanged, its score would need to fall from
`360.21e9` to about `273.63e9` (a `24.04%` reduction). This remains an
optimization target, not a claim that the target is already achieved.

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
