# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_mf AND-merge pass (kit v10 post-pass, own code). Two top-level unconditional CCX that add the same
product P (equal value fingerprints from retain.scan) to targets t1 (line p1) and t2 (line p2 > p1, consecutive in the
product's occurrence list) are merged into one Toffoli when one target has no non-commuting use (control, Z-type,
SWAP, CSWAP, HMR, R) strictly between them:
  t2 free : p1 -> CX t1 t2 ; CCX a1 b1 t1 ; CX t1 t2 ; p2 dropped
  t1 free : p1 dropped ; p2 -> CX t1 t2 ; CCX a2 b2 t1 ; CX t1 t2
  same target, no use between : both dropped
(the CX pair adds t1's change, P, to t2). Pairs non-overlapping, greedy by p2. plan() then apply()."""
import collections, json
import retain

def plan(path):
    occ, idle, n = retain.scan(path, retain.read_registers(path))
    del idle
    queries = collections.defaultdict(list)
    for P, lst in occ.items():
        for (p1, a1, b1, t1), (p2, a2, b2, t2) in zip(lst, lst[1:]):
            queries[p2].append((p1, a1, b1, t1, a2, b2, t2))
    del occ
    nc = collections.defaultdict(lambda: -1)
    cands = []
    with open(path) as f:
        for L, line in enumerate(f):
            if L in queries:
                for (p1, a1, b1, t1, a2, b2, t2) in queries[L]:
                    f1 = nc[t1] <= p1; f2 = nc[t2] <= p1
                    if t1 == t2: cls = 'cancel' if f1 else 'blocked_same'
                    elif f2 and t1 not in (a1, b1) and t2 not in (a1, b1): cls = 't2free'
                    elif f1 and t1 not in (a2, b2) and t2 not in (a2, b2): cls = 't1free'
                    else: cls = 'blocked'
                    cands.append((p1, L, cls))
            c0 = line[0]
            if c0 in 'AIBP' or line.startswith('REG'): continue
            p = line.split(); op = p[0]
            if len(p) >= 3 and p[-2] == 'if': p = p[:-2]
            qs = [x for x in p[1:] if x[0] == 'q']
            if op in ('CX', 'CCX'):
                for x in qs[:-1]: nc[x] = L
            elif op != 'X' and op != 'NEG':
                for x in qs: nc[x] = L
    used = set(); chosen = []; cen = collections.Counter()
    for p1, p2, cls in sorted(cands, key=lambda c: (c[1], c[0])):
        cen['all_' + cls] += 1
        if cls.startswith('blocked'): continue
        if p1 in used or p2 in used: cen['overlap_' + cls] += 1; continue
        used.add(p1); used.add(p2); chosen.append((p1, p2, cls)); cen['chosen_' + cls] += 1
    return chosen, dict(cen)

def apply(inp, chosen, out):
    act = {}
    for p1, p2, cls in chosen:
        act[p1] = (cls, 1, p2); act[p2] = (cls, 2, p1)
    need = {p2 for p1, p2, cls in chosen if cls == 't2free'}
    tgt = {}
    with open(inp) as f:
        for L, line in enumerate(f):
            if L in need: tgt[L] = line.split()[3]
    pend_t1 = {}; removed = 0
    with open(inp) as f, open(out, 'w') as g:
        for L, line in enumerate(f):
            a = act.get(L)
            if a is None: g.write(line); continue
            cls, role, other = a
            p = line.split(); assert p[0] == 'CCX' and len(p) == 4, (L, line)
            if cls == 'cancel': removed += 1; continue
            if cls == 't2free':
                if role == 1:
                    t1, t2 = p[3], tgt[other]
                    g.write('CX %s %s\n%sCX %s %s\n' % (t1, t2, line, t1, t2)); removed += 1
                continue
            if role == 1: pend_t1[other] = p[3]; continue
            t1, t2 = pend_t1.pop(L), p[3]
            g.write('CX %s %s\nCCX %s %s %s\nCX %s %s\n' % (t1, t2, p[1], p[2], t1, t1, t2)); removed += 1
    assert not pend_t1
    return removed
