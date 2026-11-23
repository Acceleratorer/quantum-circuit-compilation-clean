---
id: lit-select-swap-qrom-fit
title: "Select-Swap QROM trade-off for the 7-bit chemistry loaders"
year: 2024
tasks: dfthcsos
relevance: "Clean Select-Swap reduces loader Toffolis, but the width trade-off erases the gain"
read: 2026-11-23
---

# Select-Swap QROM trade-off for the 7-bit chemistry loaders

## Primary-source result

Babbush et al. give a unary-iteration QROM with T-count `4N - 4`, independent of word width, using logarithmic workspace; each row's classical data is encoded as target CNOTs. For an XOR loader, this is the relevant width-independent baseline. [Babbush et al., §III.3](https://arxiv.org/html/1805.03662#III.3)

Low, Kliuchnikov, and Schaeffer split the address into a high part and a low part of size `log2(λ)`, load `λ` words in parallel, then route the selected word with controlled swaps. Their SelectSwap row in Table 2 gives

```text
T-count <= 4 ceil(N / λ) + 8 b λ + O(log N log λ)
qubits   = b λ + 2 ceil(log2 N)
```

Here `N` is the number of addresses, `b` is the output width in bits, and `λ` is the block size. The T-count trade-off is real only if the extra `b(λ-1)` data registers fit the workspace budget. Their Sec. 2 specifies the data-lookup interface and notes that non-power-of-two `λ` requires quotient/remainder arithmetic; using power-of-two `λ` avoids that split arithmetic. [Low, Kliuchnikov & Schaeffer, Sec. 2 and Table 2](https://arxiv.org/html/1812.00954)

Dividing the paper's T-count upper bound by four gives a rough Toffoli-equivalent estimate `ceil(N/λ) + 2 b λ`; it is not an exact count in this competition's gate model. The verifier's XOR semantics, cleanup, padding behavior, and actual emitted gate count still need a circuit-level check. In particular, the SelectSwap paper specifies lookup into a zero output and may carry garbage, so adapting it to the required arbitrary-target XOR oracle is not automatic.

## Fit to this workspace

The candidate has `N = 1,219` addresses, `b = 5 × 7 = 35` output bits, and 15 loaders. The current balanced tree emits `N - 2 = 1,217` Toffoli-like gates per loader, for `18,255` static gates per pass. It uses `11 + 35 + 10 = 56` qubits per loader. The current `exp-061` builder expected `3,468` gates, but its run produced `18,255` and stopped before writing outputs; the smaller expectation has no implemented construction behind it.

The published SelectSwap upper bound gives these first screens (15 loaders; one pass). The last column projects the **whole-task verifier score**, holding this factorization's `lambda_eff` fixed and using the official forward-plus-reverse Toffoli accounting. It is an arithmetic screen, not a measured circuit:

| Block size `λ` | Approx. Toffolis per loader | Family static T per pass | Estimated ANGLES width | Projected whole-task score |
|---:|---:|---:|---:|---:|
| Current tree | 1,217 measured | 18,255 | 56 measured | 817,512,097.94 measured |
| 2 | 750 | 11,250 | 92 | 551,217,178.34 |
| 3 | 617 | 9,255 | 127 | 475,377,297.59 |
| 4 | 585 | 8,775 | 162 — over cap | rejected |
| 8 | 713 | 10,695 | 302 — over cap | rejected |

The whole-task projection uses `score = lambda_eff × T_total × Q_total`. The verified 7-bit baseline has `lambda_eff = 46.932071378`, `T_total = 43,010`, and `Q_total = 405`; its 18,255 ANGLES Toffolis per pass are charged in both the forward and reverse traversal. For blocks 2 and 3, the estimated ANGLES workspace stays below the task's existing shared heuristic workspace, so this screen keeps `Q_total = 405`. Against the current best chemistry score of `294,642,305.56`, a loader family needs at most **4,500 static Toffolis per pass** under these same fixed metrics. Both width-fitting SelectSwap estimates miss that gate; every `λ≥4` exceeds the 128-qubit ANGLES cap recorded by [exp-007](../../experiments/exp-007/README.md). The non-power-of-two `λ=3` estimate also omits quotient/remainder arithmetic, so it is optimistic. Row uniqueness does not change the leading term: SelectSwap's leading cost depends on address count and output width, not duplicate-row elimination.

## Decision

**No-go on implementing this clean SelectSwap variant for the score objective.** The score screen uses the verifier's whole-task formula: neither width-fitting block size reaches the 4,500-Toffoli gate, and larger blocks violate the ANGLES width cap. The `3,468`-Toffoli expectation in `exp-061` is a target gate with no construction behind it, not a result. Reopen only with a concrete circuit that preserves arbitrary-target XOR behavior and measures at most 4,500 static Toffolis per pass, then passes cleanup, padding, and the official verifier.

This is a cost screen, not a proof that no structured or dirty-ancilla QROM can help. The estimates use the paper's upper bound converted to Toffoli-equivalents and must not be presented as measured circuit counts.
