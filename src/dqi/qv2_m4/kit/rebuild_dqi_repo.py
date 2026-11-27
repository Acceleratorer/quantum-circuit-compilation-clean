#!/usr/bin/env python3
"""Fresh isolated rebuild of the submitted DQI member (sha256 3c03fa53...) with the frozen kit
runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit/frozen_entry.py, provisioned exactly as
tools/dqi_pair_v12/sandbox.py provisions OUT (code/ = tools/dqi_pair_v12/*.py + retain.py + LICENSE/NOTICE,
src/dqi_source_zip = Syed Asad Ali v12 archive), and launched with the argv of
runs/20261119T035100Z-coordinator-resume/jet_terminal17_independent/sandbox.json.
  python3 rebuild_dqi.py OUT CPU [--strace]"""
import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path
ROOT = Path('<REPO>')
KIT = json.loads((ROOT / 'tools/dqi_public_cut18/kit.json').read_text())
ENTRY = ROOT / 'runs/20261119T035200Z-dqi-split-finish/jet_terminal17_kit/frozen_entry.py'
sha = lambda p: hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()
out = Path(sys.argv[1]).resolve(); cpu = sys.argv[2]; trace = '--strace' in sys.argv
src = ROOT / KIT['archive']['path']; off = ROOT / KIT['official_dir']
assert sha(src) == KIT['archive']['sha256']
for rel, h in KIT['host_inputs'].items():
    assert sha(off / rel) == h, rel
out.mkdir(parents=True, exist_ok=False)
for d in ('home', 'code', 'src'):
    (out / d).mkdir()
pair = ROOT / 'tools/dqi_pair_v12'
for p in pair.glob('*.py'):
    shutil.copy(p, out / 'code' / p.name)
shutil.copy(ROOT / 'tools/dqi_public_cut18/notebook/retain.py', out / 'code' / 'retain.py')
for p in ('LICENSE', 'NOTICE'):
    shutil.copy(pair / p, out / 'code' / p)
shutil.copy(src, out / 'src/dqi_source_zip')
prov = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob('*')) if p.is_file()}
prov['ENTRY ' + str(ENTRY.relative_to(ROOT))] = sha(ENTRY)
(out / 'provisioned_inputs.json').write_text(json.dumps(prov, indent=1))
home = Path.home()
py = [str(ROOT / '.venv-quantum/bin/python'), '-I', '-B', str(ENTRY), '--src', str(out / 'src'), '--official', str(off), '--out', str(out)]
if trace:
    py = ['/usr/bin/strace', '-f', '-qq', '-e', 'trace=open,openat,execve,stat,newfstatat,readlink', '-o', str(out / 'strace.log')] + py
argv = ['bwrap', '--unshare-net', '--die-with-parent', '--ro-bind', '/', '/', '--dev', '/dev', '--proc', '/proc', '--tmpfs', '/tmp',
        '--tmpfs', str(home / '.kaggle'), '--tmpfs', str(home / '.ssh'), '--bind', str(out), str(out), '--chdir', str(out),
        '/usr/bin/env', '-i', 'PATH=/usr/bin:/bin', f'HOME={out}/home', 'OPENBLAS_NUM_THREADS=1', 'OMP_NUM_THREADS=1', 'MKL_NUM_THREADS=1',
        '/usr/bin/taskset', '-c', cpu, *py]
t0 = time.time()
with open(out / 'run.stdout', 'x') as so, open(out / 'run.stderr', 'x') as se:
    rc = subprocess.run(argv, stdout=so, stderr=se, stdin=subprocess.DEVNULL).returncode
res = dict(exit_code=rc, seconds=round(time.time() - t0, 1), argv=argv)
if (out / 'dqi.kmb').exists():
    res['dqi_sha256'] = sha(out / 'dqi.kmb'); res['match'] = res['dqi_sha256'] == '3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3'
(out / 'sandbox.json').write_text(json.dumps(res, indent=1))
print(json.dumps({k: v for k, v in res.items() if k != 'argv'}))
sys.exit(rc)
