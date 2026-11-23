# 2026-11-23 — one invsqrt source lead

## Decision

Keep inverse square root as the single active optimization direction. Do not
reuse the 37-qubit `bb676b95…` circuit: its notebook applies a phase edit to
the pinned public `d2148a7c…` parent, and the public-circuit manifest has no
generator or rebuild record for the result.

The higher-confidence next candidate is Syed Asad Ali’s Apache-2.0 v17
from-source generator, which reports a 43-qubit circuit at cost `72,440.35`
and a full official-verifier PASS. The repository’s current generator
(`src/invsqrt`) has a full PASS at 92 qubits and cost `148,977.90`.

## Evidence and gate

The full measurements, hashes, provenance, and source-access limitation are
in [`evals/2026-11-23-invsqrt-source-lead.json`](../evals/2026-11-23-invsqrt-source-lead.json).
The 43-qubit result is a published source claim, not a result reproduced
here. The advertised archive path returned 404 through Kaggle; only selected
source files and the Apache notice have been read so far.

Next: resolve the complete source bundle, port it with Syed’s LICENSE/NOTICE,
then generate and run the official verifier in a private Kaggle kernel. Do
not copy any public circuit binary into the candidate.
