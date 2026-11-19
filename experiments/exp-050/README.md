---
id: exp-050
title: Factorized FMA state payload
task: dqi
tests: exhaustive valid-pattern screens at small fields; targeted GF(2^12), 70-point cases
direction: D-004
status: information_bound_screen
date: 2026-11-19
result: the normalized minimum-rank row can be factored by its common divisor and paired with one source sample per common node, using at most 2e field words for e errors
---

# Factorized FMA state payload

## Result

For a valid error pattern with locator `W=Lambda` of degree `e` and evaluator
`N=Z`, let `G=gcd(W,N)`, `A=W/G`, and `B=N/G`. In the verifier's FMA input
map, `G` contains exactly the factors `(x+beta)` for error locations `beta`
that coincide with an FMA node. If `k=deg(G)`, store:

- the `k` lower coefficients of monic `G`;
- the `e-k` lower coefficients of monic `A`;
- `e-k` coefficients of `B`, padded to that width;
- one original FMA sample at each of the `k` common nodes.

The payload is `k + (e-k) + (e-k) + k = 2e` field words. Since `e<=35`, a
70-symbol DQI instance needs at most 70 words (840 qubits) for this payload.
For a node outside `G`, `A(node)` is nonzero and the original sample is
`B(node)/A(node)`. At a common node, the saved sample carries the error value
that `Z` cannot encode because the node polynomial vanishes there. Thus the
encoding reconstructs all 70 transformed samples on the valid-error domain.

The common-factor claim follows by evaluating `Z` at a locator root `beta_j`:
`Z(beta_j) = e_j beta_j P(beta_j) product_{l!=j}(beta_j+beta_l)`. Distinct
nonzero error locations and nonzero error values make this zero exactly when
`P(beta_j)=0`, meaning `beta_j` is one of the FMA nodes. The WB relation
`d_i W(node_i)+N(node_i)=0` then gives `d_i=B(node_i)/A(node_i)` away from
those common roots; at the common roots the saved samples supply the missing
values.

This is a storage-width result only. It does not give a reversible circuit for
finding `G`, splitting `W,N`, framing the variable degrees, reconstructing a
complementary row, or running the FMA recursion. It does not include rank
registers, branch/phase cleanup, workspace, or Toffoli cost, so it does not
prove `Q<=890` or the score gate.

## Screens

`fma_factorized_state.py` enumerates every valid error support and every
nonzero error-value assignment through `t=n/2` for GF(4), four points; GF(8),
six points; and GF(16), four points. For every case it checks that the
classical minimum-rank row matches the exact locator/evaluator, that `G` has
the expected common-node factors, that the packed payload reconstructs every
FMA sample, and that the encoding has no collisions.

| Field | Points | Valid patterns | Distinct encodings | Largest fiber | Max payload |
|---|---:|---:|---:|---:|---:|
| GF(4) | 4 | 37 | 37 | 1 | 4 words |
| GF(8) | 6 | 13,084 | 13,084 | 1 | 6 words |
| GF(16) | 4 | 23,851 | 23,851 | 1 | 4 words |

It also checks six targeted GF(2^12), 70-point cases: no errors, one error at
an FMA node, 31 errors outside the FMA nodes, 35 errors with four common-node
roots, 35 errors all at FMA nodes, and 35 errors outside the FMA nodes. These
cases all reconstructed every sample. Their payload widths were 0, 2, 62,
70, 70, and 70 words respectively. They are not an exhaustive 70-point proof.

Run the screen with the workspace virtualenv:

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' `
  'experiments/exp-050/fma_factorized_state.py'
```
