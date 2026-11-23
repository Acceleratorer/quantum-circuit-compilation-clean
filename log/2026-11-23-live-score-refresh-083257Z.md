# 2026-11-23 — live leaderboard and DQI gate refresh

Kaggle CLI captured the public leaderboard at 08:32:57 UTC. Accelra is rank
1386 at 28.14028; Entangled Team is rank 1 at 33.90122,
a gap of 5.76094. The retained CSV and hashes are in
[`kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-23T08-32-57.csv`](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-23T08-32-57.csv)
and [`evals/2026-11-23-live-leaderboard-083257Z.json`](../evals/2026-11-23-live-leaderboard-083257Z.json).

Holding the other task costs fixed, score equivalence sets the DQI target at
198.975B. At Q=890 and repetition factor 1.1912605, that requires
mean T ≤ 210,868.74. The exp-057 route still projects 243,905T before DQI
output, phase, and cleanup, at least 33,036T over the gate.

The five public usernames on the current leader were checked with Kaggle
`kernels list`. The only matching public kernel found was Tony Li's older
32.85306 notebook; [exp-056](../experiments/exp-056/README.md) already rejects
its recovered-KMX generators as a source-owned submission path. No public
current-leader generator was found. Keep the next work on one source-owned DQI
path; no submission was made.
