# dqi_public_cut18: rebuild of the public DQI circuit 821bf8d1 from source

Credit: **Syed Asad Ali (v12 decoder, Apache-2.0), Ertugrul Ozer (extractor cutoff), areebbb (retained products)**.
Lineage starting from Syed Asad Ali.

- Decoder generator: Syed Asad Ali's archive `dqi_source_zip` (Kaggle dataset syed3000/vqcc-own-circuit-portfolio v12,
  Copyright 2026 Syed Asad Ali, Apache-2.0), used from `tools/dqi_public_syed_v12/dqi_source_zip` (LICENSE and NOTICE in
  `tools/dqi_public_syed_v12/upstream/`); pinned by sha256 in `kit.json`.
- Extractor cutoff: Ertugrul Ozer's (ozertuu) runtime wrapper on `P.First3.emit_prefix` (notebook "Quantum AI 27.083+ VQCC:
  DQI cutoff 17"), applied with cutoff 18 by areebbb.
- `notebook/build_cut.py`, `retain.py`, `peep.py`, `alloc.py`: the %%writefile cells 9, 4, 5, 6 of the public Kaggle notebook
  areebbb/qai-fewer-toffolis-same-qubits-lb-27-11042 (Apache-2.0 by the notebook's credits section: "Ours: the
  value-fingerprint scanner, idle-window analysis, retention planner and rewrite, ... (Apache-2.0)"), extracted verbatim
  (first line `%%writefile /tmp/NAME` removed) from the .ipynb JSON, sha256 a03370c7...; `notebook/kernel-metadata.json` as pulled.
- `driver.py`, `rebuild.py`: ours. `driver.py` performs the notebook's cells 10 and 12 in order: build_cut.py with CUT,
  kmb -> kmx, `retain.scan` (seed 20261112), `retain.plan(first_new_bit=num_bits+100008, extra=[], max_hops=0)`,
  `retain.rewrite`, kmx -> kmb. peep.py and alloc.py are an audit in the notebook and do not change its dqi.kmb.

Rebuild (bubblewrap sandbox: no network, read-only root, tmpfs /tmp, ~/.kaggle and ~/.ssh masked, env -i, one BLAS thread):

    .venv-quantum/bin/python -I -B tools/dqi_public_cut18/rebuild.py --out NEW_DIR [--cut 18] [--cpus 2]

asserts output sha256 821bf8d157c03c3e868a0099b0ab1438cfba664ab1bc6fec3210654099b672a3 (455,584,321 bytes) and the
unretained intermediate prefix 32b0a8b44476. Measured 2026-11-13: 390 s, peak RSS 1.0 GB, about 2 GB temporary disk.
Receipt: runs/20261113T164312Z-dqi-pub2/build_cut18/report.json. Other cutoffs (`--cut 19`, `--cut 20`) build without a pin.
