---
id: exp-049
title: FMA split-state information screen
task: dqi
tests: exhaustive small-field enumeration in fma_state_compression.py
direction: D-004
status: feasibility_screen
date: 2026-11-19
result: exact syndrome-to-FMA samples recover all screened locators, but the split state still collides
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
not provide a reversible circuit schedule. The paper defines this FMA at
[Tang and Han, arXiv:2207.11079](https://arxiv.org/abs/2207.11079),
Algorithm 6. Its fast divide-and-conquer evaluation uses structured points;
the small-field screen runs the generic sequential update on `0..n-1`. It does
not yet validate the paper's fast recursion for 70 arbitrary-redundancy
syndromes or its 70-symbol product count.

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

## Decision

The syndrome-to-FMA map is now exact, but this closes only the shortcut that
keeps the right pairs and branch history while erasing everything else. A
reversible schedule could retain more history in the unused input slots and 50
scratch qubits. The small-field valid-domain fibers do not bound the
70-symbol maximum preimage. No complete circuit, 70-symbol liveness proof,
verifier run, or submission was produced.

For the count-minimizing 70-symbol split `38+32`, the 64 right-pair symbols
occupy 768 of the 840 syndrome-bank bits, leaving six field slots (72 bits)
plus the 50-qubit scratch budget for reversible history. Whether that capacity
is enough for the exact FMA transform is still unknown. The branch-history
screen above shows that storing one bit per sequential update is insufficient
by itself; an upper bound for the remaining history at 70 symbols is needed.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' `
  experiments\exp-049\fma_state_compression.py
```
