# 2026-11-20 mid-competition gate

## Target

Reach the top public leaderboard position with a source-complete portfolio. The
current public target is `29.90871`; it moves as the leaderboard changes.

## Evidence required

- A completed Kaggle submission whose score and rank are in a dated leaderboard snapshot.
- A deterministic generator for every submitted circuit, with source lineage and hashes.
- Full official verifier evidence for the exact archived bytes, plus targeted checks for known DQI counterexamples.
- A score above the current `27.28986` portfolio before replacing it.

## Current gap

At the 2026-11-14 17:23 UTC snapshot, the current portfolio is rank `579 / 3,053`,
2.61885 points below rank 1. Its DQI costs `360.21e9`; if the other tasks stay
unchanged, DQI must reach about `273.63e9` to close the gap. The current DQI
member has a sampled PASS but known targeted counterexamples and no matching
generator in this repository. No replacement is ready to submit.
