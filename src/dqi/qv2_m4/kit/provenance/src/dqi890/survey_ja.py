# SPDX-License-Identifier: Apache-2.0
# Derived from the compiled DQI decoder of Syed Asad Ali (Apache-2.0); original builder: Syed Asad Ali (portfolio v13).
"""Lane dqi890: survey of all J_A halves (186 ANDs, followed by a 173-AND J_B half) in the forward extractor steps.
For each: t_new from the n' law, t_old = the even t for which the e law sqrt(c0 + c1 (alpha + kappa)) m has a linear
output basis (kappa = q_t(alpha)), s = t_old xor t_new; exports one verified kernel per new s with ja_tensor.py.
  survey_ja.py KMX SLOTS_DIV.json WORKDIR PROBEDIR"""
import json, os, pickle, subprocess, sys
import numpy as np
kmx, slots, W, PR = sys.argv[1:5]
hits = json.load(open(slots))['new']['lines'][:30]
steps = [(hits[2 * k], hits[2 * k + 2] if k < 14 else 21660000) for k in range(15)]
PY = [sys.executable, '-I', '-B']; SRC = '<REPO>/src/dqi890/'
def lw(f):
    s = set(); x = f >> 1; q = 0
    while x:
        if x & 1: s.add(q)
        x >>= 1; q += 1
    return s
done_s = {}; table = []
for k, (a, b) in enumerate(steps, 1):
    pk = f'{W}/step{k}.pkl'
    if not os.path.exists(pk): subprocess.run(PY + [SRC + 'symtrack.py', kmx, str(a), str(b), pk], check=True, capture_output=True)
    d = pickle.load(open(pk, 'rb')); P = d['prods']
    tags = []
    for n, l, r, t in P:
        s = lw(l); g = {q // 24 for q in s}
        tags.append(min(g) if len(g) == 1 and s and max(s) < 840 else None)
    runs = []
    for i, t in enumerate(tags):
        if runs and runs[-1][0] == t: runs[-1][2] = i
        else: runs.append([t, i, i])
    halves = [(t, i0, i1) for t, i0, i1 in runs if t is not None and (i1 - i0 + 1) in (173, 186)]
    for (t, i0, i1), nxt in zip(halves, halves[1:] + [None]):
        if i1 - i0 + 1 != 186 or nxt is None or nxt[2] - nxt[1] + 1 != 173: continue
        la, lb = P[i0 - 1][0] + 1, P[i1][0] + 1; lc = P[nxt[2]][0] + 1
        pa, pb = f'{W}/st{k}_h{t}_A.pkl', f'{W}/st{k}_h{t}_B.pkl'
        for p, x, y in ((pa, la, lb), (pb, lb, lc)):
            if not os.path.exists(p): subprocess.run(PY + [SRC + 'symtrack.py', kmx, str(x), str(y), p], check=True, capture_output=True)
        da = pickle.load(open(pa, 'rb'))
        groups = sorted({w // 24 * 24 for w in range(840) if da['final'][w] != 1 << (w + 1)} - {t * 24, t * 24 - 24})
        E0 = groups[-1]
        res = None
        for to in [t + 2] + [x for x in range(0, 80, 2) if x != t + 2]:
            out = f'{PR}/kernel_JA_tmp.json'
            r = subprocess.run(PY + [SRC + 'ja_tensor.py', pa, str(t * 24), pb, str(nxt[0] * 24), str(E0), 'AUTO', str(to), out], capture_output=True, text=True)
            if 'written' in r.stdout: res = (to, r.stdout); break
        if res is None:
            table.append(dict(step=k, head=t, result='no t_old found')); print(k, t, 'no t_old'); continue
        info = json.load(open(f'{PR}/kernel_JA_tmp.json')); s = info['s']
        table.append(dict(step=k, head=t, t_new=info['t_new'], t_old=info['t_old'], s=s, kappa=info['kappa'], lines=info['source_lines']))
        print(k, t, 't_new', info['t_new'], 't_old', info['t_old'], 's', s, flush=True)
        if s not in done_s:
            os.replace(f'{PR}/kernel_JA_tmp.json', f'{PR}/kernel_JA_s{s}.json'); done_s[s] = (k, t)
json.dump(table, open(f'{PR}/ja_survey.json', 'w'), indent=1)
print('distinct s', sorted(done_s))
