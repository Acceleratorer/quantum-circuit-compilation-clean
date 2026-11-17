# 2026-11-18 — Bori frontier hybrid, public 28.14028

## Action

Inspected the completed public kernel
`boristown/qcc-gap-3-residue-repair-and-c43-native-compiler`. Its inverse and
chemistry members were better than the submitted portfolio. Its newer DQI
member (`bb9bf415`) was not selected because the kernel audit explicitly left
weight-16/17 counterexamples open. Built one hybrid using Bori's inverse and
chemistry with the already-scored Asterios DQI (`46446af1`) and submitted it
once as Kaggle ref `58479383`.

## Evidence

- Archive: 18 members, CRC clean, member hashes match receipts; SHA-256
  `4ccce01059e6d5c769e80a8091cc08a8c05a38588fc10a3877524412dd9e95cf`.
- Inverse: PASS, 44 qubits, cost `74560.90687312803`, 200,540,928 shots.
- DQI: PASS, 890 qubits, cost `347904227555.5428`, 102,400 shots, zero
  default-salt value/phase errors.
- Chemistry: PASS, 427 qubits, cost `294642305.5649051`, 78,080 shots.
- Local zero-error geometric mean: `28.140276838282986`.
- Kaggle ref `58479383`: COMPLETE, public score `28.14028`.
- Public rank: `505 / 3273`; leader `aadi_stonks` scored `31.44520` in the
  saved `2026-11-17T19:25:10Z` leaderboard CSV. CSV hash and path are in
  `evals/2026-11-18-bori-frontier-hybrid.json`.

## Decision

The hybrid improves the previous public score by `0.08066`, but rank 1 remains
`3.30492` points ahead. With inverse and chemistry fixed, DQI would need to
fall to about `249.33e9`, a `28.33%` reduction. The selected DQI has a separate
seven-salt audit with one value error on one salt; this remains the main
correctness risk. Do not use the higher-scoring Bori DQI until its documented
weight-16/17 counterexamples are resolved.
