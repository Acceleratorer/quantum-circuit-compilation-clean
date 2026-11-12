# Evidence

- `artifacts/submission_syed_own_v12.receipt.json` records archive/member hashes.
- `new_download/datasets_recent/syed_own/files/SHA256SUMS` is the public source manifest.
- `new_download/datasets_recent/syed_own/files/README.md` records the public verifier results and Apache-2.0 notice.
- Independent local verifier logs are written under `artifacts/` and copied here after completion.

## Local verifier runs

- `syed_chem_verify.log`: official chemistry verifier PASS.
- `syed_dqi_verify.log`: official DQI verifier PASS, 102,400 shots, zero value/phase errors.
- `syed_invsqrt_smoke.json`: invsqrt smoke PASS, 10,000 shots.
- `syed_invsqrt_verify_1shot.log`: exhaustive one-shot run is still in progress outside Git.
