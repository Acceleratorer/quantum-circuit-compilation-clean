# Upstream attribution — exp-066

## Generator source

- Tony Li, [Quantum AI 32.85306 Task Generators](https://www.kaggle.com/datasets/tonylica/quantum-ai-32-85306-task-generators), version 2, Apache-2.0.
- The dataset's `notices/RELEASE_NOTICES.txt` credits Team ThemBones and the inherited Syed Asad Ali, Atakan Aldemir, and James Day circuit sources. Its `dqi/README.md` describes which decoder stages are recovered native KMX assembly and which D16 arithmetic stages are generated from editable tables.
- The public package reports base DQI SHA-256 `4b5721411adc239f61fc11c773a2358b75dfe7cb15586efae4f0459c77d77e52`.

## DQI gate rewrites

- Areeb Ali, [QAI | The 26-Toffoli Cut](https://www.kaggle.com/code/areebbb/qai-the-26-toffoli-cut-lb-33-21010), Apache-2.0 as stated in the notebook's Credits section.
- The rewrite set includes Evgeniy Dvorkin's `CCZ` to `CZ` simplification, Ertuğrul Özer's redundant conditional `CCZ` deletion, and Areeb's eight `CCX` to `CX` edits in the 24-bit zero-test chain.
- The edit patterns are applied only after rebuilding the DQI from the licensed source dataset. The final circuit is recompiled and checked against the public rewritten hash before official verification.

This is an attributed source adaptation, not an independent rediscovery of the upstream decoder or gate identities.
