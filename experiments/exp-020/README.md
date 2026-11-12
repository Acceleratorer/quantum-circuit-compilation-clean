---
id: exp-020
title: Verify Atakan 328ced chemistry family
task: dfthcsos
tests: [C-024]
direction: D-004
status: rejected_worse_score
date: 2026-11-13
result: the 3045-static-Toffoli family passes the official 78080-shot verifier but costs more than the retained e9cff84 chemistry member
---

# Atakan 328ced chemistry family

The public `atakanaldemir/qcc-gap-3-residue-repair-and-c43-native-compiler`
release advertises an eleven-loader chemistry compiler with a lower static
angle count. I downloaded its 15 loaders and `submission.npz` from the
`asteriospanoras/qcc-circuit-atlas` dataset, converted the `.kmx` loaders to
the official `.kmb` format, and ran the unchanged competition verifier.

## Official verification

- status: `PASS`
- shots: `78,080` (`--shots-per-address 64`)
- score: `302,196,075.2036132`
- lambda_eff: `46.893661918626364`
- Toffoli count: `15,092`
- qubits: `427`
- error_1: `0.019999990015043493`
- error_2: `0.01999998999691989`
- submission hash: `b089ee6183ce749c4b771b8c6adc192ce0008b852849c74c037ee2004464b708`

The archive member currently used by v24, `e9cffb84`, scores
`297,237,044.9509761`. Replacing it with this family lowers the full hybrid
estimate from `25.4495735281` to `25.3095960912`, so the candidate is rejected.
The lower static angle count does not compensate for the factorization's
larger effective Hamiltonian cost.

## Pinned inputs

- factorization: `328cedb098839642e38e0f0df244bd35279a8b1d08ba28cb697d47c9b8ab9e4c`
- source notebook: [Atakan gap-3 compiler](https://www.kaggle.com/code/atakanaldemir/qcc-gap-3-residue-repair-and-c43-native-compiler)
- atlas: [QCC Circuit Atlas](https://www.kaggle.com/datasets/asteriospanoras/qcc-circuit-atlas)
- converted member hashes are recorded in `receipt.json`

No submission archive was created from this rejected candidate.
