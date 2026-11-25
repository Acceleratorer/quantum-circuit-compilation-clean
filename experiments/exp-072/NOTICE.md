# Third-party notices

- The chemistry weight payload, packed loader programs and rebuild algorithm
  are derived from Goodpjw2008's V19 Kaggle notebook. That notebook states
  Apache-2.0 for its code and loader work, and preserves each upstream file's
  license. Source notebook SHA-256:
  `c4c9f473d26f10cdb5351be8885bb1e26636269c5b39488ea3eba47ed7661121`.
- The raw `submission.npz` parameter table is read from Maoxin123's published
  kernel output and pinned by SHA-256
  `ec85d969811623b5b4c7e3fff26fef2151bafedaa9a4741cb978e56ff34fbba1`.
  The kernel reads no compiled circuit from that archive.
- Source KMX circuits, the DQI base, the Invsqrt base, and Kickmix come from
  Tony Li's Apache-2.0 task-generator dataset. The build checks its complete
  dataset fingerprint, release manifest and SDK hash before compiling.
- DQI gate edits retain the upstream credits recorded in
  `../exp-066/UPSTREAM.md`, including Tony Li, Evgeniy Dvorkin, Ertuğrul Özer,
  Syed Asad Ali and the circuit contributors named there.

`LICENSE` contains the Apache License 2.0 terms used by the source package.
Each upstream source retains its own attribution and terms.
