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
matching the existing `42T` product plus `12T` controlled-swap ledger.

The v19 local bridge diagnostic measured `CONVERT + scan + reverse CONVERT`
at `Q=879`, `T=183,837`. A canonical DQI residue-pair control matched phase,
but the padded FMA low-rank row did not. Combining this path with the v18
repeated subtotal would cost `314,247T`, above the current `211,775.05T`
score-equivalent gate before omitted work. The earlier `202,075T` projection
is unsupported. V18 receives ratio and branch inputs; the full schedule,
width, cleanup, and verifier remain unmeasured.

The next gate is a reversible mapping from the terminal FMA state to the
scan-ready DQI residue pair that avoids the measured converter path. Measure it
with the scan and close exp-057 if the combined circuit cannot fit the resource
gate.
