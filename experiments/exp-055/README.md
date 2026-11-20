---
id: exp-055
title: Factorized shape-tag field-growth screen
task: dqi
tests: exhaustive GF(8) and GF(16) four-sample domains; exhaustive 16^4 input subset under competition GF(2^12) arithmetic
direction: D-004
status: blockwise_shape_tag_rejected
date: 2026-11-20
result: >-
  The existing three-color shape map remains collision-free for pristine
  four-sample inputs, but fails after a valid 4+4 left-basis transformation.
  One exhaustive GF(8) transformed context has a five-color conflict graph.
---

# Factorized shape-tag field-growth screen

## Question

Does the three-color (two-bit) shape map found by the exhaustive GF(8) screen
still distinguish factorized payloads in larger fields and under the actual
competition field arithmetic?

## Result

The source-owned screen rebuilds the payload-conflict graph from the four-point
factorized codec. It exhausts all inputs in GF(8) and GF(16), then checks every
four-tuple over `0..15` using the competition field GF(2^12), modulus `0x1053`,
and points `0,1,2,3`.

| Arithmetic and input domain | Inputs | Conflicts | Minimum colors | Existing map collisions |
| --- | ---: | ---: | ---: | ---: |
| Pristine GF(8), exhaustive | 4,096 | 9 edges | 3 | 0 |
| Pristine GF(16), exhaustive | 65,536 | 9 edges | 3 | 0 |
| Pristine GF(2^12), values 0–15 | 65,536 | 8 edges | 3 | 0 |
| Transformed GF(8), one actual 4+4 context | 4,096 | 22 edges | 5 | 274 |
| Transformed GF(2^12), same context, values 0–15 | 65,536 | 0 edges | 1 | 0 |

Every packed label recovered its original right samples using the retained
left-basis context. The GF(8) transformed context used `left=(1,6,1,6)`,
right points `4,5,6,7`, and the rank pair produced by that left block, `(4,5)`.
Its fixed three-color map has 274 same-color payload collisions. For example,
payload `(5,7,0,0)` represents shape IDs 10 and 4, both color 0, for distinct
right inputs `(0,0,0,5)` and `(0,1,7,7)`. The exact conflict graph needs five
colors, so no two-bit coloring works for this transformed GF(8) domain.

The GF(2^12) transformed run checks the same 4+4 context for all 65,536
right-input tuples over values `0..15`. It finds no cross-shape payload
collisions in that subset, but 61 states are outside the current factorized
codec catalog. This does not establish the full GF(2^12) graph.

## Limits and next gate

The pristine-prefix color map cannot be repeated across transformed blocks:
the exhaustive GF(8) block counterexample rejects that mapping, and the
existing codec also omits transformed states where its normalized numerator
cofactor is zero. The GF(2^12) transformed run is only a `16^4` subset, so it
does not tell us whether a different 2-bit map works over the complete field.
Do not count this lead as a 34-qubit saving or use it in the 4+66 schedule.
Any replacement needs a complete transformed-state encoding and measured
width, Toffoli, phase, and cleanup costs.

Reproduce with:

```powershell
python -I .\experiments\exp-055\shape_tag_field_growth.py
```
