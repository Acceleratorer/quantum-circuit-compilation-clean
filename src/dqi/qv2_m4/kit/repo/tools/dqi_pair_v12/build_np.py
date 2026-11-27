# SPDX-License-Identifier: Apache-2.0
"""Runs INSIDE tools/dqi_pair_v12/sandbox.py: full confluent decoder (component.py full: Syed Asad Ali's v12 DQI decoder,
Apache-2.0, with confluent_ext installed), then areebbb's retained-products pass exactly as tools/dqi_public_cut18/driver.py
(retain.scan, retain.plan(extra=[], max_hops=0), retain.rewrite), then lane dqi_mf's AND-merge pass (andmerge.py), then lane
dqi_rank's shared-control merge pass (rankmerge.py).
Output OUT/dqi.kmb, OUT/driver_report.json."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--src', type=Path); ap.add_argument('--official', type=Path); ap.add_argument('--out', type=Path)
a = ap.parse_args()
CODE = Path(__file__).resolve().parent
KM = a.official / 'kickmix'
sys.path[:0] = [str(KM), str(a.official / 'verifiers'), str(CODE)]
import kickmix as km
import retain
import andmerge
import rankmerge
sha = lambda p: hashlib.file_digest(open(p, 'rb'), 'sha256').hexdigest()
T0 = time.time(); rep = {}
env = dict(os.environ, PYTHONPATH=f'{KM}:{a.official / "verifiers"}')
r = subprocess.run([sys.executable, '-I', '-B', str(CODE / 'component.py'), '--src', str(a.src), '--official', str(a.official),
                    '--out', str(a.out), 'fullnp'], capture_output=True, text=True, env=env)
print(r.stdout[-800:], r.stderr[-3000:], flush=True)
assert r.returncode == 0, 'component full failed'
raw = a.out / 'full.kmb'
rep.update(build_stdout=r.stdout.strip()[-400:], unretained_sha256=sha(raw), build_seconds=round(time.time() - T0, 1))
kmx, kmx_ret, out = a.out / 'dqi.kmx', a.out / 'dqi_ret.kmx', a.out / 'dqi.kmb'
cd = km.Circuit.from_file(str(raw), format='kmb'); cd.to_file(str(kmx), format='kmx')
NQ, NB, T_STATIC = cd.num_qubits, cd.num_bits, cd.operation_statistics().num_toffoli_like; del cd
occ, idle, n = retain.scan(str(kmx), retain.read_registers(str(kmx)))
repl, post, st = retain.plan(occ, idle, first_new_bit=NB + 100008, n_lines=n, extra=[], max_hops=0)
del occ, idle
retain.rewrite(str(kmx), str(kmx_ret), repl, post)
os.remove(kmx)
chosen, mcen = andmerge.plan(str(kmx_ret))
kmx_mf = a.out / 'dqi_mf.kmx'
merged = andmerge.apply(str(kmx_ret), chosen, str(kmx_mf))
os.remove(kmx_ret)
rep.update(andmerge=dict(census=mcen, toffolis_removed=merged))
edits, rcen = rankmerge.plan(str(kmx_mf))
kmx_rk = a.out / 'dqi_rk.kmx'
rk = rankmerge.apply(str(kmx_mf), edits, str(kmx_rk))
os.remove(kmx_mf); kmx_mf = kmx_rk
rep.update(rankmerge=dict(census=rcen, toffolis_removed=rk))
cr = km.Circuit.from_file(str(kmx_mf), format='kmx'); cr.to_file(str(out), format='kmb')
rep.update(unretained_qubits=NQ, unretained_static_toffoli_like=T_STATIC, retention=st, qubits=cr.num_qubits,
           static_toffoli_like=cr.operation_statistics().num_toffoli_like, output_sha256=sha(out), seconds=round(time.time() - T0, 1))
del cr
os.remove(kmx_mf)
(a.out / 'driver_report.json').write_text(json.dumps(rep, indent=1) + '\n')
print('BUILT', json.dumps(rep), flush=True)
