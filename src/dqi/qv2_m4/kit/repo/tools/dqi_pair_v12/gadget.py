# SPDX-License-Identifier: Apache-2.0
"""Runs INSIDE tools/dqi_close/sandbox.py: stand-alone value AND phase test of the norm-preserving closing (npclose.py)
against Syed Asad Ali's gf24_nested_norm.emit_closing (Apache-2.0) and confluent_ext.closing_with_case1, with the
official kickmix Simulator. Circuit: registers s (24), v (24), x (24); classical old-target mask (24, stored 0).
  closing(s, v) with a zero old-target mask must give v -> v / s (inv0: s = 0 -> 0), s and x unchanged, ancillas clean,
  phase not flipped. Plain closings are tested on unit s and on (s = 0, v = 0); case-1 closings (x = v) on every class
  including (s = 0, v != 0). Also a prefix + closing round trip (v -> s v -> v). Negative control: the new closing
  without its phase_inverse_six payment must give phase errors.
  args: --src --official --out [--shots N]"""
import argparse, json, os, random, shutil, sys, time, zipfile
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument('--src', type=Path); ap.add_argument('--official', type=Path); ap.add_argument('--out', type=Path)
ap.add_argument('--shots', type=int, default=4096)
a = ap.parse_args()
CODE = Path(__file__).resolve().parent
BUILD = Path('/tmp/conf_build'); shutil.rmtree(BUILD, ignore_errors=True); BUILD.mkdir()
with zipfile.ZipFile(a.src / 'dqi_source_zip') as z:
    z.extractall(BUILD)
ROOT = BUILD / 'dqi_source' / 'src'
OFF = ROOT / 'pro1_controller_bundle' / '1_task' / 'official'; OFF.mkdir(parents=True, exist_ok=True)
shutil.copy(a.official / 'kickmix' / 'kickmix.so', OFF / 'kickmix.so')
VDIR = ROOT / 'pro1_controller_bundle' / '1_task' / 'verifiers' / 'dqi'; VDIR.mkdir(parents=True, exist_ok=True)
shutil.copy(a.official / 'verifiers' / 'dqi' / 'verify_submission_dqi.py', VDIR / 'verify_submission_dqi.py')
sys.path.insert(0, str(ROOT / 'controller_work' / 'after_v3' / 'integration_v7'))
os.chdir(ROOT)
import v7_pipeline as V7
V7.configure()
sys.path.insert(0, str(CODE))
import numpy as np
import kickmix as km
import confluent_ext as CE
import npclose as NP
A = V7.P.Arithmetic
Tail = V7.P.Tail
F = km.GF2Field(12)
ORIG_CLOSE, ORIG_C1 = A.emit_closing, CE.closing_with_case1


def mul(a, b): return A.mul24(a, b, A.DEFAULT_DELTA)
def inv(a): return A.inverse24(a, A.DEFAULT_DELTA)
def norm(s):
    x, y = s & 4095, s >> 12
    return F.mul(x, x) ^ F.mul(x, y) ^ F.mul(A.DEFAULT_DELTA, F.mul(y, y))


rng = random.Random(20261116)
def rand_unit():
    while True:
        s = rng.randrange(1, 1 << 24)
        return s
def with_norm(pred):
    while True:
        s = rng.randrange(1, 1 << 24)
        if pred(norm(s)): return s
def s_from_norm(n):   # s = (x, 0): N = x^2
    return F.pow(n, 2048)
sub64 = [n for n in range(1, 4096) if F.pow(n, 64) == n]
c1 = [n for n in range(1, 4096) if F.pow(n, 65) == 1]
SPECIAL = [1, 2, 4095, 4096, (1 << 24) - 1, 0x800800, 0xFFF000, 0x000FFF]


def classes(case1):
    out = {}
    out['random'] = [(rand_unit(), rng.randrange(1 << 24)) for _ in range(a.shots)]
    out['norm1'] = [(with_norm(lambda n: n == 1) if k % 2 else s_from_norm(1), rng.randrange(1 << 24)) for k in range(64)]
    out['norm_gf64'] = [(s_from_norm(rng.choice(sub64)) if k % 2 else with_norm(lambda n: n in sub64), rng.randrange(1 << 24))
                        for k in range(256)]
    out['child_norm1'] = [(s_from_norm(rng.choice(c1)) if k % 2 else with_norm(lambda n: F.pow(n, 65) == 1), rng.randrange(1 << 24))
                          for k in range(256)]
    out['zero_zero'] = [(0, 0)] * 8
    out['special'] = [(s, v) for s in SPECIAL for v in [0, 1] + SPECIAL]
    if case1:
        out['zero_src'] = [(0, rng.randrange(1, 1 << 24)) for _ in range(256)] + [(0, v) for v in SPECIAL]
    return out


def build(kind, closing):
    b = km.CircuitBuilder(); b.set_max_qubits(200)
    s = b.create_quantum_register(24, 's'); v = b.create_quantum_register(24, 'v'); x = b.create_quantum_register(24, 'x')
    if kind == 'roundtrip':
        rec = A.emit_prefix(b, s, v)
    else:
        m = b.alloc_bits(24); b.bit_store(m, False)
        rec = A.make_record(b, m)
    if closing == 'old':
        ORIG_CLOSE(b, s, v, rec)
    elif closing == 'new':
        NP.emit_closing(A, b, s, v, rec)
    elif closing == 'old_c1':
        ORIG_C1(A, b, s, v, rec, x, Tail)
    elif closing == 'new_c1':
        NP.closing_with_case1(A, b, s, v, rec, x, Tail)
    c = b.finish_circuit()
    return c, s, v, x


def run(c, s, v, x, cases, expect):
    regs = km.array([*s, *v, *x])
    known = set(q.id for q in regs)
    anc = km.array([km.q(k) for k in range(c.num_qubits) if k not in known])
    res = dict(n=0, value_err=0, phase_err=0, anc_err=0, tof=0.0)
    for i in range(0, len(cases), 64):
        ch = cases[i:i + 64]; B = len(ch)
        bits = np.zeros((72, B), dtype=bool); want = np.zeros((72, B), dtype=bool)
        for k, (sv, vv) in enumerate(ch):
            xv = vv
            ov = expect(sv, vv)
            for j in range(24):
                bits[j, k] = sv >> j & 1; bits[24 + j, k] = vv >> j & 1; bits[48 + j, k] = xv >> j & 1
                want[j, k] = sv >> j & 1; want[24 + j, k] = ov >> j & 1; want[48 + j, k] = xv >> j & 1
        sim = km.Simulator(batch_size=B, debug_print=False, counting_operations=True, seed=rng.randrange(1 << 62))
        sim.use_same_registers_as(c)
        sim.write_across_shots(regs, bits)
        sim.do(c)
        ph = sim.read_phase_flipped_across_shots()
        out = sim.read_across_shots(regs)
        ve = (out ^ want).any(axis=0)
        ae = sim.read_across_shots(anc).any(axis=0) if len(anc) else np.zeros(B, dtype=bool)
        res['n'] += B; res['value_err'] += int(ve.sum()); res['anc_err'] += int(ae.sum())
        res['phase_err'] += int((ph & ~ve & ~ae).sum())
        res['tof'] += sim.operation_statistics().num_toffoli_like
    res['tof'] = round(res['tof'] / max(res['n'], 1), 3)
    return res


T0 = time.time()
report = {}
div = lambda sv, vv: mul(vv, inv(sv))
for kind in ('closing', 'roundtrip'):
    for closing in ('old', 'new', 'old_c1', 'new_c1'):
        c, s, v, x = build(kind, closing)
        st = c.operation_statistics().num_toffoli_like
        cl = classes(closing.endswith('c1'))
        if kind == 'roundtrip':
            cl.pop('zero_src', None)
            exp = lambda sv, vv: vv
        else:
            exp = div
        r = {name: run(c, s, v, x, cases, exp) for name, cases in cl.items()}
        report[f'{kind}/{closing}'] = dict(static_toffoli_like=st, qubits=c.num_qubits - 72, classes=r)
        print(kind, closing, st, c.num_qubits - 72, json.dumps({k: (q['n'], q['value_err'], q['anc_err'], q['phase_err'], q['tof'])
                                                                  for k, q in r.items()}), flush=True)

# negative controls: (1) drop the C^-1 X-measure payment; (2) plain closing on (s = 0, v != 0)
import scalar_inverse_phase as SIP
keep = SIP.phase_inverse_six
SIP.phase_inverse_six = lambda builder, source, mask, root=True: None
c, s, v, x = build('closing', 'new')
SIP.phase_inverse_six = keep
cl = classes(False)
report['neg/no_phase_inverse_six'] = {n: run(c, s, v, x, cl[n], div) for n in ('random', 'special')}
c, s, v, x = build('closing', 'new')
report['neg/plain_on_zero_src'] = run(c, s, v, x, classes(True)['zero_src'], div)
print('NEG', json.dumps({k: v for k, v in report.items() if k.startswith('neg')}), flush=True)
report['seconds'] = round(time.time() - T0, 1)
(a.out / 'gadget.json').write_text(json.dumps(report, indent=1) + '\n')
print('DONE', report['seconds'], flush=True)
