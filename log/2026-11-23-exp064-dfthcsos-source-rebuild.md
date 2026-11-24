# 2026-11-23 — exp-064 dfthcsos source rebuild

- Kernel: `accelra/exp-064-dfthcsos-source-audit`, version 1; internet disabled.
- Source: `syed3000/vqcc-own-circuit-portfolio`, version 17; selected source tree SHA-256 `61c2b9db025e13dac7192e436d6354a9892ffde0a719e1fb3a81734cfad9da83`.
- Build: 15 circuits; every output hash matched the source manifest. Build time 10.60 seconds.
- Official verifier: PASS, 78,080 shots; score `295006518.96994764`; 427 qubits; 14,718 Toffoli. Verification took 27.69 seconds.
- Audit: zero reads from public `.kmb`/`.kmx` inputs and zero blocked-read attempts.
- Margin: both residual errors and the SOS gap sit very close to their strict acceptance bounds; see [`exp-064`](../experiments/exp-064/README.md).
- Decision: mark the dfthcsos component gate complete, then assemble and verify the three-member archive before submission.
