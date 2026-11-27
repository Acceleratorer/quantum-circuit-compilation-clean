from collections import defaultdict, Counter
from pathlib import Path
import random
import sys

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('tmp/qv2-static.kmx')
ONE = 1 << 64
LOW = ONE - 1
rnd = random.Random(20261128).getrandbits
h = defaultdict(lambda: rnd(64))
memo = {}

def AND(x, y):
    x0, y0 = x & LOW, y & LOW
    if x0 == 0 or y0 == 0 or x0 == y0:
        return None
    k = (x0, y0) if x0 < y0 else (y0, x0)
    c = memo.get(k)
    if c is None:
        c = memo[k] = rnd(64)
    return c ^ (y0 if x >> 64 else 0) ^ (x0 if y >> 64 else 0) ^ (ONE if (x >> 64) and (y >> 64) else 0)

total = Counter()
examples = []

def close(groups):
    for t, E in list(groups.items()):
        G, live = E
        if len(G) < 2 or not live:
            continue
        total['groups'] += 1
        rest = list(range(len(G)))
        out = []
        while True:
            cnt = Counter()
            for i in rest:
                cnt[G[i][1]] += 1
                cnt[G[i][2]] += 1
            if not cnt:
                break
            y, k = cnt.most_common(1)[0]
            if k < 2:
                break
            cl = [i for i in rest if y in (G[i][1], G[i][2])]
            ys, xs = [], []
            for i in cl:
                L, va, vb, a, b, ha, hb = G[i]
                if va == y:
                    ys.append(a); xs.append(b)
                else:
                    ys.append(b); xs.append(a)
            if len(set(xs)) != len(xs) or set(xs) & set(ys) or t in xs or t in ys:
                total['wire_clash'] += 1
                break
            out.append((cl, xs, ys))
            rest = [i for i in rest if i not in cl]
        for cl, xs, ys in out:
            total['clusters'] += 1
            total['removed'] += len(cl) - 1
            total[f'size{len(cl)}'] += 1
            if len(examples) < 10:
                examples.append((t, len(cl), xs, ys, G[cl[-1]][0]))

frames = []
line = 0
with p.open(encoding='utf-8') as f:
    for s in f:
        line += 1
        parts = s.split()
        if not parts:
            continue
        op = parts[0]
        if op == 'PUSH_CONDITION':
            frames.append(({}, {}, True))
            continue
        if op == 'POP_CONDITION':
            old, groups, live = frames.pop()
            close(groups)
            for q, v in old.items():
                h[q] = v
            continue
        qs = [x for x in parts[1:] if x.startswith('q')]
        if not frames:
            if op == 'CX' and len(qs) >= 2:
                a, b = qs[:2]; h[b] ^= h[a]
            elif op == 'X' and qs:
                h[qs[0]] ^= ONE
            elif op == 'SWAP' and len(qs) >= 2:
                a, b = qs[:2]; h[a], h[b] = h[b], h[a]
            elif op == 'CCX' and len(qs) >= 3:
                a, b, t = qs[:3]; z = AND(h[a], h[b])
                if z is None: h[t] = rnd(64)
                else: h[t] ^= z
            elif op not in ('APPEND_TO_REGISTER', 'REGISTER', 'INFO_TAG', 'DEBUG_PRINT', 'BIT_STORE0', 'BIT_STORE1', 'NEG'):
                for q in qs: h[q] = rnd(64)
            continue
        old, groups, live = frames[-1]
        def save(q):
            if q not in old:
                old[q] = h[q]
        for q in qs:
            save(q)
        def flush(q):
            E = groups.pop(q, None)
            if E and len(E[0]) >= 2:
                close({q: E})
        if op == 'CX' and len(qs) >= 2:
            a, b = qs[:2]; flush(a); h[b] ^= h[a]
        elif op == 'X' and qs:
            h[qs[0]] ^= ONE
        elif op == 'CCX' and len(qs) >= 3:
            a, b, t = qs[:3]; flush(a); flush(b); z = AND(h[a], h[b])
            if z is None:
                flush(t); h[t] = rnd(64)
            else:
                E = groups.get(t)
                if E is None:
                    E = groups[t] = [[], True]
                else:
                    E[1] = all(h[g[3]] == g[5] and h[g[4]] == g[6] for g in E[0])
                E[0].append((line, h[a] & LOW, h[b] & LOW, a, b, h[a], h[b]))
                h[t] ^= z
        elif op == 'SWAP' and len(qs) >= 2:
            a, b = qs[:2]; flush(a); flush(b); h[a], h[b] = h[b], h[a]
        elif op in ('Z', 'CZ', 'CCZ', 'Z_POW', 'INFO_TAG', 'APPEND_TO_REGISTER', 'REGISTER', 'DEBUG_PRINT', 'BIT_STORE0', 'BIT_STORE1', 'NEG'):
            pass
        else:
            for q in qs: flush(q)
            for q in qs: h[q] = rnd(64)

print(dict(total))
print('examples', examples)
