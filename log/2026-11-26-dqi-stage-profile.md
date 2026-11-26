---
date: 2026-11-26
title: DQI source stage cost profile
status: analysis_only
---

# DQI source stage cost profile

I downloaded Tony Li's public [Apache-2.0 task-generator dataset](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators)
into ignored staging and verified all 88 source files against the fingerprint
pinned by exp-074. The DQI release circuit hash also matches `4b572141…`.

The stream profile counted `318,972` static Toffoli-like instructions across
`69,782,188` circuit instructions, matching the dataset release README. The
source assembly also contains `54,145` register metadata lines. The three
largest stages are `decoder_return` (`109,515`),
`quantum_decoder_to_field_1` (`90,766`), and
`field_2_to_root_1330_phase` (`77,036`). Together they account for `277,317`
static Toffoli-like gates. All four D16 substitutions account for only `850`.

Exp-074's source-owned DQI mean is `316,131.22` Toffolis. At `Q=900`, the
current leader-equivalent gate is `278,742.57`, a required mean reduction of
`37,388.65`. That gap is `34.14%` of `decoder_return`'s static count; this is a
scale comparison, not an exact gate-deletion requirement. Static counts do not
predict the verifier's mean.

The first `decoder_return` follow-up scanned 19,804,589 assembly instructions,
including 107,422 CCX and 2,093 CCZ gates. It found zero identical Toffoli-like
pairs that could be canceled by adjacency or by commuting across gates on
disjoint wires. Close this generic peephole screen; a future candidate needs an
algorithm-level reversible-uncompute change with a credible path to at least
`37,389` mean-Toffoli savings before a private full-verifier run.

This remains static inspection only: no circuit was built, no verifier was
run, and no candidate was made. The full stage table and source hashes are in
the [evaluation receipt](../evals/2026-11-26-dqi-stage-profile.json).
