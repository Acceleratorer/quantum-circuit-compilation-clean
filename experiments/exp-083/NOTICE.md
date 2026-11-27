# Source and data notice

- Invsqrt, DQI, and the base chemistry loaders are rebuilt from
  `syed3000/vqcc-own-circuit-portfolio`, version 17, under Apache-2.0. The
  original package `LICENSE` and `NOTICE` are preserved in the attached dataset.
  The DQI design lineage caveat in `src/dqi/NOTICE` is retained.
- The V20 chemistry loader generator and its packed source descriptions come
  from Goodpjw2008's `qcc-shorter-chemistry-loaders-lb-33-25564` Kaggle
  notebook, which states Apache-2.0. Its notebook hash is
  `ea7323f8536747c7775397e718f42745db802dacf4dcd24a5ead07baa9ed3420`.
- The raw chemistry parameter table comes from Maoxin123's public kernel output
  `qcc-33-17-3-357-toffoli-chemistry-loaders`; only the pinned `submission.npz`
  with SHA-256 `ec85d969811623b5b4c7e3fff26fef2151bafedaa9a4741cb978e56ff34fbba1`
  is read. No compiled circuit is read or copied from this input.
- The V20 module is adapted under Apache-2.0: its loader parser selects the
  seven data qubits in each 8-qubit word register and leaves the extra qubit
  untouched. The five registers provide the 35 bits represented by the
  chemistry word table.
- Private kernel versions 1–3 generated and officially verified the Invsqrt,
  DQI, and base chemistry circuits from source. Version 4 rebuilds them from
  source, checks their pinned hashes, then generates and verifies the V20
  chemistry circuits.
- The source bundle, orchestration, archive builder, and exact-output checks in
  this experiment are our integration work. No public compiled circuit is used.
