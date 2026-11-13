# DQI cutoff-17 module

The local builder is kept in `artifacts/build_cutoff17_local.py` and is not
copied into the submission archive. It patches the cutoff parameter in memory,
leaving the pinned source receipts unchanged, then emits the 889-qubit
`dqi_cutoff17.kmb` artifact.

The build contract is recorded in `artifacts/dqi_cutoff17_build.json`; the
official 102,400-shot verification is recorded in
`artifacts/dqi_cutoff17_verify.log` and `evals/2026-11-13-dqi-cutoff17.json`.
