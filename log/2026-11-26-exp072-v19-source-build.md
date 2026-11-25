# 2026-11-26 — exp-072 V19 source build

## Run

- Private Kaggle kernel: `accelra/exp-072-source-built-v19-chemistry`, version 4.
- Command: `kaggle kernels push -p %TEMP%\qcc-exp072-source-build-kernel-v4`.
- Sources: Goodpjw2008 V19 notebook; Maoxin raw table `ec85d969…`; pinned
  Tony Li generator dataset fingerprint `50be321a…`; Kickmix SHA-256
  `c66b3216…`.
- The Maoxin archive scan read only `submission.npz`. All 15 baseline loaders
  were compiled from editable KMX source; DQI and Invsqrt were source-built.
  Receipt records `compiled_input_circuits_read: 0`.
- Kernel versions 1–3 stopped on script packaging/scope errors before the
  verifier stage. Version 4 completed all builds and checks.

## Results

- Chemistry: PASS at default and salt 42; 78,016 shots; score
  `249,967,854.71943197`; 3,328 Toffolis/pass; 128-qubit angle cap met.
- Invsqrt: PASS; 200,540,928 shots; score `61,696.23146663024`.
- DQI: PASS; 102,400 shots; score `309,694,874,626.0435`; four value errors,
  zero phase errors.
- 18-member archive: CRC PASS; SHA-256
  `6fb21b160f87ebeff80a9b506e7335e5a4d0803db5ca6e2ba61257010e084a5e`.
- Local verifier GM: `32.9148153851` for this DQI draw. The exact DQI hash had
  zero value errors in exp-071; substituting that score gives diagnostic GM
  `33.0813367703`, still below the `33.17067` account best. This is not a
  public-score projection.

## Decision

Do not submit. Chemistry improved over exp-071 by `608,050.4202`, but the
source build missed the notebook's 3,310-Toffoli claim by 18 Toffolis/pass and
the measured portfolio did not establish an account-best improvement. The
notebook's `33.25057` title score remains unverified. Full verifier and
leaderboard evidence is in
[`evals/2026-11-26-exp072-source-built-v19-chemistry.json`](../evals/2026-11-26-exp072-source-built-v19-chemistry.json).

Next gate: V19's 37-qubit Invsqrt notebook starts from the published compiled
`d2148a7c` circuit and edits its phases; it does not rebuild that circuit from
editable source. Keep this lead parked unless a separate source generator is
found. The source-built Invsqrt remains the 39-qubit exp-071 circuit.
