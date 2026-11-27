# QV2 m4 DQI generator

This directory keeps the 92 source files and five attribution files used to
reproduce the DQI generator in Matt Liston's Apache-2.0
`vqcc-milestone-generators-32-30740` kit. The files under `kit/` are unchanged.
See [UPSTREAM.md](UPSTREAM.md) for provenance and design lineage.

`MANIFEST.json` pins every file here except itself. Exp-089 attaches the public
Kaggle dataset at runtime, checks the pinned file hashes, and copies only those
files into its private build directory. The upstream kit reports that this
generator emits DQI circuit SHA-256
`3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3` at a
mean verifier cost of `313736314690.17`. Those are upstream figures; the
reproducible private-kernel measurement is recorded under
[`experiments/exp-089`](../../../experiments/exp-089/README.md).

No compiled circuit (`.kmb`, `.kmx`, or `.npz`) is included. Build and run the
official verifier only through the private Kaggle kernel described in exp-089.
