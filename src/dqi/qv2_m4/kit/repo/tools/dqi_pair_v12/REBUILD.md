# dqi_pair v12: kit v11 + shared-control merge pass (890 qubits), rebuild kit

Credit: original builder **Syed Asad Ali** (v12 DQI decoder, Apache-2.0; LICENSE and NOTICE here). Lineage starting from Syed Asad Ali.

Changes from v11 (tools/dqi_pair_v11; lane dqi_rank, 2026-11-16, run runs/20261116T173822Z-dqi-rank):
- rankmerge.py (own code): after retain and andmerge, groups of top-level unconditional CCX onto one target with no other
  use of the target between them, whose control wires all still hold their values at the group's last gate (linear GF(2)
  value fingerprints), are re-associated: gates sharing one control value y merge, a1.y + ... + ak.y = (a1+...+ak).y
  (CX-fold the other controls onto one, one CCX, unfold). Idea class first shown publicly for inverse-sqrt by Jeff
  Emerson (Apache-2.0; credit in NOTICE). On this build: 200 groups, 192 clusters of 3 (16 words x 12 bits in the
  conversion, 96 forward + 96 return: CCX q867/q874/q869 y t), -384 static Toffolis.
- build_np.py: calls rankmerge.plan / rankmerge.apply after andmerge; report key `rankmerge`.
- component.py: extra analysis mode fullnptag (nopark + stage INFO_TAG markers; not used by the build); tagbuild.py
  (analysis driver for that mode).
- Kill-test scanner (not part of the build): src/dqi_rank/rank_scan.py (GF(2) rank of every group's quadratic form):
  total rank deficiency of the v11 circuit = 384, all of it the class above; no other stage has any.

Rebuild (about 11 minutes on one core):

    .venv-quantum/bin/python -I -B tools/dqi_pair_v12/sandbox.py --out NEW_DIR --cpus 4 build_np.py

Result of the freeze: circuit dqi.kmb sha256 328e4e7bae16102c8406f48df8b316e4afb0c10479dfa31ca59ab6fd18c84012: 890 qubits,
static Toffoli-like 367,880 (v11 368,264). Three builds byte-identical (runs/20261116T173822Z-dqi-rank/build1..3).
Official verifier (2 workers): default PASS 0/0, 367,086.200 executed, score 346,381,588,906.6; salt 71 PASS 0/0,
367,086.231; salt 72 PASS 0/0, 367,086.404; salt 73 PASS 0/0, 367,086.218 (v11 default 367,470.45).

---- text of the v11 kit follows ----

# dqi_pair v11: kit v10 + norm-preserving tower closing (890 qubits), rebuild kit

Changes from v10 (tools/dqi_pair_v10; lane dqi_close, 2026-11-16):
- npclose.py (own code): every unguarded GF(2^24) closing (49 per shot: 33 in the synthesis return, 16 in the finish
  return) keeps the 12-bit norm N alive, multiplies by conj(N) (free in the tower basis), inverts only the 6-bit child
  norm and pays the phases with a 6-bit recompute: 340 Toffolis instead of 360. Idea and reference implementation:
  Balram Srinivasan's team, Kaggle dataset "VQCC 28.10 norm-preserving DQI closings" (Apache-2.0; credit in NOTICE);
  written against Syed Asad Ali's builder (original builder, Apache-2.0). Installed from component.py (--np 1, default).
- gadget.py: stand-alone test of the old and the new closing on random and special input classes (value, phase, ancilla;
  negative controls). Results of the freeze run: runs/20261116T165558Z-dqi-close/gadget1/gadget.json.

Rebuild (about 8 minutes on one core):

    .venv-quantum/bin/python -I -B tools/dqi_pair_v11/sandbox.py --out NEW_DIR --cpus 4 build_np.py

Result of the freeze: circuit dqi.kmb sha256 87ce9d72dd29b0540dc75aca0d6cc8494b727446cc2dd70a4b45fc535f81feba: 890 qubits,
static Toffoli-like 368,264 (v10 369,244), 367,470.45 executed per shot (v10 368,453.13). Three builds byte-identical
(runs/20261116T165558Z-dqi-close/build1..3). Official verifier: default salt and salt 73: 0 failed shots; salt 71: 1 value
error; salt 72: 1 phase error; both replayed on the v10 circuit by lane dqi_tower (same shots fail there, same kind: known
rare classes; runs/20261116T170955Z-dqi-tower/fail/). Kit files: SHA256SUMS.

---- text of the v10 kit follows (unchanged parts) ----

# dqi_pair v10: kit v9 + AND-merge post-pass (890 qubits), rebuild kit

Credit: original builder **Syed Asad Ali** (v12 DQI decoder, Apache-2.0; LICENSE and NOTICE here). Lineage starting from Syed Asad Ali.
The retained-products pass is areebbb's (retain.py, Apache-2.0). The joint kernels J_A / J_B and the v6/v7 node
changes are as in tools/dqi_pair_v7/REBUILD.md. The end node (slot 33 = modulus x^2 at the field point 0, slot 34 = the
point at infinity, 12-bit chains over the 33 stored heads) follows the layout of Syed Asad Ali's compiled 890-qubit
decoder (decoded by lanes dqi_fnode / dqi_v8).

Changes from v9 (tools/dqi_pair_v9, lane dqi_mf):
- andmerge.py (own code): after the retain pass, pairs of top-level unconditional CCX that add the same product
  (equal value fingerprints from retain.scan, consecutive occurrences) to targets t1 / t2 are merged when one target has
  no non-commuting use between them: one CCX becomes `CX t1 t2; CCX a b t1; CX t1 t2` and the other is dropped.
  On this build: 120 pairs (104 t2-free, 16 t1-free; 4,340 blocked, 662 same-target blocked), -120 static Toffolis.
- build_np.py: calls andmerge.plan / andmerge.apply on the retained text; report key `andmerge`.
- sandbox.py: usage path only.
- No measure-first sites exist in this circuit (lane dqi_mf scanner src/dqi_mf/scan.py: 0), so no such pass.

Changes from v7 (tools/dqi_pair_v7):
- confluent_ext.py: 33 extractor slots (single node 0 + doubles 1..16), new geometry words S66..S69 (lane dqi_v8b);
  emit_key_prefix / emit_key_closing rewritten for the end node (lane dqi_v9b): f31 X-measured after the extractor,
  v7 gauge, endnode.SeqEnd forward, synthesis from i = 32; return = native closings (RIPPLE_SLOTS masks deferred),
  SeqEnd.reverse with the head ripple run on the reconstructed P33 words (C class carrier), gauge return, extractor
  closing with f31 = [nA = 0 and eA = 0] and [head 32 = 0].
- endnode.py: Pass (12-bit chains) + SeqEnd (sequential end node: chain A scaled by lambda, kernel A with the
  B-input scale by 1/U, chain B, query, kernel B, class fixups, r = 1 step; exact return). Word model
  src/dqi_v8b/seq_model.py; class checks src/dqi_v9b/check_fwd.py, check_errs.py.
- nopark.py (lane dqi_v9): the conversion's gauge flag is never lent (890 qubits; parks are bookkeeping only).
- build_np.py: component.py fullnp (nopark + full at max 890 qubits) + retain pass.

## Command (from the repository root)

    .venv-quantum/bin/python -I -B tools/dqi_pair_v10/sandbox.py --out NEW_DIR --cpus 4 build_np.py

## Inputs (sha256)

| file | sha256 |
|---|---|
| tools/dqi_public_syed_v12/dqi_source_zip | 49e2b331d4008afb724985caf1038765b7a910f08838b590bf6e8fb692772763 |
| official/2026-10-27/kickmix/kickmix.so | c66b3216c4029e0cdfd09054306aa0feadf53ab2f50c1164e37f752874e5005e |
| official/2026-10-27/verifiers/dqi/verify_submission_dqi.py | f14274bc0943fb9769ddb01131be6063191a15009fe1caf1d4bdd9fd25194e65 |
| tools/dqi_public_cut18/notebook/retain.py | f9a477f5148bf6cb454917e5f3f10e7a042fce0c14d20ea21e32fe3a36240bfc |
| kit files | SHA256SUMS |

## Outputs

- circuit dqi.kmb sha256 455c0617e1dbe77778b27736afb12472b2644f8474ff3ba56bcc935ffe565437: 890 qubits, static
  Toffoli-like 369,244 (v9 369,364). Three builds byte-identical (runs/20261116T061823Z-dqi-mf/kitbuild1..3).
- Official verifier (dqi, 4 workers): default PASS 0/0, 368,453.133 executed Toffolis, score 347,671,423,431.9;
  salt 71 PASS 0/0, 368,452.725, 347,671,038,538.1; salt 72 PASS 0/0, 368,452.669, 347,670,986,069.0.
- Negative control (one merged site without its second CX, runs/20261116T061823Z-dqi-mf/v10neg): FAIL, 51,306/102,400
  value errors.
