# Source and data notice

## Goodpjw2008 V22 loaders

The loader construction and packed V22 descriptions are adapted from
Goodpjw2008, [QCC | Shorter Chemistry Loaders | LB 33.25737](https://www.kaggle.com/code/goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25737),
version 26, notebook SHA-256
`ee75f7d419f3f687edf2fc1f1e6899e8a1eca94694b695c8c122e85aec29da7a`.
The notebook states that its code, loaders, `dqiscan`, and rewrites are under
Apache-2.0; its upstream files retain their own terms. The original author and
source remain credited. The V22 packed loader payload SHA-256 is
`5076df379225232c722bc9f0c27f6b7f796a871b17c5501d5fd21fab19dac4ff`.

Our changes are limited to taking the V22 packed descriptions and their
batch metadata, using the exp-074 builder's isolated source-build interface,
keeping exp-074's refitted weights, and requiring the source-built 3,324-Toffoli
loader count before full verification. No compiled candidate circuit from the
notebook is read or copied.

## Base source and raw data

The DQI, Invsqrt, and base chemistry inputs are generated from Tony Li's
Apache-2.0 `quantum-ai-32-85306-task-generators` source dataset, pinned by its
manifest and full dataset fingerprint in `main.py`. The raw chemistry table is
Maoxin123's v4 `submission.npz`, pinned by SHA-256
`ec85d969811623b5b4c7e3fff26fef2151bafedaa9a4741cb978e56ff34fbba1` and used
only as source data. No compiled candidate circuits are used as inputs.

The Apache-2.0 license text is in [LICENSE](LICENSE). Copyright and attribution
remain with the upstream authors.
