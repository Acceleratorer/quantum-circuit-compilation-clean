---
id: exp-063
title: Rebuild Syed v25 paired-plain DQI from source
task: dqi
tests: Official DQI verifier, 102,400 shots
status: source_rebuilt_and_officially_verified
date: 2026-11-23
result: Q=890, cost=336,559,961,203.1761, verifier PASS with zero value and phase errors; candidate SHA-256 fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5.
---

# exp-063: source-built DQI

## Result

Private Kaggle kernel `accelra/exp-063-syed-v25-dqi-source-audit`, version 4,
rebuilt the `paired-plain` candidate and passed the unmodified official DQI
verifier on 102,400 shots. It measured 890 qubits, mean 356,677.4942 Toffoli
gates per shot, score `336,559,961,203.1761`, and zero value or phase errors.
Build time was 443.93 seconds; verification took 487.52 seconds.

The candidate SHA-256 is
`fc2564c61931a0b1c789d8857a78e54f88466b546870f0e99ad252b8c59183c5`.
The generated circuit is 828,831,824 bytes and remains in the private Kaggle
kernel output; it is not stored in Git.

## Source and rebuild

- Dataset: [`syed3000/vqcc-own-circuit-portfolio`, version 17](https://www.kaggle.com/datasets/syed3000/vqcc-own-circuit-portfolio/versions/17)
- License: Apache-2.0; the source `LICENSE` and `NOTICE` are retained in [`upstream/`](upstream/).
- The 630-file extracted source tree is 56,594,465 bytes, with tree SHA-256
  `8907c2df2cf821fb1e232148d6b93d8b49f4f2f44a88e53c15b62a43be364ec1`.
- The advertised ZIP was unavailable. The kernel built a temporary ZIP from
  the extracted tree after checking every path and file hash against the
  published manifest. The original build then checked every ZIP member again.
  The temporary ZIP hash and source tree receipt are in
  [`provenance.json`](receipts/provenance.json).
- No public `.kmb` or `.kmx` input was read. Internet access was disabled for
  the private kernel, and credential-like environment variables were removed
  before starting build and verifier subprocesses.
- The initial static scan and the reviewed runtime-wrapper hashes are in
  [`static_source_audit.json`](receipts/static_source_audit.json) and
  [`wrapper_source_audit.json`](receipts/wrapper_source_audit.json).
- Across the 630-file source tree, the scan found no credential identifiers or
  pickle loads. Its three network-keyword hits were references to an in-memory
  `requests` list; it also recorded subprocess and dynamic-execution sites in
  the broader research tree. The selected build ran offline with sanitized
  subprocess environments.

The kernel source is [`kernel/rebuild_verify.py`](kernel/rebuild_verify.py).
The exact build and verifier receipts are under [`receipts/`](receipts/), and
the raw Kaggle output is under [`kaggle_output/`](kaggle_output/).

## Submission status

This is a verified **DQI component**, not a competition submission or top-1
result. Together with the exp-062 invsqrt component, two of the three required
members now have source builds and official verifier passes. The dfthcsos
member and a complete archive are still outstanding. No partial archive was
submitted.
