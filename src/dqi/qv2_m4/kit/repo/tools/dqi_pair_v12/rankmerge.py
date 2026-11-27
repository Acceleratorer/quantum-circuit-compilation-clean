# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_rank shared-control merge pass (kit v12 post-pass after retain and andmerge, own code).
A group is a maximal run of top-level unconditional CCX onto one target t with no other use of t in between (only CX
into t and X on t, which commute). If at the group's last gate every control wire of every gate in the group still holds
the value it had at its own gate (linear GF(2) value fingerprints), all the group's products can be added at the last
gate instead. Gates whose controls share one value y (on wires y_1..y_k, other controls x_1..x_k on distinct wires) are
merged: a_1.y + ... + a_k.y = (x_1 + ... + x_k).y:
    CX x_2 x_1; ...; CX x_k x_1; CCX x_1 y_1 t; CX x_k x_1; ...; CX x_2 x_1      (k-1 Toffolis removed)
the earlier gates of the cluster are deleted. plan(path) -> (edits, census); apply(src, edits, dst) -> removed."""
import collections, random
ONE = 1 << 64; LOW = ONE - 1

def plan(path, seed=20261116):
    rnd = random.Random(seed).getrandbits
    h = collections.defaultdict(lambda: rnd(64)); memo = {}
    def AND(x, y):
        x0, y0 = x & LOW, y & LOW
        if x0 == 0 or y0 == 0 or x0 == y0: return None
        k = (x0, y0) if x0 < y0 else (y0, x0)
        c = memo.get(k)
        if c is None: c = memo[k] = rnd(64)
        return c ^ (y0 if x >> 64 else 0) ^ (x0 if y >> 64 else 0) ^ (ONE if (x >> 64) and (y >> 64) else 0)
    groups = {}; edits = {}; cen = collections.Counter()
    def close(t):
        E = groups.pop(t, None)
        if not E: return
        G, live = E
        if len(G) < 2: return
        cen['groups'] += 1
        if not live: cen['groups_not_live'] += 1; return
        rest = list(range(len(G))); out = []
        while True:
            cnt = collections.Counter()
            for i in rest:
                for v in {G[i][1], G[i][2]}: cnt[v] += 1
            if not cnt: break
            y, k = cnt.most_common(1)[0]
            if k < 2: break
            cl = [i for i in rest if y in (G[i][1], G[i][2])]
            # wires: y wire and other control wire of each member
            ys, xs = [], []
            for i in cl:
                L, va, vb, a, b = G[i][:5]
                if va == y: ys.append(a); xs.append(b)
                else: ys.append(b); xs.append(a)
            if len(set(xs)) != len(xs) or set(xs) & set(ys) or t in xs or t in ys:
                cen['cluster_wire_clash'] += 1; break
            out.append((cl, xs, ys)); rest = [i for i in rest if i not in cl]
        if not out: return
        last = G[-1][0]; text = []
        for cl, xs, ys in out:
            x1 = xs[0]; fold = [f'CX {x} {x1}\n' for x in xs[1:]]
            text += fold + [f'CCX {x1} {ys[0]} {t}\n'] + fold[::-1]
            for i in cl:
                if G[i][0] != last: edits[G[i][0]] = ''
            cen['clusters'] += 1; cen['toffolis_removed'] += len(cl) - 1; cen[f'cluster_size_{len(cl)}'] += 1
        last_in = any(G[-1][0] == G[i][0] for cl, _, _ in out for i in cl)
        edits[last] = ''.join(text) + ('' if last_in else KEEP)
    KEEP = '\0KEEP\0'
    def cw(q):
        if q in groups: close(q)
    depth = 0; written = []
    with open(path) as f:
        for L, line in enumerate(f):
            p = line.split()
            if not p: continue
            op = p[0]
            if op in ('INFO_TAG', 'APPEND_TO_REGISTER', 'REGISTER', 'DEBUG_PRINT', 'BIT_INVERT', 'BIT_STORE0', 'BIT_STORE1', 'NEG'): continue
            if op == 'PUSH_CONDITION': depth += 1; written.append(set()); continue
            if op == 'POP_CONDITION':
                depth -= 1; w = written.pop()
                for q in w: cw(q); h[q] = rnd(64)
                if written: written[-1] |= w
                continue
            cond = len(p) >= 3 and p[-2] == 'if'
            if cond: p = p[:-2]
            qs = [x for x in p[1:] if x[0] == 'q']
            if depth or cond:                       # only top-level unconditional groups are merged
                for q in qs: cw(q)
                if op not in ('Z', 'CZ', 'CCZ', 'Z_POW'):
                    tg = qs[-1:] if op in ('X', 'CX', 'CCX', 'HMR', 'R') else qs if op == 'SWAP' else qs[1:]
                    if depth: written[-1].update(tg)
                    else:
                        for q in tg: h[q] = rnd(64)
                continue
            if op == 'CX':
                a, b = qs; cw(a); h[b] ^= h[a]; continue
            if op == 'X': h[qs[0]] ^= ONE; continue
            if op == 'CCX':
                a, b, t = qs; cw(a); cw(b)
                P = AND(h[a], h[b])
                if P is None:
                    cw(t); h[t] = rnd(64); continue      # linear product: not grouped (none in kit v11)
                E = groups.get(t)
                if E is None: E = groups[t] = [[], True]
                else: E[1] = all(h[g[3]] == g[5] and h[g[4]] == g[6] for g in E[0])
                E[0].append((L, h[a] & LOW, h[b] & LOW, a, b, h[a], h[b]))
                h[t] ^= P; continue
            for q in qs: cw(q)
            if op in ('Z', 'CZ', 'CCZ', 'Z_POW'): continue
            if op == 'SWAP': x, y = qs; h[x], h[y] = h[y], h[x]
            elif op in ('R', 'HMR'): h[qs[0]] = 0
            elif op == 'CSWAP':
                c, x, y = qs; P = AND(h[c], h[x] ^ h[y])
                if P is None: h[x] = rnd(64); h[y] = rnd(64)
                else: h[x] ^= P; h[y] ^= P
            else:
                for q in qs: h[q] = rnd(64)
    for t in list(groups): close(t)
    return edits, dict(cen)

def apply(src, edits, dst):
    removed = 0
    with open(src) as f, open(dst, 'w') as g:
        for L, line in enumerate(f):
            e = edits.get(L)
            if e is None: g.write(line); continue
            assert line.startswith('CCX ') and ' if ' not in line, (L, line)
            if e.endswith('\0KEEP\0'): g.write(e[:-6]); g.write(line)
            else: g.write(e)
            removed += 1 - e.count('CCX ') - (1 if e.endswith('\0KEEP\0') else 0)
    return removed
