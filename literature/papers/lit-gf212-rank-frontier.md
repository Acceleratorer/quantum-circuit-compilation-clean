---
id: lit-gf212-rank-frontier
title: "GF(2^12) multiplier bilinear-rank frontier"
year: 2026
tasks: dqi
relevance: "42-term upper bound; public sources checked for sub-42 formulas"
read: 2026-11-18
---

# GF(2^12) multiplier bilinear-rank frontier

The published survey by Ballet et al. lists the best-known symmetric bilinear-complexity bound as `μ_sym_2(12) ≤ 42`; this is an upper bound, not an optimality proof. It also says exact values are known only in a few small cases. A 2026 Cotardo–Zullo preprint develops explicit decompositions only for extension degrees 2, 3, and 4, so it supplies no degree-12 candidate. ([Ballet et al., 2019, Table 2 and §9.1](https://arxiv.org/pdf/1906.07456); [Cotardo & Zullo, 2026](https://arxiv.org/abs/2605.12295)).

The source-available Jain preprint gives an explicit multiplier for the Classic McEliece field `x^12 + x^3 + 1` with 210 total gates: **78 AND + 132 XOR**. It beats a simple polynomial-multiply-plus-reduction baseline, but not 42 AND terms. The author explicitly makes no optimality claim and says the literature search was not systematic. ([Jain, 2026 preprint](https://www.researchgate.net/publication/415561348_Smaller_Gate_Counts_for_Polynomial-Basis_Binary-Field_Multipliers); [circuit repository](https://github.com/Swapnil-jain/gf2m-circuits)).

The project’s current GF(2^12) audit uses modulus `0x1053` (`x^12 + x^6 + x^4 + x + 1`), while Jain’s artifact uses `0x1009` (`x^12 + x^3 + 1`) ([local audit](../../src/dqi/pro_q2_897/exp/convert/hankel_check.py)). These are isomorphic degree-12 binary fields. A basis change conjugates the input and output linear maps, so the bilinear-term count is preserved, though the bit-level circuit needs extra XOR/CNOT work. This is an algebraic inference from field isomorphism, not a claim that the released gate list directly matches the competition basis.

**Finding:** this targeted search found no published or source-available GF(2^12) bilinear decomposition with fewer than 42 terms. It does not establish that none exists, or that 42 is the exact tensor rank. Keep 42 as the best located public upper bound; do not call it optimal. AND/rank terms in these classical bilinear formulas are also not automatically equal to a competition circuit’s final Toffoli count after reversible synthesis and measurement-based uncomputation.

## 2026-11-27 Type-I normal-basis screen

GF(2^12) does admit a Type-I optimal normal basis: 13 is prime and 2 has order 12 modulo 13. That does **not** give a 23-Toffoli multiplier. The normal-basis multiplication complexity counts the sparse coordinate formula; a quantum multiplier still has quadratic Toffoli cost in the cited construction ([Kwon et al., 2022](https://eprint.iacr.org/2022/1095.pdf)). Also, changing basis applies invertible linear maps to the input and output of the same multiplication tensor, so its bilinear rank is invariant (algebraic inference). The project's current polynomial-basis tensor uses 42 rank terms in [`field.py`](../../src/dqi/pro_q2_897/exp/arithmetic/field.py). **Decision: no-go for a basis-only rewrite.** Reopen only with an explicit lower-rank decomposition or a reversible implementation whose measured Toffoli count improves on the existing 42-term kernel.

Primary normal-basis source: [Reducing the Complexity of Normal Basis Multiplication, §6](https://eprint.iacr.org/2014/687.pdf).
