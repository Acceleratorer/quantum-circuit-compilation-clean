# 2026-11-21 — focus reset and live frontier

- Refreshed the full public leaderboard at `2026-11-21T12:55:34Z`: 3,519
  teams; `Accelra` rank 1,202 at `28.14028`; leader `Z³C¹oherence` at
  `33.34845`.
- With other task costs fixed, the DQI score gate is `209.035e9`, equivalent
  to mean `T <= 221,529` at `Q=890`, `R=1.1912605`. The source-owned FMA
  projection is `202,075T`; `19,454T` remain for omitted work. Width, phase,
  and cleanup are not proved.
- Audited the public `32.85306` task-generator dataset as text only. Its
  metadata says license `other`; the builders reconstruct released circuit
  sources. It is not a source-owned candidate. Full disposition and hashes:
  [`exp-056`](../experiments/exp-056/README.md).
- Removed the redundant leaderboard ZIP after checking the CSV SHA-256,
  3,519 rows, leader, and own rank. Retained the CSV and JSON evaluation.
- Focus: no more public-source sweeps. Continue only the source-owned FMA
  4+66 schedule, with `Q <= 890`, `T <= 221,529`, exact verification, and
  multiple DQI salts as gates. No new submission is ready.
