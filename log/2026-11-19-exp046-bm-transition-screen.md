---
id: 2026-11-19-exp046-bm-transition-screen
date: 2026-11-19
---

# exp-046 — packed BM transition screen

The exact GF(2) screen enumerated all prefixes of lengths 5–9 and both next
symbols. At length 9, only `21 / 29` direct forward-state output bits and
`24 / 28` full-inverse output bits fit degree 4. The inverse fits all
`27 / 27` bits when the consumed syndrome symbol is provided separately.

The conditioned inverse is not a low-space solution because it requires the
syndrome symbol to remain available while the BM state is retained. The direct
degree-4 transition is a no-go. This does not rule out a factored GF(2^12)
transition, but that path should proceed only after a full compute, phase, and
uncompute resource count passes the DQI score gate.

Code, exhaustive results, and limits are in `experiments/exp-046/`.
