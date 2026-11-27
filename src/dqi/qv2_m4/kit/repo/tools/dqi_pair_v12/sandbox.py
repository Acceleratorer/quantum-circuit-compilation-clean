#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run tools/dqi_pair code (which imports Syed Asad Ali's public v12 DQI source, Apache-2.0) inside bubblewrap, exactly as
tools/dqi_public_cut18/rebuild.py does: no network, read-only root, tmpfs /tmp, ~/.kaggle and ~/.ssh masked, env -i,
one BLAS thread, taskset; only OUT is writable. The code files are copied fresh into OUT/code.
  .venv-quantum/bin/python -I -B tools/dqi_pair_v12/sandbox.py --out OUT [--cpus 22] SCRIPT [ARGS...]
SCRIPT is a file in tools/dqi_pair; it receives --src OUT/src --official OFFICIAL --out OUT before ARGS."""
import argparse, hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KIT = json.loads((ROOT / 'tools/dqi_public_cut18/kit.json').read_text())
sha = lambda p: hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--cpus', default='22')
ap.add_argument('--python', default=str(ROOT / '.venv-quantum/bin/python'))
ap.add_argument('script')
ap.add_argument('args', nargs=argparse.REMAINDER)
a = ap.parse_args()
src = ROOT / KIT['archive']['path']; off = ROOT / KIT['official_dir']
assert sha(src) == KIT['archive']['sha256']
for rel, h in KIT['host_inputs'].items():
    assert sha(off / rel) == h, rel
out = a.out.resolve(); out.mkdir(parents=True, exist_ok=False)
for d in ('home', 'code', 'src'):
    (out / d).mkdir()
for p in HERE.glob('*.py'):
    shutil.copy(p, out / 'code' / p.name)
# areebbb's retained-products pass (Apache-2.0, notebook qai-fewer-toffolis-same-qubits-lb-27-11042), verbatim
shutil.copy(ROOT / 'tools/dqi_public_cut18/notebook/retain.py', out / 'code' / 'retain.py')
for p in ('LICENSE', 'NOTICE'):
    shutil.copy(HERE / p, out / 'code' / p)
shutil.copy(src, out / 'src/dqi_source_zip')
home = Path.home()
argv = ['bwrap', '--unshare-net', '--die-with-parent', '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp',
        '--tmpfs', str(home / '.kaggle'), '--tmpfs', str(home / '.ssh'), '--bind', str(out), str(out), '--chdir', str(out),
        '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', f'HOME={out}/home', 'OPENBLAS_NUM_THREADS=1', 'OMP_NUM_THREADS=1', 'MKL_NUM_THREADS=1',
        '/usr/bin/taskset', '-c', a.cpus, a.python, '-I', '-B', str(out / 'code' / a.script),
        '--src', str(out / 'src'), '--official', str(off), '--out', str(out), *a.args]
t0 = time.time()
with open(out / 'run.stdout', 'x') as so, open(out / 'run.stderr', 'x') as se:
    rc = subprocess.run(argv, stdout=so, stderr=se, stdin=subprocess.DEVNULL).returncode
(out / 'sandbox.json').write_text(json.dumps(dict(exit_code=rc, seconds=round(time.time() - t0, 1), argv=argv), indent=1))
print(json.dumps(dict(exit_code=rc, seconds=round(time.time() - t0, 1))))
sys.exit(rc)
