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

## Packed-state layout check

Keeping the 840-qubit syndrome bank beside exp-045's observed 847-bit packed
BM state gives `Q=1,687` before extra workspace. At the current rank-1 tie
gate, that width allows about `79,334` mean Toffolis. The straightforward BM
subtotal is `102,900T` for 2,450 GF(2^12) products alone, before inversions,
phase evaluation, input restoration, and cleanup. Its optimistic score is
already `1.297x` the tie gate, so do not build this retained-syndrome layout.

The 847-bit state width is sampled rather than a worst-case bound, and the
product count is a straightforward estimate rather than a lower bound. The
screen closes this high-space layout only. Continue the BM/Hankel route only
if the block update can overwrite or compress the syndrome state in place.

I also extended the exact packed-state feedback screen to degree 5 at a
12-symbol GF(2) prefix. None of the polynomials through degree 5 in the 33
packed-state coordinates reproduces the next feedback across all 4,096
prefixes. This closes the simple low-degree local-feedback formula at that
screen size; it does not rule out a field-level or block/Hankel update.

Sources: [Gu et al., arXiv:2610.22367](https://arxiv.org/abs/2610.22367),
[Anthropic's summary](https://www.anthropic.com/research/designing-efficient-quantum-circuits).
