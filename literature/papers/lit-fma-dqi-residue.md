---
id: lit-fma-dqi-residue
title: "FMA evaluator to DQI scan residues"
year: 2026
tasks: dqi
relevance: "A direct FMA row does not replace the scanner's derivative-aware residue conversion"
read: 2026-11-23
---

# FMA evaluator to DQI scan residues

## Required map

The DQI paper states the Forney relation: at an error root `β`, the error value
is `eβ = -Ω(β)/σ′(β)` (Eq. 15, Sec. III.4). The minus sign vanishes in
characteristic two. [Khattar et al., arXiv:2510.10967v2](https://arxiv.org/html/2510.10967v2)

The local FMA sample construction uses `Φ(X) = ∏(X+j)`, `j=0..69`; its
evaluator therefore has root values `ΩΦ(β) = eβ β Φ(β) σ′(β)` on the
non-sample roots. The scanner instead phases using `A(β)/(β Pscan(β))`, so
its required residue numerator satisfies `Ascan(β) = eβ β Pscan(β)`.
Consequently, on this domain the unique degree-`< deg(σ)` numerator is

```text
Ascan ≡ ΩΦ · Pscan · Φ⁻¹ · (σ′)⁻¹  (mod σ).
```

`Pscan` is the degree-70 product of the 35 quadratics in
[`extract.constants`](../../src/dqi/pro_q2_897/exp/decoder/extract.py);
`Φ` is the 70-linear-factor polynomial in
[`phase_compatibility.py`](../../experiments/exp-057/phase_compatibility.py).
The factors are data-dependent modulo `σ`, and errors on FMA sample nodes
need their separate prefix handling. Thus the FMA low-rank row is not a
drop-in scanner input. The scanner contract and constant-weighted phase are
in [`scan.py`](../../src/dqi/pro_q2_897/exp/scan/scan.py).

## Cost gate

The existing specialized `convert_safe` measures 69,220T forward and 70,342T
reverse at Q=879. The remaining v18 updates and scan already cost 174,685T,
so at the refreshed 210,868.74T score-equivalent gate the forward conversion
can use at most 36,183T **before** output and cleanup. A direct long reduction
of a product of degree at most 104 modulo a degree-35 locator takes up to
70×35 = 2,450 variable field products (roughly 103kT at the project's 42T GF(2^12)
multiplier, recorded in the [multiplier frontier](lit-gf212-rank-frontier.md)),
before computing either modular inverse. This is a conservative generic
operation-count screen, not a lower bound; a structured fused recurrence could
be cheaper, but no such construction is established here.

The one-pattern bridge screen confirms the direct low-rank FMA row fails the
phase check while the canonical pair passes. The full measured split and gate
are in the [bridge receipt](../../evals/2026-11-23-exp057-fma-convert-scan-v19.json)
and [cost receipt](../../evals/2026-11-23-exp057-convert-cost-split.json).

**No-go on dropping `CONVERT` by wiring the current FMA row directly into the
scanner.** Reopen only with an exact reversible map or fused recurrence that
produces `Ascan`, measures below 36,184T including its uncomputation, and
passes the phase/cleanup gates. This is not a proof that no such recurrence
exists.
