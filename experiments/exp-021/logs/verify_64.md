# 2026-11-13 chemistry candidate check

- Candidate family: `1f19ecca7044` (15 `.kmb` loaders plus `submission.npz`).
- Official `dfthcsos/verify.py --shots-per-address 64`: PASS, 78,080 shots.
- Score: `298998656.7697932`; lambda_eff: `46.91350973464301`; Toffoli: `14926`; Q: `427`.
- Retained v24 chemistry `e9cffb84`: `297237044.9509761`.
- Decision: reject; the lower static loader count does not beat the factorization's effective cost.
