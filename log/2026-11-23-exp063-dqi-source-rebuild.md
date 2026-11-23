# 2026-11-23 — exp-063 source-built DQI

## Execution

- Source: `syed3000/vqcc-own-circuit-portfolio`, dataset version 17, Apache-2.0.
- Private Kaggle kernel: `accelra/exp-063-syed-v25-dqi-source-audit`, version 4.
- The original source ZIP was unavailable. The kernel recreated a temporary
  ZIP from the published extracted tree after checking all 630 file hashes;
  the original builder rechecked the member list and hashes before building.
- Kernel internet was disabled. Credential-like environment variables were
  removed before launching the build and verifier subprocesses.

## Result

The `paired-plain` source build reproduced SHA-256
`fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5`.
The unmodified official verifier passed 102,400 shots with zero value and
phase errors at Q=890. DQI cost was `336,559,961,203.1761`; build time was
443.93 seconds and verification time was 487.52 seconds.

See the [evaluation receipt](../evals/2026-11-23-exp063-dqi.json),
[experiment record](../experiments/exp-063/README.md), and raw
[Kaggle kernel log](../experiments/exp-063/kaggle_output/rebuild_verify_v4.log).

## Debugging note

Kernel v2 did not package the helper module beside the configured script.
Kernel v3 then exposed that the Kaggle script upload includes only its
`code_file`; the required helper files were omitted. Version 4 pinned those
five Apache-2.0 helpers by SHA-256 and included them in the temporary build
package. The source build and verifier then passed.

## Decision

Keep this as the verified source-owned DQI member. Do not submit it alone:
invsqrt is also verified, but dfthcsos and the complete three-member archive
are still open.
