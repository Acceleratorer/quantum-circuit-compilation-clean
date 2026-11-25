# 2026-11-24 — exp-065 source-owned archive submission

## Outcome

Kaggle completed submission `58832495` with public score `28.71611`.
The CLI returned no private score.

## Archive identity

- SHA-256: dd4615023eef0478f34738bd7205f3233a14c6cd7ccb800fa55e0b71b20233b6
- Size: 109,303,498 bytes
- Integrity receipt: [exp-065 archive receipt](../experiments/exp-065/receipts/archive.json)

## Submission issue and fix

The initial CLI call uploaded the archive but the create-submission endpoint
returned HTTP 400. Inspecting the Kaggle API response identified the cause:
the competition requires the uploaded file to be named submission.zip.
The staged archive was copied to that exact filename and its SHA-256 was
rechecked before the successful submission.

## Leaderboard context

The pre-submit snapshot is recorded in
[evals/2026-11-24-live-leaderboard-133209Z.json](../evals/2026-11-24-live-leaderboard-133209Z.json).
It has 3,671 ranked teams; rank 1 is 34.25544. Accelra's older public-circuit
entry is 33.17067 at rank 354. The source-owned result is `5.53933` below
the `34.25544` rank-1 score in the leaderboard readback. No rank-1
claim is made.
