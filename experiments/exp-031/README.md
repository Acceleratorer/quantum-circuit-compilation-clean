---
id: exp-031
title: Atakan 46Q inverse with v17 chemistry and cutoff18 DQI
task: portfolio
tests: [C-034]
status: verified_ready_for_submit
date: 2026-11-13
result: source full PASS for inverse, chemistry fresh PASS, DQI exact full PASS receipt; projected local GM 27.2699718109
---

# Atakan 46Q inverse portfolio

This candidate keeps the retained cutoff18 DQI (`821bf8d15703`) and replaces
the inverse with Atakan's public `4560ac0c017b`. It also uses the lower-cost
chemistry refit `45621b0e3d36`. The 18-member archive is the exact output of
Atakan's notebook, with deterministic member hashes recorded in
[`receipts/member_hashes.json`](receipts/member_hashes.json).

## Evidence

- **Inverse:** source notebook receipt reports an unchanged official
  `200,540,928`-shot PASS, 46 qubits, score `78,765.63681893334`, and
  circuit SHA-256 `4560ac0c017bf6d1bf27c73320f2e30c247a2a18143d58ff92a601f8bc20b218`.
- **Chemistry:** independently re-run locally with the official verifier;
  PASS at `78,080` shots, score `296,008,772.34505755`, 427 qubits,
  14,776 Toffoli-like gates. Receipt: [`verify_chem.json`](receipts/verify_chem.json).
- **DQI:** exact hash `821bf8d15703c3e868a0099b0ab1438cfba664ab1bc6fec3210654099b672a3`;
  the source notebook preserves a full `102,400`-shot PASS with zero value and
  phase errors. Local static load confirms 889 qubits and 383,414 Toffoli-like
  gates. Receipt: [`atakan_reproduction_audit.json`](receipts/atakan_reproduction_audit.json).

The zero-failure projection is `27.269971810894724`. This is a local
geometric-mean estimate, not a Kaggle leaderboard score; the archive has not
yet been submitted because the daily submission quota was exhausted.
