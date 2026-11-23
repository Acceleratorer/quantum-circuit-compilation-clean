# DQI contract and algorithm gate

Captured 2026-11-23 00:52 UTC. This is a static audit; no downloaded notebook
or circuit was executed.

## Official DQI contract

Kaggle's [`verify_submission_dqi.py`](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/data)
requires 70 quantum syndrome registers and 4,095 classical MBUC-mask
registers. For decoded error word `e` and masks `M`, the circuit must apply
`(-1) ** sum_j popcount(e[j] & M[j])`, restore all syndrome inputs, and clean
every other qubit. `Z_POW` is disallowed. Scoring uses
`R(eps_plus) * Q^2 * T`; default verification uses 102,400 shots.

The files were fetched with Kaggle CLI into the untracked workspace staging
folder `tmp/kaggle-verifier-dqi/` and inspected as text. SHA-256:

- `verifiers/dqi/verify_submission_dqi.py` — `f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65`
- `verifiers/dqi/dqi_reference_circuit.py` — `2b8e1b80a806157c333a7e308eaf2499ee09de499efbc05875202c327959959e`

## Candidate implication

Exp-057 v15's `Q=889`, `T=19,004` result checks a syndrome-derived checksum
after prefix decoding and 66 matrix actions. Its receipt explicitly omits the
MBUC-dependent phase, full DQI cleanup, and official verifier. It is a useful
component result, not a DQI candidate. The missing phase must connect the
decoded error values/locations to the 4,095 `M_j` inputs, then reverse the
computation while restoring all 70 syndromes.

Do not add the 19,004T checksum count to the independent 202,075T FMA
projection; there is no composed ledger showing overlap or compatibility. A
candidate must measure the complete `Q`, `T`, phase, and cleanup schedule and
fit the current score-equivalence gate (`Q <= 890`, mean `T <= 212,110.59` at
`R=1.1912605`) before the official verifier run.

## Alternative algorithm: no-go

Gu et al.'s primary-source DQI implementation reports 141,071T for forward
Berlekamp–Massey, 86,176T for its reverse, 15,246T for the evaluator each way,
44,470T for half-degree Euclid each way, 1,583T for normalization each way,
and 92,552T for the position scan. The displayed stage counts sum to
442,397T; the peak stage width is 1,837 qubits. The authors report a sampled
rare-window error rate of `3.8e-5`. Even before its repetition overhead, the
published BM route misses both current DQI gates, so do not port it wholesale.
See the [author's primary-source implementation](https://andigu.github.io/projects/uncompute/dqi-reed-solomon.html).

## Next gate

First prove classically that the exp-057 state can produce the official
MBUC-dependent phase for verifier-distributed inputs. Only then build the
phase/cleanup circuit and measure the fully composed budget. If the output
mapping or full budget fails, close this FMA direction instead of adding more
component screens.
