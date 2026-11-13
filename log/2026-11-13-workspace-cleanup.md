# 2026-11-13 — Workspace cleanup

Removed the disposable top-level scratch set after checking that the prepared
submission lives under `kaggle_scout/chem_refit_exp033/`.

- Removed `63` top-level files totaling `9,871,002,751` bytes (`9.193 GiB`).
- Removed old `tmp_*.kmb/kmx/npz` files, prior submission ZIPs, probe scripts,
  stale submission snapshots, and generated browser assets.
- Left the prepared archive untouched: `submission_exp033.zip`,
  `49,302,365` bytes, SHA-256
  `0f992a97d4411737cb1da2712b3617f0bdfd784ce3a5b3ebe8689fd85a2365cb`.
- Post-cleanup check: no top-level `tmp_*` files and no top-level
  `submission*.zip` files remain.
