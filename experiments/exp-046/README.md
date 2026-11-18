---
id: exp-046
title: Packed BM local transition degree screen
task: dqi
tests: experiments/exp-046/bm_transition_screen.py (exhaustive GF(2) reachable transitions)
status: negative_result
result: direct degree-4 forward and full-inverse formulas fail by prefix 9; the symbol-conditioned inverse fits but keeps syndrome data available
---

# Packed BM local transition degree screen

## Question

Can the exp-045 packed Berlekamp–Massey state update from one syndrome symbol
be represented by low-degree Boolean functions of the packed state and that
symbol, in both the forward and reverse directions?

## Method

Enumerate every GF(2) prefix at lengths 5–9 and both possible next symbols.
For each reachable transition, encode the current and next packed BM states
with fixed-width coefficient and control bits. Exactly test whether every
output bit lies in the span of square-free monomials through degree 4. Also
screen the inverse transition, which must recover both the prior state and the
consumed syndrome symbol from the next state alone. Separately screen the
inverse when the syndrome symbol remains available in its original input
register. Assertions check injectivity before measuring degree.

This is a small-field feasibility screen only. A degree-4 fit does not prove a
cheap GF(2^12) circuit; a failure rules out only a direct degree-4 formula for
the measured transition.

## Results

At prefix length 9, only `21 / 29` forward-state output bits and `24 / 28`
full-inverse output bits fit degree 4. The full inverse must recover the
consumed symbol because it is part of the state being uncomputed. With that
symbol supplied as a separate input, all `27 / 27` prior-state bits fit degree
4. The exact counts for every tested length are in `results.json`.

## Decision

No-go for a direct degree-4 transition on the packed state. The conditioned
inverse does not solve the low-space problem: it assumes the syndrome symbol
is still available separately, which would require retaining the syndrome
alongside the BM state. The high-space screen in the mid-competition record
already puts that design near `Q=1730` and requires `T <= 68.8k`, below the
straightforward BM estimate.

This result does not rule out a factored reversible transition over GF(2^12).
Do not build one until a complete forward, phase, and uncompute count can pass
`R × Q² × T <= 245.285e9`.

## Run

```powershell
..\..\.venv\Scripts\python.exe experiments\exp-046\bm_transition_screen.py
```
