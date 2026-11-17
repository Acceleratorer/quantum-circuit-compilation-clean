---
id: lit-eea-dialog-fit
title: "Reversible EEA Dialog: fit for the current DQI decoder"
year: 2025
tasks: dqi
relevance: "High-impact architecture checked; direct Dialog port is a Toffoli-cost no-go"
read: 2026-11-18
---

# Reversible EEA Dialog: fit for the current DQI decoder

## Source claims

Khattar et al. give two reversible Reed–Solomon decoder paths. The explicit path keeps the Bézout polynomials; the implicit “Dialog” path stores the division-free EEA trace and replays it to evaluate the locator polynomial and derivative. Their Table 5 gives leading-order quantum–quantum (QQ) field multiplications:

| Decoder phase | Explicit Bézout | Implicit Dialog |
|---|---:|---:|
| EEA / key equation | `3 n^2` | `n^2` |
| Chien + Forney | `0` | `2 m n` |
| Total | `3 n^2` | `2 m n + n^2` |

The explicit path instead has `m n` quantum–classical (QC) multiplications in Chien/Forney. For binary extension fields these QC products are Clifford-only, while QQ products consume Toffolis; the paper therefore says the explicit path is substantially cheaper in its target regime. For its illustrative `m=4095, n=70` parameters, the table implies 14,700 explicit QQ products versus 578,200 implicit QQ products. This is a calculation from the paper’s leading-order formulas, not a measured circuit result. [Khattar et al., §§II.2, II.4, Table 5](https://arxiv.org/html/2510.10967v1)

The Dialog is not a local replacement for an EEA subroutine: the decoder must preserve and replay the trace through all `m` Chien/Forney evaluations. The paper’s 5.72-million-Toffoli estimate is for its own `(m=4095,n=70,b=12)` OPI design and Qualtran accounting, so it is not a direct benchmark against the competition verifier.

## Fit to this workspace

The owned DQI entry point is specialized: [`final_decoder/decode.py`](../../src/dqi/pro_q2_897/final_decoder/decode.py) builds 34 head pairs, runs a custom in-place `synthesize`/`undo` path, then converts and scans. It is not a direct implementation of either paper EEA architecture. The current portfolio milestone records a DQI-only cost target near `249.33e9`, versus the retained candidate’s `347.90e9`, so a useful change must cut about 28.3% of DQI cost.

## Decision

**No-go on directly porting Dialog for this submission.** In the paper’s binary-field decoder, Dialog trades a small reduction in EEA products for `2mn` non-Clifford QQ products during evaluation; its own comparison favors explicit Bézout access. No mapping from Dialog to this specialized generator has been shown to remove enough work to overcome that cost. Revisit only if a concrete hybrid can be counted against the current generator before implementation and predicts a large net reduction in both verifier cost and failure risk.

This is a screening conclusion, not a proof that no hybrid or further EEA optimization exists. The paper’s leading-order model and parameters differ from the competition circuit, so exact counts require a faithful reversible implementation and official verification.
