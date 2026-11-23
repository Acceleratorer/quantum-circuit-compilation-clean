# exp-057 FMA pair update component

## Score target

The previously saved rank-1-equivalent DQI target was `T <= 213,956.98` at
`Q=890`. The 02:43 UTC leaderboard audit now sets the target to
`T <= 211,775.05` at `Q=890` and
`R=1.1912605`. The 70-symbol circuit must fit this complete resource bound;
the new component count is not a circuit estimate.

## V18 gate achieved

Private Kaggle kernel v18 passed the one-pair normalized MBU update for both
branches: 32 cases per branch, `Q=50`, `T=54`, 13 clean scratch qubits,
preserved ratio and branch, and zero phase flips.

Evidence: [v18 evaluation receipt](../evals/2026-11-23-exp057-fma-pair-update-mbu-v18.json),
[run log](../log/2026-11-23-exp057-fma-pair-update-mbu-v18.md),
[raw output](../experiments/exp-057/kaggle-v18-output.log), and
[private kernel v18](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/18).

## Resource decision

The v17 `210T` implementation would cost `507,150T` across the 2,415 pair
updates and is closed. Repeating the v18 `54T` component gives `130,410T`,
matching the existing `42T` product plus `12T` controlled-swap ledger. The
prior `202,075T` full projection already includes this subtotal and `71,665T`
of other estimated work, leaving only `9,700.05T` beneath the current full
DQI gate. V18 receives ratio and branch inputs; integration, width,
output/phase, cleanup, and verifier cost remain unmeasured.

The next gate is one source-owned circuit for ratio generation and all 2,415
updates, followed by exact full-resource accounting and the DQI output/phase,
cleanup, and official verifier. Close this route if the composed circuit misses
the gate; no new branch is justified by the one-cell result.
