---
id: exp-021
title: Verify 1f19ecca7044 chemistry family
task: dfthcsos
tests: [C-025]
direction: D-004
status: rejected_worse_score
date: 2026-11-13
result: the 4132-static-Toffoli family passes the official 78080-shot verifier but costs more than the retained e9cffb84 chemistry member
---

# 1f19ecca7044 chemistry family

The Apache chemistry corpus contains a 15-loader family with factorization `1f19ecca7044`. I checked the unchanged competition verifier against the converted `.kmb` loaders and compared its full block-encoding cost with the retained `e9cffb84` chemistry member.

## Official verification

- status: `PASS`
- shots: `78,080` (`--shots-per-address 64`)
- score: `298,998,656.7697932`
- lambda_eff: `46.91350973464301`
- Toffoli count: `14,926`
- qubits: `427`
- error_1: `0.017425629447271176`
- error_2: `0.019999974863085707`
- static loader sum: `4,132` (`R=8`, `C=44`, `brot=8`, `J=5`)

The current v24 chemistry member `e9cffb84` scores `297,237,044.9509761`. Replacing it with this family changes the local v24 estimate from `25.449573528079686` to `25.39949459072615` (`-0.05007893735353619`), so the candidate is rejected.

## Pinned inputs

- family key: `1f19ecca7044`
- factorization SHA-256: `c615d7c793252a2a5d70167b391f416c462988ca11997b638e1aee50c1a33f27`
- local source directory: `apache_full/circuits/chemistry/1f19ecca7044`
- all loader and factorization hashes are recorded in `receipt.json`

No submission archive was created from this rejected candidate.
