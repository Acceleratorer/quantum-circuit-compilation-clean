#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the DQI member dqi.kmb (sha256 3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3) from this kit.

  python3 rebuild.py --official /path/to/competition/official_dir --python /path/to/python3.13 --out NEW_DIR [--cpu 0] [--no-sandbox]

--official is the folder that holds the competition's kickmix/kickmix.so and verifiers/dqi/verify_submission_dqi.py
(competition data, not part of this kit). The script copies repo/ to NEW_DIR/repo, links the competition data into
it, provisions NEW_DIR/build exactly as tools/dqi_pair_v12/sandbox.py does, and runs the frozen entry inside
bubblewrap (no network, read-only root, private /tmp, env -i, one BLAS thread). Needs Linux, bwrap, taskset,
Python 3.13 with numpy (recorded: 3.13.18, numpy 2.5.4). About 4-6 minutes on one core; ~1.1 GB disk."""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
KIT = Path(__file__).resolve().parent
WANT = '3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3'
sha = lambda p: hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()
ap = argparse.ArgumentParser()
ap.add_argument('--official', type=Path, required=True)
ap.add_argument('--python', required=True)
ap.add_argument('--out', '--work', dest='out', type=Path, required=True)
ap.add_argument('--cpu', default='0')
ap.add_argument('--hide', action='append', default=[], help='directory to mask with an empty tmpfs inside the sandbox (repeatable)')
ap.add_argument('--src-at', default=None, help='optional: also mount the kit copy\'s repo/src read-only at this absolute path inside the sandbox (no longer needed: the two modules that hard-coded a path find src relative to their own file since the 2026-11-20 re-pin)')
ap.add_argument('--no-sandbox', action='store_true', help='run the build directly (no bubblewrap), e.g. in a Kaggle session; env -i and HOME inside --out are kept')
ap.add_argument('--trace', action='store_true', help='run under strace; log in OUT/build/strace.log')
a = ap.parse_args()
top = a.out.resolve(); top.mkdir(parents=True, exist_ok=False)
root = top / 'repo'; shutil.copytree(KIT / 'repo', root, symlinks=True)
for d, _, fs in os.walk(root):   # the kit may be read-only (e.g. /kaggle/input): make the working copy writable
    for x in [d] + [os.path.join(d, f) for f in fs]:
        if not os.path.islink(x): os.chmod(x, os.stat(x).st_mode | 0o200)
# The pinned source archive is stored in the kit as "source_zip" (dataset hosts unpack *.zip files); the build reads it
# under its pinned name source.zip, restored here in the working copy.
_kit = root / 'runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit'
if (_kit / 'source_zip').is_file() and not (_kit / 'source.zip').exists():
    (_kit / 'source_zip').rename(_kit / 'source.zip')
off = a.official.resolve()
(root / 'official').mkdir(); (root / 'official/2026-10-27').symlink_to(off, target_is_directory=True)
cfg = json.loads((root / 'tools/dqi_public_cut18/kit.json').read_text())
src = root / cfg['archive']['path']; assert sha(src) == cfg['archive']['sha256']
for rel, h in cfg['host_inputs'].items():
    assert sha(off / rel) == h, rel
out = top / 'build'; out.mkdir()
for d in ('home', 'code', 'src'):
    (out / d).mkdir()
pair = root / 'tools/dqi_pair_v12'
for p in pair.glob('*.py'):
    shutil.copy(p, out / 'code' / p.name)
shutil.copy(root / 'tools/dqi_public_cut18/notebook/retain.py', out / 'code' / 'retain.py')
for p in ('LICENSE', 'NOTICE'):
    shutil.copy(pair / p, out / 'code' / p)
shutil.copy(src, out / 'src/dqi_source_zip')
entry = root / 'runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit/frozen_entry.py'
home = Path.home()
inner = ['/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', f'HOME={out}/home', 'OPENBLAS_NUM_THREADS=1', 'OMP_NUM_THREADS=1', 'MKL_NUM_THREADS=1',
         *(['taskset', '-c', a.cpu] if shutil.which('taskset') else []),
         *(['/usr/bin/strace', '-f', '-qq', '-e', 'trace=open,openat,execve', '-o', str(out / 'strace.log')] if a.trace else []), a.python, '-I', '-B', str(entry), '--src', str(out / 'src'),
         '--official', str(root / 'official/2026-10-27'), '--out', str(out)]
sandbox = ['bwrap', '--unshare-net', '--die-with-parent', '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp',
           '--tmpfs', str(home / '.kaggle'), '--tmpfs', str(home / '.ssh'), *[x for h in a.hide for x in ('--tmpfs', str(Path(h).resolve()))],
           *(['--ro-bind', str(root / 'src'), a.src_at] if a.src_at else []), '--bind', str(top), str(top), '--chdir', str(out)]
argv = inner if a.no_sandbox else sandbox + inner
t0 = time.time()
with open(out / 'run.stdout', 'x') as so, open(out / 'run.stderr', 'x') as se:
    rc = subprocess.run(argv, stdout=so, stderr=se, stdin=subprocess.DEVNULL, cwd=out).returncode
res = dict(exit_code=rc, seconds=round(time.time() - t0, 1), argv=argv)
if (out / 'dqi.kmb').exists():
    res['dqi_sha256'] = sha(out / 'dqi.kmb'); res['match'] = res['dqi_sha256'] == WANT
(top / 'rebuild.json').write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'argv'}))
sys.exit(0 if rc == 0 and res.get('match') else 1)
