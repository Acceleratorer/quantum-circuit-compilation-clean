# Upstream and attribution

- **Source:** Kaggle dataset [`mliston/vqcc-milestone-generators-32-30740`](https://www.kaggle.com/datasets/mliston/vqcc-milestone-generators-32-30740), retrieved 2026-11-27.
- **Local dataset snapshot SHA-256:** `9fe082e0d22e3b95b802b0c0ba548c6798ebd869cff503446af2fb82ea11148e`. This identifies the locally retrieved snapshot used for the source audit; it is not a Kaggle dataset archive checksum.
- **Imported path:** `generators/dqi/` (92 files; checked against the upstream `generators/MANIFEST.sha256`).
- **Output reported by upstream:** `dqi.kmb`, SHA-256 `3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3`.
- **License:** Apache-2.0. The source kit's `LICENSE`, `NOTICE`, and `CREDITS.md` are retained here.

This is an attributed reproduction, not our original decoder design. The DQI
compiler is Matt Liston's work, built on Syed Asad Ali's Apache-2.0 v12
decoder source. The compiler also reads two multiplication tables (`J_A` and
`J_B`) extracted from Syed's compiled decoder. Team ThemBones' hoisted-prefix
mechanism and the additional contributors are credited in the retained
`CREDITS.md` and `NOTICE` files.

Only the 92 source files and five attribution files from the DQI subtree were
copied into this repository. Exp-089 attaches the public dataset as a Kaggle
kernel input, validates the pinned generator manifest and file hashes, then
copies only those files into a private temporary build directory. It does not
use the dataset's compiled artifacts as generator input. Nested source archives
were checked for unsafe paths and compiled circuit files before use.
