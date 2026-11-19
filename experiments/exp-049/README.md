---
id: exp-049
title: FMA split-state information screen
task: dqi
tests: exhaustive small-field enumeration in fma_state_compression.py
direction: D-004
status: feasibility_screen
date: 2026-11-19
result: complementary FMA rows can be reconstructed classically from the normalized low-rank row and common-zero samples; reversible cost remains unproven
---

# FMA split-state information screen

## Question

Can a pristine FMA input block be replaced by only the updated `(d,g)` pairs
for the right block, without retaining any information from the original
input?

## Method

Implement the paper's sequential modular-approach basis update over small
binary extension fields. For every input tuple, compute the left-block basis,
apply it to the pristine right inputs (`g=1`), and count how many original
tuples map to each right state. Assertions check that each basis row satisfies
the key-equation constraints and that its determinant is a nonzero scalar
multiple of the processed-point polynomial. The enumeration is exhaustive for
each listed field and block size.

## Results

| Field | Split | Inputs | Distinct right states | Largest preimage | Minimum side information |
|---|---:|---:|---:|---:|---:|
| GF(4) | 2+2 | 256 | 147 | 6 | 3 bits |
| GF(8) | 3+3 | 262,144 | 166,061 | 29 | 5 bits |
| GF(8) | 4+2 | 262,144 | 3,969 | 97 | 7 bits |
| GF(8) | 4+4 | 16,777,216 | 10,486,775 | 65 | 7 bits |

`minimum side information` is `ceil(log2(maximum preimage))`; it is the number
of bits needed to distinguish the largest fiber when the right state is fixed.
The map is therefore not reversible if the original input and all side
information are discarded.

## Exact verifier-syndrome input map

The official verifier supplies `S_k = sum_j e_j beta_j^(k+1)`, with
`beta_j = alpha^j` (see `verify_submission_dqi.py`). For distinct FMA points
`omega_i` in `GF(2^m)`, define

```text
P(x)   = product_i (x + omega_i)
Q_i(x) = P(x) / (x + omega_i)
d_i    = sum_k coefficient_k(Q_i) * S_k
g_i    = 1
```

This is an invertible linear transform: `Q_i(omega_l)` is zero for `l != i`
and nonzero for `l == i`. For an error locator
`Lambda(x) = product_j (x + beta_j)`, the transformed samples satisfy
`d_i * Lambda(omega_i) + Z(omega_i) = 0`, where

```text
Z(x) = sum_j e_j * beta_j * P(beta_j) * Lambda(x)/(x + beta_j)
```

and `degree(Z) < number_of_errors`. The polynomial quotients handle errors at
an FMA point as well, without dividing by zero. This establishes the exact
classical input transform for FMA on the verifier's power syndromes. It does
not provide a reversible circuit schedule. The paper's Algorithm 6 uses
structured points for its fast divide-and-conquer evaluation and states that
FMA can handle non-power-of-two redundancy, but does not spell out a
reversible 70-symbol schedule or its resource count ([Tang and Han,
arXiv:2207.11079](https://arxiv.org/abs/2207.11079)).

The verifier's installed `GF2Field(12)` uses modulus `0x1053` and primitive
element `2`. In this polynomial basis, `omega_i = i` for `i=0..127` is a
7-dimensional additive subspace, and the first 70 points split into aligned
affine blocks `64+4+2`. The 70-symbol screen now verifies that composing the
three generic modular bases on those blocks gives the same minimum-rank basis
as processing all 70 constraints sequentially. This validates the classical
block boundaries only; it does not implement Algorithm 6's fast evaluation
and interpolation or provide a reversible schedule. The
direct syndrome map above produces a valid WB sample vector for the same
locator, but it does not reproduce the appendix's `u_1` values.

`verify_70_valid_error_patterns()` checks deterministic verifier-form syndromes
at error weights 1, 31, and 35. The direct basis and both trees (`38+32` and
`64+4+2`) recovered the exact monic locator and evaluator polynomials in all
six cases. This checks classical decoding on three valid inputs; it is not
exhaustive and does not verify a quantum circuit.

In each case, the materialized 38-point left basis contains 79 GF(2^12)
coefficients (948 qubits), already above `Q=890`. The ordinary schedule that
keeps the whole coefficient matrix cannot fit; a viable version must stream or
reuse that state in place. This only rules out full matrix materialization.

The script also tallies the data-dependent field products for one proposed
fast tree, `64+(4+2)`. It counts four products per right-side sample when
applying a 2x2 basis and eight products per evaluation point for a naive 2x2
matrix product. The FFT/IFFT and fixed-coefficient transforms are linear and
therefore omitted from the Toffoli tally. This gives 5,132 forward GF(2^12)
products, or 215,544 Toffolis at the in-tree 42-Toffoli multiplier cost. This
is only the FMA basis subtotal. The in-tree multiplier supports
measurement-based erasure of standalone products at zero additional
Toffolis ([`field.py`](../../src/dqi/pro_q2_897/exp/arithmetic/field.py)),
but a complete schedule still needs to show how it cleans rank/branch history
and accounts for root scan and phase extraction. The subtotal does not
establish that the decoder resource gate passes.

The separate balanced-split count is reproducible with
`estimate_minimum_70_fma_products()`. It minimizes the recurrence over every
split `n=a+b`, with `P(1, pristine)=P(1, updated)=0`:

```text
P(n, pristine) = min(P(a, pristine) + P(b, updated) + 2b + 7(n+1))
P(n, updated)  = min(P(a, updated)  + P(b, updated)  + 4b + 7(n+1))
```

The `2b`/`4b` terms apply the left basis to pristine/updated right samples;
`7(n+1)` counts seven field products per 2x2 matrix-composition point. The
minimum is `P(70, pristine)=4,166` at `38+32`, including `P(38, pristine)=1,961`
and `P(32, updated)=1,644`. At 42 Toffolis per product plus the existing
45,045-Toffoli scan, the subtotal is 220,017, leaving 39,930 under the saved
259,947 gate. This remains a count only: it excludes phase extraction and
does not prove a ≤50-qubit liveness schedule.

The exhaustive small-field check verifies that the minimum-rank FMA basis
returns the true locator for every valid error pattern, then measures
collisions in `(branch history, final right-block state)`:

| Field | FMA points | Valid patterns | Locator failures | Split | Largest fiber | Extra bits |
|---|---:|---:|---:|---:|---:|---:|
| GF(4) | 4 | 37 | 0 | 2+2 | 1 | 0 |
| GF(4) | 4 | 37 | 0 | 3+1 | 3 | 2 |
| GF(8) | 6 | 13,084 | 0 | 3+3 | 7 | 3 |
| GF(8) | 6 | 13,084 | 0 | 4+2 | 10 | 4 |

For GF(8), every error support and nonzero error-value assignment through
weight 3 is enumerated. These valid-domain fibers are smaller than the
arbitrary-input fibers above, but the state still is not injective. Neither
small field gives a bound for the 70-symbol competition instance.

## Branch-history variant

The follow-up screen also records one branch bit for every step of the
sequential modular update, together with the final right-block `(d,g)` state.
This still does not make the map injective in the exhaustive GF(8), six-symbol
cases:

| Split | Distinct combined states | Largest preimage | Extra bits beyond branch history |
|---:|---:|---:|---:|
| 3+3 | 212,206 | 21 | 5 |
| 4+2 | 33,930 | 63 | 6 |

So one stored branch bit per symbol is not a complete reversible encoding even
for these small cases. These results do not establish the side-information
bound at 70 symbols.

An exact vectorized screen extended the arbitrary-input enumeration to all
`GF(8)^8` inputs for two more splits. It records every branch bit and the final
right-block state, then compares selected entries with the sequential reference:

| Split | Mean fiber | Largest fiber | Additional label bits |
|---:|---:|---:|---:|
| 6+2 | 16 | 2,177 | 12 |
| 7+1 | 1,024 | 114,940 | 17 |

The vectorized reference checks pass for both cases. These exact small-field
results show the size of the remaining collision label for these inputs; they
do not bound the 70-symbol fiber or prove that a 52-qubit label is enough.
`screen_branch_history_vectorized()` reproduces the screen using the pinned
NumPy dependency.

The same screen also retained the first three left-side `d` samples before
measuring the remaining fiber:

| Split | Retained samples | Largest residual fiber | Label bits | Total side width |
|---:|---:|---:|---:|---:|
| 6+2 | 3 | 64 | 6 | 15 bits |
| 7+1 | 3 | 448 | 9 | 18 bits |

For the 70-symbol root, retaining three 12-bit samples costs 36 qubits. Under
`Q=890`, that leaves at most 16 qubits for the remaining label and overlapping
scratch after the 64 right-pair words and 70 branch bits. The target screen is
therefore a maximum residual fiber of at most `2^16`; the 70-symbol case is
still unbounded.

A projective-state check exhaustively screened the same `GF(8)^8`, `6+2`
domain while retaining those three samples. Encoding each right pair as
`d/g` (with an infinity sentinel) reduced its stored state by 4 bits, but the
largest fiber grew from 64 to 343, raising the label from 6 to 9 bits. The net
state-plus-label saving was only 1 bit in this small case. The screen discards
pair scale and does not provide a 70-symbol bound or a reversible encoding.

A separate exhaustive valid-domain screen covered all 97,119 GF(8), eight-point
error patterns through weight 4 while retaining the first three left `d`
samples. Locator recovery had zero failures; the largest fibers were 1 for
split 4+4 and 7 for split 5+3, so these two small cases need 0 and 3 extra
label bits. This is specific to GF(8) and eight points; it does not bound the
70-symbol fiber. To run this slower screen alone:

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -c `
  "import sys; sys.path.insert(0, 'experiments/exp-049'); import fma_state_compression as f; print(f.screen_valid_error_domain(3, 0b1011, 4, 3))"
```

## Complementary row reconstruction

Given a normalized low-rank row `(W,N)`, let `G=gcd(W,N)`, `A=W/G`,
`B=N/G`, and `P(x)=product_i(x+point_i)`. Extended Euclid gives
`U*A+V*B=1`; therefore `(V*(P/G), U*(P/G))` is a complementary row with
determinant `P`. The remaining freedom is `(V*P/G + A*t, U*P/G + B*t)`.
The experiment interpolates `t` at common zeros, then uses polynomial
remainders to choose a representative with the required complementary rank.
Those are the only original left-side `d_i` values needed by this
reconstruction. One leading coefficient of the stored row is fixed to one and
need not be stored.

`verify_complementary_row_reconstruction()` checks determinant, key-equation
constraints, and the complementary-rank sum for every GF(4), four-point input,
256 deterministic GF(8), eight-point inputs, and 256 deterministic GF(2^12),
38-point inputs. For verifier-form syndromes at weights 1, 31, and 35, it also
reconstructs the left basis, updates the untouched right samples, and checks
that the composed normalized low row matches the direct 70-point basis for
three splits:

| Error weight | Split | Normalized left-row words | Exception samples | Right input words | Persistent qubits | Remaining under Q=890 |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4+66 | 2 | 0 | 66 | 816 | 74 |
| 1 | 8+62 | 2 | 0 | 62 | 768 | 122 |
| 1 | 38+32 | 2 | 0 | 32 | 408 | 482 |
| 31 | 4+66 | 4 | 0 | 66 | 840 | 50 |
| 31 | 8+62 | 8 | 0 | 62 | 840 | 50 |
| 31 | 38+32 | 38 | 0 | 32 | 840 | 50 |
| 35 | 4+66 | 4 | 0 | 66 | 840 | 50 |
| 35 | 8+62 | 8 | 0 | 62 | 840 | 50 |
| 35 | 38+32 | 38 | 0 | 32 | 840 | 50 |

These checks establish classical composition only. The state count excludes
reversible scratch, branch history, and phase correction.

## Sampled split-cost screen

The current score-equivalence gate is `T <= 256,943` at `Q=890` and
`R=1.1912605`. A seeded dynamic-taint pass on the verifier-form `e=31` and
`e=35` samples counted variable field products and inversions in complementary
row reconstruction. The estimate uses the source-owned 42-Toffoli GF(2^12)
product, 66-Toffoli inverse, and 45-Toffoli inverse erasure. FMA product counts
come from `minimum_fma_product_cost()` with the first split fixed; the scan
adds 45,045T. `poly_divmod()` reuses the inverse of the divisor's leading
coefficient across that division's quotient terms.

| Split | FMA products | Reconstruction products | Reconstruction inverses | Estimated T incl. scan | Margin to 256,943T |
|---:|---:|---:|---:|---:|---:|
| 1+69 | 4,864 | 15 | 7 | 250,740 | 6,203 |
| 2+68 | 4,810 | 28 | 7 | 249,018 | 7,925 |
| 3+67 | 4,763 | 65 | 9 | 248,820 | 8,123 |
| 4+66 | 4,720 | 71 | 8 | 247,155 | 9,788 |
| 5+65 | 4,681 | 144 | 10 | 248,805 | 8,138 |
| 6+64 | 4,648 | 145 | 9 | 247,350 | 9,593 |
| 7+63 | 4,615 | 253 | 11 | 250,722 | 6,221 |
| 8+62 | 4,585 | 205 | 10 | 247,335 | 9,608 |
| 12+58 | 4,478 | 463 | 12 | 253,899 | 3,044 |
| 16+54 | 4,390 | 649 | 14 | 258,237 | -1,294 |
| 18+52 | 4,354 | 919 | 15 | 268,176 | -11,233 |
| 38+32 | 4,166 | 3,877 | 25 | 385,626 | -128,683 |

The total is `42 * (FMA products + reconstruction products) + 111 *
reconstruction inverses + 45,045`. The two high-weight samples give the same
counts except at 16+54, where the table keeps the larger estimate. A separate
1,024-shot screen at e=31 and e=35 found a common-zero correction in 2 shots;
the representative paths in the table need none. This is a sample-path
screening estimate, not a reversible circuit or a bound: it omits branch/
control gates, phase correction, and a ≤50-qubit scratch schedule. The 4+66
split is the best tested split, with 9,788T of headroom before those omitted
costs.

This is a classical reconstruction and a persistent-state count. It does not
show that extended Euclid and the correction solve can be computed reversibly
within the remaining 50 qubits or the Toffoli budget. The three verifier-form
weights are samples, not a bound over all 70-symbol inputs; no quantum circuit
or submission has been produced.

## Decision

The syndrome-to-FMA map and the complementary-row reconstruction are validated
classically on the cases above. The 4+66 sampled estimate is below the current
T gate, but its 9,788T margin must also cover branch/control, common-zero,
phase, and reversible cleanup costs. The samples do not establish a bound over all
70-symbol inputs or a ≤50-qubit schedule. No complete circuit, liveness proof,
official verifier run, or submission was produced.

For the count-minimizing 70-symbol split `38+32`, the 64 right-pair symbols
occupy 768 of the 840 syndrome-bank bits, leaving six field slots (72 bits)
plus the 50-qubit scratch budget for reversible history. Whether that capacity
is enough for the exact FMA transform is still unknown. The branch-history
screen above shows that storing one bit per sequential update is insufficient
by itself; an upper bound for the remaining history at 70 symbols is needed.
If all 70 branch bits are retained, the right-pair state plus branch history
uses 838 qubits, leaving an absolute 52-qubit ceiling for additional collision
labels and any overlapping scratch under `Q=890`. The label must be computed
reversibly; the small-field fiber counts do not establish that a ≤52-bit label
exists for 70 symbols.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' `
  experiments\exp-049\fma_state_compression.py
```
