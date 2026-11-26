# 2026-11-26 — Published BM circuit cost gate

The optimized Berlekamp–Massey DQI circuit in Gu et al. reports 440,000
Toffolis and 1,837 peak qubits. Its history reconstruction reduces the saved
exception stack to 19 qubits, but the complete circuit still misses our
competition's current `R × Q² × T` rank-1 tie gate by 6.50× at the published
resource point. At that width, the tie gate allows about 67,649 Toffolis.

Decision: close the direct port before spending time on source translation.
The result does not rule out a new BM design that substantially reduces the
live width or gate count. The calculation and assumptions are in
[`evals/2026-11-26-bm-published-cost-gate.json`](../evals/2026-11-26-bm-published-cost-gate.json).

Sources: [Gu et al., arXiv:2610.22367](https://arxiv.org/abs/2610.22367),
[Anthropic's summary](https://www.anthropic.com/research/designing-efficient-quantum-circuits).
