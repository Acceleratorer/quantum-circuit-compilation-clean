---
id: exp-049
title: FMA split-state information screen
task: dqi
tests: exhaustive small-field enumeration in fma_state_compression.py
direction: D-004
status: feasibility_screen
date: 2026-11-19
result: the updated right block alone is non-injective; a reversible split must preserve side information
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

## Decision

This closes only the shortcut that keeps the right pairs and erases everything
else. It does not rule out a compressed FMA schedule: the 70-symbol circuit may
retain history in the unused input slots and 50 scratch qubits, and the small
field results do not bound the 70-symbol maximum preimage. No full circuit,
70-symbol liveness proof, verifier run, or submission was produced.

For the count-minimizing 70-symbol split `38+32`, the 64 right-pair symbols
occupy 768 of the 840 syndrome-bank bits, leaving six field slots (72 bits)
plus the 50-qubit scratch budget for reversible history. Whether that capacity
is enough for the actual FMA transform is still unknown.

## Reproduce

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' `
  experiments\exp-049\fma_state_compression.py
```
