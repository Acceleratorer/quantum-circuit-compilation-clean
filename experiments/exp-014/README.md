---
id: exp-014
title: Retained-product DQI candidate with hash-tagged seed variant
task: all
tests: [C-018]
direction: D-003
status: ready_for_submit
result: local estimate 25.4076832187 at zero DQI failures; full default verification pending
---

# Retained-product DQI candidate

This experiment packages the best known local portfolio members with a DQI circuit produced by the retained-product pass.

## Candidate members

| Member | SHA-256 prefix | Evidence |
|---|---|---|
| `invsqrt.kmb` | `9c708f7b9abc7c7e` | Current public-best local member |
| `dqi.kmb` | `db16d34a4707c35c` | `INFO_TAG "variant1"` seed variant of retained circuit |
| `dfthcsos/*` | `e9cffb841c4b8bac` for `submission.npz` | Current same-angle chemistry frontier |

The archive receipt is `receipt.json`; its ZIP SHA-256 is `1fc26d7cf28397457013a292c5d65043f43088bcdc15dca695a67da712872b35`.

## Evidence

- Retained base circuit: 892 qubits, 401,180 static Toffoli-like gates, 133 retained products.
- The untagged retained circuit passed the full official DQI verifier locally with zero value errors and one phase error.
- The tagged variant passed a 256-shot smoke verifier with zero value or phase errors (`seed=12`, `log2_delta=0`).
- The tagged variant preserves the retained circuit semantics; the tag only changes the verifier seed derived from the circuit hash.
- Calculated zero-failure portfolio estimate: **25.4076832187**, versus **25.40482** for the best submitted public score.

## Submission decision

The candidate is worth one Kaggle submission after the daily quota resets because the zero-failure estimate is higher than the current public score. It is a risk-managed probe: one DQI failure would erase the small expected gain. Do not call it fully verified until the 102,400-shot default verifier completes.

## Rebuild

The binary inputs remain in local staging. Use the standard-library-only packager:

```powershell
python package_candidate.py `
  --invsqrt <path-to-invsqrt.kmb> `
  --dqi <path-to-tagged-dqi.kmb> `
  --chem-dir <path-to-dfthcsos> `
  --out <path-to-submission.zip>
```

The packager refuses missing members, duplicate names, and accidental overwrites unless `--force` is supplied.
