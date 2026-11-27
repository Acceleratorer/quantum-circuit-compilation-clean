---
id: exp-083
title: Source-owned exp-065 portfolio with V20 chemistry loaders
task: portfolio
status: cancelled
date: 2026-11-27
result: Kernel version 5 was cancelled before an integrated verifier result; no v5 output archive or Kaggle score exists. The local component-composed archive projects to 30.35107 and is not a measured score.
---

# exp-083 — exp-065 source portfolio with V20 chemistry

## Gate

The local component-composed archive retains exp-065's Invsqrt and DQI and
replaces only chemistry with exp-074's source-built V20 result. Its exact ZIP
hash and component scores are recorded in
receipts/source-assembled-v20-portfolio.json. It projects to `30.35107`, but
the combined archive did not run through the integrated Kaggle verifier and
was not submitted.

## Source build

The private Kaggle kernel rebuilds Invsqrt, DQI, and the base chemistry loaders
from the pinned Syed v17 source dataset, then applies the Apache-2.0 V20 loader
generator to the source-built chemistry inputs. It reads only Maoxin's pinned
raw parameter table (`submission.npz`) from that kernel output. It does not read
compiled circuits from public Kaggle inputs.

Kernel version 1 completed all three component rebuilds and official
verifications, then stopped at an aggregator check: the Invsqrt receipt nests
its verifier status under `official_verification.status`, unlike the DQI and
chemistry receipts. The check in `main.py` now validates each receipt using its
actual schema. Version 2 rebuilt and verified all three components, then
stopped because the V20 loader was passed the `dfthcsos` directory even though
it appends that directory itself. Version 3 fixed that path and reached V20,
where its parser exposed 40 qubits for five 8-qubit registers while the word
table contains 35 data bits. The adapted parser now selects seven data qubits
from each register and leaves each extra qubit untouched. Version 4 rebuilt
all three components, then its V20 loader simulator stopped on an `R q51`
reset operation it did not model. The failure is recorded in
`receipts/source-kernel-v4-summary.json`. Version 5 added reset handling, but
Kaggle now reports `CANCEL_ACKNOWLEDGED`. It produced no receipt or output
archive. Do not treat version 5 as a verifier pass. The exact cancellation
state is recorded in `receipts/source-kernel-v5-cancelled.json`.

The source wrappers are bundled from exp-062, exp-063, exp-064, and the V20
module adapted from exp-074. `package_kernel.py` records SHA-256 values for the
bundled files in the runtime receipt. The source builders must reproduce the
pinned Invsqrt and DQI hashes before the chemistry build can continue.

## Historical run (closed)

```powershell
python experiments/exp-083/package_kernel.py kaggle/staging/exp083-private-v5
kaggle kernels push -p kaggle/staging/exp083-private-v5
```

These commands describe how the experiment was staged. Kernel version 5 was
cancelled and produced no output archive. The component-composed local archive
is not a Kaggle measurement and was not submitted.

## Attribution

See [`NOTICE.md`](NOTICE.md) and [`source.json`](source.json). The DQI lineage
caveat remains the one recorded in [`src/dqi/NOTICE`](../../src/dqi/NOTICE).
