# Run-time dependencies of the three rebuilds

Recorded environment (all three MATCH): Linux x86-64, bash, coreutils, `taskset` (optional), `bwrap` 0.9.0 (sandboxed
mode only), system `python3` 3.12 for small JSON steps of the drivers (standard library only), and:
- `--python-gen`: CPython 3.13.18 with numpy 2.5.4, scipy 1.18.1, numba 0.68.1 (llvmlite 0.50.0).
- `--python`: CPython 3.13.18 with numpy 2.5.4.
- the competition's `kickmix/kickmix.so` (ELF x86-64 extension, from the competition data) for every build.
Packages loaded: invsqrt and chemistry from file-open traces of complete runs (strace, openat); DQI from its import lines (grep of every .py in dqi/repo and both archives: numpy is the only third-party package imported; scipy appears only in one census report script that the build does not use).

| rebuild | packages loaded at run time | can the OUTPUT depend on the package version? |
|---|---|---|
| DQI (`dqi/rebuild.py`, our compiler) | numpy (+ standard library), by imports; kickmix | Low risk, not proven. The circuit is built by integer / GF(2^m) table logic (numpy integer arrays). `np.random.default_rng` appears in 59 places: in self-check scripts and some source modules of Syed Asad Ali's v12 archive and in two of our modules (emit_payload.py, axis_grade.py); whether any seeded draw shapes gates was not traced (numpy keeps PCG64 bit streams stable, but not every Generator method's output across versions). No scipy, no floating-point solve on the gate path was found by reading the imports. |
| invsqrt (`invsqrt/rebuild.sh`, ThemBones' generator) | numpy, scipy (constants, fft, linalg, optimize ...), numba + llvmlite (JIT), kickmix | Possible. scipy.optimize (`milp` with `time_limit=20` in `invsqrt_fk_rteval.py`, `linprog` in `invsqrt_sw_model.py`) is imported on the build path (`invsqrt_fk_epgen.py` imports `invsqrt_fk_rteval`); whether those solves are CALLED during this build was not traced. If they are, a different scipy / HiGHS version (or a time limit hit on a slower machine) could change the result. numba compiles integer simulators (numba version changes speed, not values, for integer code). The angles and the router are stored inputs (`data/r59b0/angles.json`, `router.json`), so no floating-point angle solve runs. |
| chemistry loaders (`chem/rebuild.sh`, kmb writer) | kickmix only (the writer process opens no site-packages) | No: text-to-binary conversion of the stored `.kmx` programs by the official writer. |
| chemistry carried `submission.npz` | none (file copy) | No. |
| chemistry regenerated `submission.npz` (Michael Rustad's `gauge.py`) | numpy | Yes, in the last bits: floating-point Givens rotations (`np.arctan2`, `np.cos`, `np.sin`, sums of absolute values, greedy accept test `< old - 1e-12`). Another numpy build or CPU (SIMD paths) can change array bits and so the file's sha256; the official verifier result would be expected to stay PASS at about the same cost, but that is untested on another image. Not the submitted file. |

Decisive check on any other image (e.g. Kaggle's): `bash rebuild_all.sh ... --no-sandbox` and the printed sha256 lines.
Resources measured on one core: peak resident memory 1.8 GB (invsqrt), 1.1 GB (DQI), 0.95 GB (chemistry); disk per
work folder 26 MB (invsqrt), 22 MB (chemistry), about 1 GB (DQI: the 499 MB dqi.kmb plus the 499 MB intermediate full.kmb).
