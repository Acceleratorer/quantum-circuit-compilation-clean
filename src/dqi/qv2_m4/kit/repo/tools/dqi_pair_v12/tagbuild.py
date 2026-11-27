# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_rank (analysis only): build_np.py with stage INFO_TAG markers kept (component fullnptag), retain + andmerge
applied to the tagged text. Output OUT/tagged.kmx (gates identical to dqi.kmb plus INFO_TAG lines)."""
import argparse, os, subprocess, sys
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--src', type=Path); ap.add_argument('--official', type=Path); ap.add_argument('--out', type=Path)
a = ap.parse_args()
CODE = Path(__file__).resolve().parent
KM = a.official / 'kickmix'
sys.path[:0] = [str(KM), str(a.official / 'verifiers'), str(CODE)]
import retain, andmerge
env = dict(os.environ, PYTHONPATH=f'{KM}:{a.official / "verifiers"}')
r = subprocess.run([sys.executable, '-I', '-B', str(CODE / 'component.py'), '--src', str(a.src), '--official', str(a.official),
                    '--out', str(a.out), 'fullnptag'], capture_output=True, text=True, env=env)
print(r.stdout[-800:], r.stderr[-3000:], flush=True)
assert r.returncode == 0
kmx = a.out / 'fulltag.kmx'; ret = a.out / 'ret.kmx'
import kickmix as km
cd = km.Circuit.from_file(str(kmx), format='kmx'); NB = cd.num_bits; del cd
occ, idle, n = retain.scan(str(kmx), retain.read_registers(str(kmx)))
repl, post, st = retain.plan(occ, idle, first_new_bit=NB + 100008, n_lines=n, extra=[], max_hops=0)
del occ, idle
retain.rewrite(str(kmx), str(ret), repl, post); os.remove(kmx)
chosen, mcen = andmerge.plan(str(ret))
merged = andmerge.apply(str(ret), chosen, str(a.out / 'tagged.kmx')); os.remove(ret)
print('TAGGED', st, mcen, merged, flush=True)
