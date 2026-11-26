# exp-053 four-to-five-pivot handoff — kernel v35

**Decision: no-go for this layout.**

The four-pivot compact state was continued through one recycled fifth pivot.
Across 32 GF(2^12) cases, labels and retained branch history matched the
reference; other payload was preserved, all scratch was clean, and phase flips
were zero. The circuit compiled at `Q=891`, one above the `Q=890` limit, with
`T=4,500`. Since this gate covers only the first five pivots, it cannot be
integrated into the full schedule.

The current leader score was `34.50408`. At `Q=890`, the score-equivalent tie
gate is `285,041.64` mean T. The historical `202,075T` projection plus the
`11,508T` four-point arithmetic proxy leaves `71,458.64T` on paper, but that
proxy can overlap the historical ledger and excludes the full tail. The hard
width failure is enough to close this 4+1 layout.

The private kernel and normalized result are recorded in
[`evals/2026-11-26-exp053-four-plus-one-handoff-v35.json`](../evals/2026-11-26-exp053-four-plus-one-handoff-v35.json)
and [`experiments/exp-053/logs/kernel-v35-output.json`](../experiments/exp-053/logs/kernel-v35-output.json).
No official verifier was run and no competition submission was made.
