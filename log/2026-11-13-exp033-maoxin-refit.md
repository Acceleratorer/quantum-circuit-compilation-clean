# 2026-11-13 — exp-033 Maoxin v25 chemistry refit

- Pulled `maoxin123/qcc-v25-coded-word-chemistry` and verified its 4,044-Toffoli
  loader chemistry locally with the official verifier.
- Ran 200 constrained reduced-gradient iterations from its factorization and
  rebuilt the full 18-member archive.
- Final chemistry: PASS, `78080` shots, score `295362181.14128023`,
  `lambda_eff=46.895912537812926`, `Q=427`, `T=14750`.
- Archive SHA-256: `0f992a97d4411737cb1da2712b3617f0bdfd784ce3a5b3ebe8689fd85a2365cb`.
- Portfolio projection: `27.289856632448792`.
- Public scan negatives: Ahoirg k6c is the same `4560ac0c` inverse; Hypery11's
  DQI is `939011176530.0194`; the 4,057-loader chemistry scores
  `296015250.2044768`; Vaibhav's C44 public loaders score `313929523.01738775`.
- Fresh lead negatives: Hengck's DQI is `410274633000.4907` with one value
  error, and the current Prvsiyan notebook reproduces the exp-033 stack.
- Public leaderboard snapshot at `2026-11-13T15:47:27Z`: Accelra is rank
  `347` at `27.11042`; rank 1 is `29.90871`, a gap of `2.79829`.
- Submission quota was `15/15` with reset at `2026-11-14T00:00:00Z`; exp-033
  remains unsubmitted until that reset.
- Decision: exp-033 is the sole prepared submit candidate; no quota was spent.
