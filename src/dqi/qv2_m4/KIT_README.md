# Generator kit for the three-task set with public leaderboard score 32.30740 (our package name: combo-m4)

Competition: Google Quantum AI "Verifiable Quantum Circuit Compilation". Package `submission.zip`, sha256
f62a9ffe48c4c6bb4aa0cdebb7012320baf63c6e2cf2d4b8be6d56c40966d69c. Score in our full local official evaluation:
**32.30740** (`stored_outputs/evaluation_combo-m4.json`). Licence of our files: Apache-2.0 (`LICENSE`); notices in
`NOTICE`; credits in `CREDITS.md`; sha256 of every kit file in `MANIFEST.sha256`; member hashes in
`EXPECTED_MEMBERS.sha256`; test record in `TESTED.md`.

## Members

| member | file(s) | sha256 | cost (official verifier) | made by | rebuild (recorded wall, one core) |
|---|---|---|---|---|---|
| invsqrt | invsqrt.kmb | 50f0140e0b6f37d4728047fc0791cc85958ee40977a54d84ad597f94ee5c0e19 | 63,035.5390 | team ThemBones' generator release (unchanged files) run with our recipe (`invsqrt/recipe/`) | `invsqrt/rebuild.sh`, about 7-13 min |
| DQI | dqi.kmb (495,618,056 B; not in the kit) | 3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3 | 313,736,314,690.17 | our compiler | `dqi/rebuild.py`, about 4-8 min, 1.1 GB disk |
| chemistry | dfthcsos/angle_k_0..14.kmb + submission.npz | EXPECTED_MEMBERS.sha256 | 255,384,620.97 | team ThemBones (loaders rebuilt from their release; table carried from their circuit release) | `chem/rebuild.sh`, seconds for the loaders, about 2-6 min for the gauge |

## Layout

| path | what | owner / licence |
|---|---|---|
| `thembones_generators/` | ThemBones generator release `vqcc-thembones-milestone-generators`, version 2 (2026-11-20 16:02 UTC), every file unchanged; checked against its `GENERATORS_MANIFEST.sha256` (1,675 files; the manifest also lists `dataset-metadata.json`, which the release does not distribute) | team ThemBones, Apache-2.0, their NOTICE and third_party__* files |
| `thembones_set/` | ThemBones circuit release `vqcc-thembones-milestone-set`: LICENSE, NOTICE, README.md, MANIFEST.sha256, the two costs__*.json, `set/invsqrt.kmb`, `set/dfthcsos/*` (17 of the 18 manifest files; `dqi_fileA.kmb`, 693 MB, is not carried and not used) | team ThemBones, Apache-2.0 |
| `invsqrt/rebuild.sh`, `invsqrt/build_driver.sh`, `invsqrt/recipe/`, `invsqrt/ours/` | our build command, the driver of their generator, our recipe (cfg patch, source patches, angles), our m9 spec script and program files | ours, Apache-2.0 |
| `chem/rebuild.sh`, `chem/ours/kmx2kmb.py`, `chem/regenerated_npz_arrays.json` | our chemistry driver, the kmb writer line, expected array hashes of the regenerated table | ours, Apache-2.0 |
| `chem/third_party_michaelrustad/` | Michael Rustad's `gauge.py` (unchanged) with its LICENSE | Michael Rustad, Apache-2.0 |
| `dqi/` | our DQI compiler and every file its build reads (`dqi/repo/`), the launcher `dqi/rebuild.py`, provenance code (`dqi/provenance/`) | ours, Apache-2.0; upstream files keep their LICENSE / NOTICE at their paths in `dqi/repo/` |
| `stored_outputs/` | our full local official evaluation of the package and the local reference run's costs | ours |

## Requirements
Linux x86-64, bash, bubblewrap (`bwrap`), `taskset`, `python3` (for small JSON steps of the drivers), and:
- `--official DIR`: the competition data folder with `kickmix/` and `verifiers/` (not in this kit; never copied into it).
- `--python-gen PY`: Python 3.13 with numpy, scipy and numba for the ThemBones code (recorded: Python 3.13.18,
  numpy 2.5.4, scipy 1.18.1, numba 0.68.1). Pass the venv's own `bin/python` (the drivers keep that path; resolving the
  symlink would lose the venv's packages).
- `--python PY`: Python 3.13 with numpy for our DQI build, the gauge and the verifier (recorded: numpy 2.5.4).

## Commands (one per member; each ends with a sha256 comparison)

```
bash invsqrt/rebuild.sh --official DIR --python-gen PY --out NEW_DIR [--cpu N] [--hide DIR]...
bash chem/rebuild.sh   --official DIR --python-gen PY --python PY2 --out NEW_DIR [--cpu LIST] [--verify] [--hide DIR]...
python3 dqi/rebuild.py --official DIR --python PY2 --out NEW_DIR [--cpu N] [--hide DIR]...
```
Outputs: `NEW_DIR/invsqrt.kmb` (last line `MATCH 50f0140e...`); `NEW_DIR/carried/dfthcsos/` (submitted member) and
`NEW_DIR/regenerated/dfthcsos/` (lines `loaders byte-equal: 15/15`, `carried submission.npz MATCH e05fb18f...`,
`regenerated submission.npz arrays MATCH`, `regenerated submission.npz file MATCH 9cd77fa4...`, `ALL CHECKS PASSED`, and with `--verify` the official verifier's status and cost of both);
`NEW_DIR/build/dqi.kmb` (`"match": true` in `NEW_DIR/rebuild.json`).

Sandbox: every ThemBones script, the gauge and our DQI build run only inside bubblewrap: no network, `/` read-only,
`/tmp`, `~/.kaggle` and `~/.ssh` replaced by empty tmpfs, `env -i`, HOME inside NEW_DIR, only NEW_DIR writable. The
upstream files are never edited: the drivers copy them into NEW_DIR and apply the ThemBones README's `<HOME>`
substitution to that working copy only. `--hide DIR` masks further directories (used for the hermetic tests).

## invsqrt: what the driver does beyond the ThemBones README
1. Their entry step 1 (`tools/invsqrt_fc_s19stage.py <PROG>`) is skipped: its input program is not in the release; its
   output `prog/dq18c.staged.json` is, and is used as given.
2. `~/qcc/ws/invsqrt_fc/s18/cub/m9dev.json` (read at emit; it sets row 24's m9 phase device and so changes gates) is not
   in the release. The driver makes it during the run: two emits with placeholder devices locate the m9 measurement and
   the 16 role wires (the generator's own `FC18_M9DBG` print); `ours/m9spec.py` simulates the emit with the release's
   `invsqrt_gen_circ.Sim` and writes the spec; the release's `tools/invsqrt_fc_s18m9q.py` makes the device (forms from
   the docstring of `tools/invsqrt_fc18_patch_m9.py`). Expected device content: sha256 bc1d5e08... of the JSON without
   its `spec` path key (6 CZ terms, 2 Z terms, sign 1). The device is not shipped; it is made by every run.
3. The two check-only comparison bases of `tools/f9_i1_stack.sh` (fc18_M's emit and the b196lend proof base) are not
   in the release; both are set to this run's own emit, so no file derived from the target is readable during the build.
   The verdict is the sha256 of the output.
4. The fourth argument of `f9_i1_stack.sh` is a taskset CPU list; the driver passes `--cpu`.

## invsqrt: our modifications (the recipe)
The member of this entry is NOT the file of team ThemBones' circuit release: it is what their generator emits when it
is run with the recipe in `invsqrt/recipe/`. Their files in `thembones_generators/` are unchanged; the recipe is applied
to the build's working copy. `invsqrt/build_driver.sh` is the driver described in the previous section with four more
options (`--patch`, `--sp`, `--angles`, `--env`); `invsqrt/rebuild.sh` calls it with the recipe and compares the result
with sha256 50f0140e0b6f37d4728047fc0791cc85958ee40977a54d84ad597f94ee5c0e19.
- driver environment (`recipe/DRIVER_ENV`): `POSTM9SP=1`; environment inside the sandboxed steps
  (`recipe/SANDBOX_ENV`): none
- cfg patch (`recipe/cfg_patch.json`): an empty patch: no key of their configuration is changed
- angles file (`recipe/angles.json`): none (the release's angles)
- program files (`ours/files/`): none
- source patches, applied in name order, each as `python3 PATCH.py SOURCE_DIR`:
- `recipe/sp/x0g8.py`: Almond-described change in ThemBones' h1c: the x0g guard-lend also on the x0 row WITHOUT an auxiliary carry wire (H1 row 8.2, carry-in T[8]); the lent guard wire R[0] is recorded as the chain's AUX wire so m3 keeps it out of its pool.
In the recipe's text files `<HOME>` stands for the build's sandbox home and `<RECIPE>` for the build's copy of
`invsqrt/ours/`; `rebuild.sh` replaces both in a temporary copy.

## Chemistry: what is rebuilt and what is carried
- Loaders: the 15 `chem/loaders_kmx/angle_k_*.kmx` of the release, written through the official kickmix kmb writer with
  the release's own writer line: 15/15 byte-equal to the submitted files.
- `submission.npz` of the submitted member (e05fb18f...) is **team ThemBones' carried file** from their circuit release
  (`thembones_set/set/dfthcsos/submission.npz`). Their assembly and gauge scripts (`tools/chem_c3_entry_raw.py`,
  `tools/lead_gauge.py`) are not in their generator release, so that exact file is not regenerated here. It equals the
  release's `table/asm_words.npz` except for a per-group orthogonal rotation of W and H2_I.
- Regenerated variant: `table/asm_words.npz` of the release turned by Michael Rustad's Apache-2.0 `gauge.py --sweeps 40`
  (the same kind of rotation). Reproducible byte for byte: file sha256 9cd77fa482efe1e673a89f64ac10cdc530651bc98ce85e7b3cd40eeb426329b7
  (same bytes in separate runs: TESTED.md), and every array's sha256 in `chem/regenerated_npz_arrays.json`. Official verifier: PASS at 255,384,530.95 (TESTED.md), against
  255,384,620.97 for the submitted file. Either can be the member; the submitted package uses the carried file.
- The `.kmx` loader programs and the tables are pinned results of ThemBones' randomized searches and GPU fits (their
  README); they are inputs, not rebuilt.

## DQI
`dqi/repo/` holds every file the build reads, at its repository path. Re-pin of 2026-11-20 (output
unchanged, dqi.kmb still 14ff3fcb...): two pinned modules imported from a hard-coded absolute path of the build
machine; they now find their sibling folders relative to their own file (one line each; `import os` added to
confluent_model.py):
| file | old sha256 | new sha256 |
|---|---|---|
| src/dqi_v8/v8_model.py (also inside source.zip) | a0c871561c60e35c1a04ff6bcdc47fd99734429b67a3ad98ac48d0e9c03dc8e7 | 4d11d90ffcd4bccbeaaae1ac12b716c747ae283ca377c8a4eba3b08e5f42de81 |
| src/dqi_end/confluent_model.py (also inside source.zip) | 81752ab8868a9525053b3ef43831fcd288f853e3aa9066468455832ff0f1a126 | 951b2ff2b5d559d3546c9762125432104ba14f9b1244ba453f76d2bc52c08d09 |
| runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit/source.zip (same entries, order and times) | 300c45e34d0e30566ad10610aa045f3e51fc7cc9a08983ff7502af8965ef2960 | 5aa1727788f0d7911bc1b7ff73095d009b11bd6381aa719bcfc73a87e13dfbc5 |
| .../jet_terminal17_kit/frozen_entry.py (pins source.zip) | 58625dd08b1f33ed6f1762eee45b4776739562a5f42525b827a90ccfd0fa4e84 | 87b301477e3f13ed849ac54d571ad2933622bf5814e597289a1cd641240243a4 |
`sources.json` carries the new hashes. Stored data the build consumes and their producers: CREDITS.md section C and
`dqi/provenance/` (provenance scripts as run on the build machine; its repository root is written `<REPO>`).

This entry's member (3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3) is built by the same frozen entry with these files of our
compiler changed against the kit of the 32.22304 entry (whose member was 14ff3fcb...): `dqi/repo/tools/dqi_pair_v12/SHA256SUMS`, `dqi/repo/tools/dqi_pair_v12/confluent_ext.py`.

In this dataset the pinned archive `.../jet_terminal17_kit/source.zip` is stored under the name `source_zip` (dataset hosts
unpack `*.zip` files); `dqi/rebuild.py` restores the name `source.zip` in its working copy before the build. Its sha256 is
unchanged (5aa1727788f0d7911bc1b7ff73095d009b11bd6381aa719bcfc73a87e13dfbc5).

## No-sandbox mode (e.g. a Kaggle session) and rebuild_all.sh
Every driver takes `--no-sandbox` (and `--work DIR`, a synonym of `--out`): the same steps without bubblewrap, with
`env -i` and HOME inside the work folder; the kit may be read-only (the drivers copy what they need and make the copy
writable). `taskset` is used when present.
```
bash rebuild_all.sh --official DIR --python-gen PY --python PY2 --work DIR [--no-sandbox] [--only invsqrt|chem|dqi] [--cpu N]
```
prints `MEMBER <name> sha256 <hash> EXPECTED <hash> MATCH|DIFFERENT wall <s>` per member file. Package versions and
whether outputs can depend on them: DEPENDENCIES.md.

## Not included
dqi.kmb (rebuild it), the competition data, ThemBones' `dqi_fileA.kmb` (their DQI line; not used by this package).
