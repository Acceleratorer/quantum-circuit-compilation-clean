# 2026-11-14 — exp-033 Kaggle submission

- Kaggle accepted exp-033 as submission ref `58348395` at `2026-11-14T15:58:04.167Z`.
- Kaggle requires this competition's upload filename to be exactly
  `submission.zip`; the first requests using `submission_exp033.zip` were
  rejected with `FAILED_PRECONDITION` and did not create submissions.
- Renamed the prepared archive inside its experiment directory without
  changing its bytes. SHA-256 remains
  `0f992a97d4411737cb1da2712b3617f0bdfd784ce3a5b3ebe8689fd85a2365cb`.
- Downloaded ref `58348395` back from Kaggle and verified its SHA-256 matches
  the local archive exactly; the temporary verification copy was removed.
- Kaggle completed scoring ref `58348395`: public score `27.28986`;
  private score is not available in the CLI response.
- The 16:07 UTC public leaderboard snapshot contains 3,050 teams. Accelra's
  prior score `27.11042` is rank `715`; rank 1 is `29.90871`, a gap of
  `2.79829`. The downloaded CSV SHA-256 is
  `15595fae8397667c21126afbfe8063f11c08e2e70c52c94ab21838d4964f275`.
- The submission-limits endpoint reports `numToday=1`, `numTotal=16`, and
  `numAllowedNow=4` after Kaggle accepted this submission.
- At the 16:28 UTC public leaderboard snapshot, Accelra is rank `570` of
  `3,051` teams. This improves the prior entry from rank `715` / `27.11042`
  by `145` places and `0.17944` points. Rank 1 is `29.90871`, a `2.61885`
  point gap. The leaderboard CSV SHA-256 is
  `f15a6d73c39045c9004150fc0115cb6ccbad81dc7117327fd1afe6ca6fe786a`.
- Follow-up lead check: downloading top-team ref `58275470` still returns
  HTTP 403 despite accepted competition rules. Competition-filtered public
  kernel listings for `jackvd`, `jsday96`, `tonylica`, and
  `yeoyunsianggeremie` returned no notebooks. No private artifact was accessed.
