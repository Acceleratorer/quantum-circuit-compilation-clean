# exp-065 — source-owned archive

## Archive

- 18 members: invsqrt, DQI, 15 dfthcsos angle circuits, and submission.npz.
- Archive SHA-256: `dd4615023eef0478f34738bd7205f3233a14c6cd7ccb800fa55e0b71b20233b6`.
- Size: 109,303,498 bytes.
- Integrity receipt: [archive.json](receipts/archive.json).
- The staged ZIP is kept outside Git under `tmp/archive-stage-2026-11-23/`.

The archive members match the source-build receipts for
[exp-062](../exp-062/README.md), [exp-063](../exp-063/README.md), and
[exp-064](../exp-064/README.md). Each member passed its official verifier.

## Kaggle submission

The first CLI attempt used the filename `source-owned-submission.zip`.
Kaggle rejected it with HTTP 400 and the message that this competition
requires the upload filename `submission.zip`. A byte-identical copy was then
submitted under the required name; its SHA-256 matches the archive receipt.

- Submission ref: `58832495`
- Last observed status: `PENDING`
- Public score: pending
- Leaderboard snapshot before this submission:
  [2026-11-24 evaluation](../../evals/2026-11-24-live-leaderboard-133209Z.json)

The rules page confirms the account has accepted the competition rules. The
CLI readback confirms the submission exists; the score must be recorded after
Kaggle finishes scoring. Rank 1 is not established by the local verifier
passes or by this pending submission.
