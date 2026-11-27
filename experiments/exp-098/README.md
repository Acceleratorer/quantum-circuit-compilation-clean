---
id: exp-098
title: ACC1 shared-denominator mapping to QV2
task: dqi
tests: source-text audit
status: closed_no_go_mapping_and_gate
date: 2026-11-28
result: The public ACC1 idea claims about 31,600 T saved at a 24-qubit price, but QV2 already carries one shared 24-bit scale through its node extractor; a direct transfer is not a new construction and still leaves about 26,262 T above the DQI gate.
---

# exp-098 — ACC1 shared-denominator mapping to QV2

This audit checked David Pilny's Apache-2.0 ACC1 design against the source-owned
QV2 generator as source text only. The downloaded public notebook was not
executed and no circuit was downloaded or run.

## Mapping

ACC1 keeps one 24-qubit denominator accumulator across projective nodes. QV2's
`src/dqi_v8/v8_model.py` already starts each node from the carried scale and
sets `c = n` after the node. The production `confluent_ext.py` follows the same
layout with its persistent `carry` word and shared normalization path. ACC1's
main mechanism is therefore already present in the QV2 source family; adding a
second accumulator would duplicate state rather than replace a measured QV2
stage.

## Gate arithmetic

The ACC1 note claims roughly `31,600 T` saved and `+24 Q` (its worked example
goes from `Q=891` to `Q=915`). Applied optimistically to the measured QV2
baseline (`Q=889`, mean `333,238.013 T`), that would be `301,638.013 T` before
any integration overhead. It remains about `26,262 T` above the current
`275,376 T` DQI tie gate. The direct width would be `Q=913`, above the 900-qubit
limit; even a hypothetical fit at `Q=900` has no proof of the required 13-qubit
compression.

The ACC1 notebook also says it does not contain a complete decoder, so its
31,600-T figure is not a QV2 measurement. No private kernel was launched.

The machine-readable receipt is
`evals/2026-11-28-exp098-acc1-qv2-mapping.json`.
