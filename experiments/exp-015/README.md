---
id: exp-015
title: Public 392k-Toffoli DQI decoder with 4089-angle chemistry
task: all
tests: [C-019]
direction: D-004
status: ready_for_submit
result: local geometric mean 25.41253; DQI full 102400-shot PASS with zero errors
---

# Public 392k-Toffoli DQI candidate

This experiment promotes the public `maoxin123/qcc-v22-a-392k-toffoli-dqi-decoder` output as the current submission candidate.

## Candidate members

| Member | SHA-256 prefix | Evidence |
|---|---|---|
| `invsqrt.kmb` | `6c6a734dbcb693bb` | public 62-qubit frontier |
| `dqi.kmb` | `4c81b7263c0b4856` | public 392k-Toffoli decoder dataset |
| `dfthcsos/*` | `f21b8a8725c342eb` for `submission.npz` | 4089-Toffoli angle-loader portfolio |

The local archive is kept outside Git at `artifacts/submission_v22_392k.zip`; its receipt is `receipt.json`.

## Verification evidence

- DQI: official verifier PASS, 102,400 shots, zero value errors and zero phase errors, 892 qubits.
- Invsqrt: official verifier PASS, 62 qubits, cost `93,863.357262`.
- Chemistry: official verifier PASS, 427 qubits, 14,856 Toffolis, cost `297,557,548.713`.
- Reported local geometric mean: **25.41253**, above the previous 25.40482 submission.

## Reproducibility and eligibility

The DQI dataset publishes a compiled `dqi.kmb.xz` without its generator. That is sufficient for a leaderboard probe, but exact generator/source delivery remains an eligibility risk for a prize claim. Keep the source kernel, dataset slug, hashes, and verifier log pinned until a generator is recovered or the host clarifies the rule.

## Submission state

The archive is ready, but the Kaggle account reported five submissions today and zero remaining on 2026-11-13. Submit after the next quota reset and append the Kaggle submission reference and public score to `receipt.json`.

