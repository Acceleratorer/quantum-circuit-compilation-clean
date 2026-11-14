# Areeb retained-product DQI

The artifact is an 889-qubit, same-qubit product-retention rewrite. It removes
241 static Toffoli-like gates while keeping the Syed v12 register width. The
source notebook includes a paired replay against the original circuit and a
full official verifier receipt; the local workspace keeps the extracted KMB
and smoke log outside Git.

## Current source and correctness gate

This is the DQI member used in the current `exp-033` public-best portfolio
(`821bf8d157c0...`). The cited notebook reports a 102,400-shot PASS with zero
observed value and phase errors. A later targeted audit records rare value
counterexamples at error weights 16/17, so the sampled PASS is not an exhaustive
correctness proof.

The repository's `src/dqi/generate.py` builds a different, 897-qubit Apache-2.0
port; it does not reproduce this 889-qubit member. The standing user decision
in `knowledge/user-decisions.md` says submitted circuits must come from our own
generator. Treat this artifact as a measurement reference until an owned,
reproducible generator replaces it and passes the targeted cases.
