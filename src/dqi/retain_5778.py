"""Reproduce the 5778cdd5 DQI retained-product circuit.

Derived from Asterios Panoras's public QCC 25.449 notebook and Areeb Ali's
Apache-2.0 retention method. The verifier-facing input is the public
4c81b726 .kmb; the builder changes two repeated products and adds two phase
correction bits without changing the 892-qubit register layout.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib

import kickmix as km
'''retain2: product retention with scratch-lifetime renaming.
Derived from Areeb Ali's `retain.py` (notebook product-retention-133-free-toffolis-lb-25-40767, Apache 2.0): the value-fingerprint
scan, idle windows, rewrite patterns and the HMR/CZ uncompute are his. New here: busy periods + global interval colouring.'''
import random, collections, bisect, re
import numpy as np

def read_registers(path):
    regq = set()
    for line in pathlib.Path(path).read_text(errors="ignore").splitlines():
        if line.startswith("APPEND_TO_REGISTER"):
            fields = line.split()
            if len(fields) > 1 and fields[1].startswith("q"):
                regq.add(fields[1])
    return regq

def scan(path, regq, nq, seed=20261112):
    '''Forward pass with value fingerprints (Areeb). Returns occ, idle, n, maxbit.
    occ: product fp -> [(line,a,b,t)]; idle: scratch qubit -> [(z, L, ins)] windows (zero & untouched after line z, before L).
    Scratch qubits start idle with z=-1 (new vs Areeb).'''
    rnd = random.Random(seed).getrandbits
    ONE = 1 << 64; LOW = ONE - 1
    h = collections.defaultdict(int)
    for q in regq: h[q] = rnd(64)
    memo = {}; occ = collections.defaultdict(list); idle = collections.defaultdict(list)
    zs = {}
    for i in range(nq):
        q = f"q{i}"
        if q not in regq: zs[q] = -1
    depth = 0; written = []; block_start = [0]; maxbit = 0
    bre = re.compile(r'b(\d+)')
    def AND(x, y):
        xn, x0, yn, y0 = x >> 64, x & LOW, y >> 64, y & LOW
        if x0 == 0 or y0 == 0 or x0 == y0:
            core = x0 if (x0 == y0) else 0; free = True
        else:
            k = (x0, y0) if x0 < y0 else (y0, x0)
            core = memo.get(k)
            if core is None: core = memo[k] = rnd(64)
            free = False
        return core ^ (y0 if xn else 0) ^ (x0 if yn else 0) ^ (ONE if (xn and yn) else 0), free
    def touch(q, L):
        z = zs.pop(q, None)
        if z is not None:
            ins = (L - 1) if depth == 0 else (block_start[0] - 1)
            if ins >= z: idle[q].append((z, L, ins))
    def settle(q, L):
        if depth == 0 and h[q] == 0 and q not in regq: zs[q] = L
        if written: written[-1].add(q)
    lineno = -1
    with open(path) as f:
        for lineno, line in enumerate(f):
            c0 = line[0]
            if c0 == 'C' and line[1] == 'X':
                p = line.split()
                if len(p) == 3:
                    a = p[1]; b = p[2]
                    if a in zs: touch(a, lineno); zs[a] = lineno
                    if b in zs: touch(b, lineno)
                    v = h[b] ^ h[a]; h[b] = v
                    if depth == 0:
                        if not v and b not in regq: zs[b] = lineno
                    else: written[-1].add(b)
                    continue
            p = line.split()
            if not p: continue
            op = p[0]
            if op == 'BIT_INVERT' or op == 'BIT_STORE0' or op == 'BIT_STORE1':
                for t in p[1:]:
                    if t[0] == 'b':
                        v = int(t[1:]); 
                        if v > maxbit: maxbit = v
                continue
            if op in ('INFO_TAG', 'APPEND_TO_REGISTER', 'REGISTER', 'DEBUG_PRINT', 'NEG'): continue
            if op == 'PUSH_CONDITION':
                if depth == 0: block_start[0] = lineno
                depth += 1; written.append(set()); continue
            if op == 'POP_CONDITION':
                if depth:
                    depth -= 1; w = written.pop()
                    for q in w: h[q] = rnd(64); zs.pop(q, None)
                    if written: written[-1] |= w
                continue
            cond = None
            if len(p) >= 3 and p[-2] == 'if': cond = p[-1]; p = p[:-2]
            for t in p[1:]:
                if t[0] == 'b':
                    v = int(t[1:])
                    if v > maxbit: maxbit = v
            if cond is not None:
                v = int(cond[1:])
                if v > maxbit: maxbit = v
            qs = [t for t in p[1:] if t[0] == 'q']
            zero_before = {q: (q in zs) for q in qs}
            for q in qs: touch(q, lineno)
            if op in ('Z', 'CZ', 'CCZ', 'Z_POW'):
                if cond is None and depth == 0:
                    for q in qs:
                        if zero_before[q]: zs[q] = lineno
                continue
            if cond is not None:
                for q in (qs[-1:] if op in ('X', 'CX', 'CCX', 'HMR', 'R') else qs if op in ('SWAP',) else qs[1:]):
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
                for q in qs:
                    if zero_before[q] and h[q] == 0 and depth == 0: zs[q] = lineno
                continue
            if op == 'X': t = qs[0]; h[t] ^= ONE; settle(t, lineno)
            elif op == 'CX':
                h[qs[1]] ^= h[qs[0]]; settle(qs[1], lineno); settle(qs[0], lineno)
            elif op == 'SWAP':
                a, b = qs; h[a], h[b] = h[b], h[a]; settle(a, lineno); settle(b, lineno)
            elif op in ('R', 'HMR'):
                t = qs[0]; h[t] = 0; settle(t, lineno)
            elif op == 'CCX':
                a, b, t = qs
                P, free = AND(h[a], h[b])
                if not free and P and depth == 0: occ[P].append((lineno, a, b, t))
                h[t] ^= P; settle(t, lineno); settle(a, lineno); settle(b, lineno)
            elif op == 'CSWAP':
                c, a, b = qs
                P, free = AND(h[c], h[a] ^ h[b]); h[a] ^= P; h[b] ^= P
                for q in qs: settle(q, lineno)
            else:
                for q in qs:
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
    n = lineno + 1
    for q, z in zs.items():
        if n - 1 >= z: idle[q].append((z, n, n - 1))
    return occ, idle, n, maxbit


def scan_snap(path, regq, nq, snap_lines, snaps, lmsnap, seed=20261112):
    '''Forward pass with value fingerprints (Areeb). Returns occ, idle, n, maxbit.
    occ: product fp -> [(line,a,b,t)]; idle: scratch qubit -> [(z, L, ins)] windows (zero & untouched after line z, before L).
    Scratch qubits start idle with z=-1 (new vs Areeb).'''
    rnd = random.Random(seed).getrandbits
    ONE = 1 << 64; LOW = ONE - 1
    h = collections.defaultdict(int)
    for q in regq: h[q] = rnd(64)
    memo = {}; occ = collections.defaultdict(list); idle = collections.defaultdict(list)
    zs = {}
    for i in range(nq):
        q = f"q{i}"
        if q not in regq: zs[q] = -1
    depth = 0; written = []; block_start = [0]; maxbit = 0
    lm = {}
    C64 = 0x9E3779B97F4A7C15
    qn = [f'q{i}' for i in range(nq)]
    bre = re.compile(r'b(\d+)')
    def AND(x, y):
        xn, x0, yn, y0 = x >> 64, x & LOW, y >> 64, y & LOW
        if x0 == 0 or y0 == 0 or x0 == y0:
            core = x0 if (x0 == y0) else 0; free = True
        else:
            k = (x0, y0) if x0 < y0 else (y0, x0)
            core = memo.get(k)
            if core is None: core = memo[k] = rnd(64)
            free = False
        return core ^ (y0 if xn else 0) ^ (x0 if yn else 0) ^ (ONE if (xn and yn) else 0), free
    def touch(q, L):
        z = zs.pop(q, None)
        if z is not None:
            ins = (L - 1) if depth == 0 else (block_start[0] - 1)
            if ins >= z: idle[q].append((z, L, ins))
    def settle(q, L):
        if depth == 0 and h[q] == 0 and q not in regq: zs[q] = L
        if written: written[-1].add(q)
    lineno = -1
    with open(path) as f:
        for lineno, line in enumerate(f):
            if lineno in snap_lines:
                snaps[lineno] = np.array([(h[q] & LOW) ^ (C64 if (h[q] >> 64) else 0) for q in qn], dtype=np.uint64)
                lmsnap[lineno] = np.array([lm.get(q, -1) for q in qn], dtype=np.int64)
            c0 = line[0]
            if c0 == 'C' and line[1] == 'X':
                p = line.split()
                if len(p) == 3:
                    a = p[1]; b = p[2]; lm[a] = lineno; lm[b] = lineno
                    if a in zs: touch(a, lineno); zs[a] = lineno
                    if b in zs: touch(b, lineno)
                    v = h[b] ^ h[a]; h[b] = v
                    if depth == 0:
                        if not v and b not in regq: zs[b] = lineno
                    else: written[-1].add(b)
                    continue
            p = line.split()
            if not p: continue
            op = p[0]
            if op == 'BIT_INVERT' or op == 'BIT_STORE0' or op == 'BIT_STORE1':
                for t in p[1:]:
                    if t[0] == 'b':
                        v = int(t[1:]); 
                        if v > maxbit: maxbit = v
                continue
            if op in ('INFO_TAG', 'APPEND_TO_REGISTER', 'REGISTER', 'DEBUG_PRINT', 'NEG'): continue
            if op == 'PUSH_CONDITION':
                if depth == 0: block_start[0] = lineno
                depth += 1; written.append(set()); continue
            if op == 'POP_CONDITION':
                if depth:
                    depth -= 1; w = written.pop()
                    for q in w: h[q] = rnd(64); zs.pop(q, None)
                    if written: written[-1] |= w
                continue
            cond = None
            if len(p) >= 3 and p[-2] == 'if': cond = p[-1]; p = p[:-2]
            for t in p[1:]:
                if t[0] == 'b':
                    v = int(t[1:])
                    if v > maxbit: maxbit = v
            if cond is not None:
                v = int(cond[1:])
                if v > maxbit: maxbit = v
            qs = [t for t in p[1:] if t[0] == 'q']
            for q in qs: lm[q] = lineno
            zero_before = {q: (q in zs) for q in qs}
            for q in qs: touch(q, lineno)
            if op in ('Z', 'CZ', 'CCZ', 'Z_POW'):
                if cond is None and depth == 0:
                    for q in qs:
                        if zero_before[q]: zs[q] = lineno
                continue
            if cond is not None:
                for q in (qs[-1:] if op in ('X', 'CX', 'CCX', 'HMR', 'R') else qs if op in ('SWAP',) else qs[1:]):
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
                for q in qs:
                    if zero_before[q] and h[q] == 0 and depth == 0: zs[q] = lineno
                continue
            if op == 'X': t = qs[0]; h[t] ^= ONE; settle(t, lineno)
            elif op == 'CX':
                h[qs[1]] ^= h[qs[0]]; settle(qs[1], lineno); settle(qs[0], lineno)
            elif op == 'SWAP':
                a, b = qs; h[a], h[b] = h[b], h[a]; settle(a, lineno); settle(b, lineno)
            elif op in ('R', 'HMR'):
                t = qs[0]; h[t] = 0; settle(t, lineno)
            elif op == 'CCX':
                a, b, t = qs
                P, free = AND(h[a], h[b])
                if not free and P and depth == 0: occ[P].append((lineno, a, b, t))
                h[t] ^= P; settle(t, lineno); settle(a, lineno); settle(b, lineno)
            elif op == 'CSWAP':
                c, a, b = qs
                P, free = AND(h[c], h[a] ^ h[b]); h[a] ^= P; h[b] ^= P
                for q in qs: settle(q, lineno)
            else:
                for q in qs:
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
    n = lineno + 1
    for q, z in zs.items():
        if n - 1 >= z: idle[q].append((z, n, n - 1))
    return occ, idle, n, maxbit



def scan_span(path, regq, nq, hits, stats, seed=20261112):
    '''Forward pass with value fingerprints (Areeb). Returns occ, idle, n, maxbit.
    occ: product fp -> [(line,a,b,t)]; idle: scratch qubit -> [(z, L, ins)] windows (zero & untouched after line z, before L).
    Scratch qubits start idle with z=-1 (new vs Areeb).'''
    rnd = random.Random(seed).getrandbits
    ONE = 1 << 64; LOW = ONE - 1
    h = collections.defaultdict(int)
    for q in regq: h[q] = rnd(64)
    memo = {}; occ = collections.defaultdict(list); idle = collections.defaultdict(list)
    zs = {}
    for i in range(nq):
        q = f"q{i}"
        if q not in regq: zs[q] = -1
    depth = 0; written = []; block_start = [0]; maxbit = 0
    lm = {}
    C64 = 0x9E3779B97F4A7C15
    qn = [f'q{i}' for i in range(nq)]
    bre = re.compile(r'b(\d+)')
    def AND(x, y):
        xn, x0, yn, y0 = x >> 64, x & LOW, y >> 64, y & LOW
        if x0 == 0 or y0 == 0 or x0 == y0:
            core = x0 if (x0 == y0) else 0; free = True
        else:
            k = (x0, y0) if x0 < y0 else (y0, x0)
            core = memo.get(k)
            if core is None: core = memo[k] = rnd(64)
            free = False
        return core ^ (y0 if xn else 0) ^ (x0 if yn else 0) ^ (ONE if (xn and yn) else 0), free
    def touch(q, L):
        z = zs.pop(q, None)
        if z is not None:
            ins = (L - 1) if depth == 0 else (block_start[0] - 1)
            if ins >= z: idle[q].append((z, L, ins))
    def settle(q, L):
        if depth == 0 and h[q] == 0 and q not in regq: zs[q] = L
        if written: written[-1].add(q)
    lineno = -1
    with open(path) as f:
        for lineno, line in enumerate(f):
            c0 = line[0]
            if c0 == 'C' and line[1] == 'X':
                p = line.split()
                if len(p) == 3:
                    a = p[1]; b = p[2]; lm[a] = lineno; lm[b] = lineno
                    if a in zs: touch(a, lineno); zs[a] = lineno
                    if b in zs: touch(b, lineno)
                    v = h[b] ^ h[a]; h[b] = v
                    if depth == 0:
                        if not v and b not in regq: zs[b] = lineno
                    else: written[-1].add(b)
                    continue
            p = line.split()
            if not p: continue
            op = p[0]
            if op == 'BIT_INVERT' or op == 'BIT_STORE0' or op == 'BIT_STORE1':
                for t in p[1:]:
                    if t[0] == 'b':
                        v = int(t[1:]); 
                        if v > maxbit: maxbit = v
                continue
            if op in ('INFO_TAG', 'APPEND_TO_REGISTER', 'REGISTER', 'DEBUG_PRINT', 'NEG'): continue
            if op == 'PUSH_CONDITION':
                if depth == 0: block_start[0] = lineno
                depth += 1; written.append(set()); continue
            if op == 'POP_CONDITION':
                if depth:
                    depth -= 1; w = written.pop()
                    for q in w: h[q] = rnd(64); zs.pop(q, None)
                    if written: written[-1] |= w
                continue
            cond = None
            if len(p) >= 3 and p[-2] == 'if': cond = p[-1]; p = p[:-2]
            for t in p[1:]:
                if t[0] == 'b':
                    v = int(t[1:])
                    if v > maxbit: maxbit = v
            if cond is not None:
                v = int(cond[1:])
                if v > maxbit: maxbit = v
            qs = [t for t in p[1:] if t[0] == 'q']
            for q in qs: lm[q] = lineno
            zero_before = {q: (q in zs) for q in qs}
            for q in qs: touch(q, lineno)
            if op in ('Z', 'CZ', 'CCZ', 'Z_POW'):
                if cond is None and depth == 0:
                    for q in qs:
                        if zero_before[q]: zs[q] = lineno
                continue
            if cond is not None:
                for q in (qs[-1:] if op in ('X', 'CX', 'CCX', 'HMR', 'R') else qs if op in ('SWAP',) else qs[1:]):
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
                for q in qs:
                    if zero_before[q] and h[q] == 0 and depth == 0: zs[q] = lineno
                continue
            if op == 'X': t = qs[0]; h[t] ^= ONE; settle(t, lineno)
            elif op == 'CX':
                h[qs[1]] ^= h[qs[0]]; settle(qs[1], lineno); settle(qs[0], lineno)
            elif op == 'SWAP':
                a, b = qs; h[a], h[b] = h[b], h[a]; settle(a, lineno); settle(b, lineno)
            elif op in ('R', 'HMR'):
                t = qs[0]; h[t] = 0; settle(t, lineno)
            elif op == 'CCX':
                a, b, t = qs
                P, free = AND(h[a], h[b])
                if not free and P and depth == 0:
                    occ[P].append((lineno, a, b, t))
                    stats['ccx'] += 1
                    vals = np.array([(h[q] & LOW) ^ (C64 if (h[q] >> 64) else 0) for q in qn], dtype=np.uint64)
                    ti = int(t[1:]); vals[ti] = 0
                    Pc = np.uint64((P & LOW) ^ (C64 if (P >> 64) else 0))
                    one = np.nonzero(vals == Pc)[0]
                    if len(one): hits.append((lineno, 1, tuple(int(x) for x in one[:3]), a, b, t)); stats['one'] += 1
                    else:
                        xs = vals ^ Pc
                        m = np.nonzero(np.isin(xs, vals) & (vals != 0))[0]
                        if len(m): hits.append((lineno, 2, tuple(int(x) for x in m[:3]), a, b, t)); stats['two'] += 1
                h[t] ^= P; settle(t, lineno); settle(a, lineno); settle(b, lineno)
            elif op == 'CSWAP':
                c, a, b = qs
                P, free = AND(h[c], h[a] ^ h[b]); h[a] ^= P; h[b] ^= P
                for q in qs: settle(q, lineno)
            else:
                for q in qs:
                    h[q] = rnd(64)
                    if written: written[-1].add(q)
    n = lineno + 1
    for q, z in zs.items():
        if n - 1 >= z: idle[q].append((z, n, n - 1))
    return occ, idle, n, maxbit



def busy_periods(idle, n):
    '''per scratch qubit: list of closed line ranges (S, Z) in which the qubit is not provably zero-and-untouched.
    Windows (z,L,ins): idle after line z until L; busy period i = [ins_i+1, z_{i+1}] (last: to n-1 if the final window does not reach n).'''
    per = {}; tails = {}
    for q, ws in idle.items():
        ws = sorted(ws); out = []
        for i in range(len(ws) - 1):
            S = ws[i][2] + 1; Z = ws[i + 1][0]
            assert S <= Z and (not out or out[-1][1] < S), (q, ws[i], ws[i+1])
            out.append((S, Z))
        last = ws[-1]
        if last[1] < n:     # last window ends before the file does: busy until the end
            out.append((last[2] + 1, n - 1)); tails[q] = (last[2] + 1, n - 1)
        per[q] = out
    busy_periods.tails = tails
    return per

def plan(occ, per, nscratch, first_new_bit, order='span', max_span=None, forbid=()):
    '''Choose repeated-product pairs to retain so that, at every line, (busy scratch lifetimes + retained products) <= nscratch,
    then colour all lifetimes onto the scratch qubits (interval colouring), renaming whole busy periods.
    Returns (runs, colour, stats). runs: list of (P, k0, k1) = occurrences k0..k1 of product P held in one scratch qubit.
    colour: dict (q,S,Z)->new qubit for busy periods ; run_host: run index -> qubit.'''
    pairs = []
    for P, lst in occ.items():
        for k in range(len(lst) - 1):
            st, en = lst[k][0], lst[k + 1][0]
            if max_span is None or en - st <= max_span: pairs.append((st, en, P, k))
    pts = set()
    for q, ps in per.items():
        for S, Z in ps: pts.add(S); pts.add(Z + 1)
    for st, en, P, k in pairs: pts.update((st, st + 1, en, en + 1))
    B = np.array(sorted(pts), dtype=np.int64); m = len(B)
    diff = np.zeros(m + 1, dtype=np.int32)
    for q, ps in per.items():
        for S, Z in ps:
            diff[np.searchsorted(B, S)] += 1; diff[np.searchsorted(B, Z + 1)] -= 1
    cov = np.cumsum(diff)[:m].astype(np.int32)
    base_max = int(cov.max())
    if order == 'span': pairs.sort(key=lambda x: (x[1] - x[0], x[0]))
    elif order == 'end': pairs.sort(key=lambda x: (x[1], x[0]))
    elif order == 'spanseg':
        pairs.sort(key=lambda x: (np.searchsorted(B, x[1]) - np.searchsorted(B, x[0]), x[0]))
    chosen = set()
    for st, en, P, k in pairs:
        i0 = int(np.searchsorted(B, st)); i1 = int(np.searchsorted(B, en + 1))
        sub = cov[i0:i1] + 1
        if (P, k - 1) in chosen: sub[0] -= 1
        if (P, k + 1) in chosen: sub[-1] -= 1
        if sub.max() <= nscratch:
            cov[i0:i1] = sub; chosen.add((P, k))
    # merge consecutive chosen pairs into runs
    runs = []
    for P, lst in occ.items():
        k = 0; L = len(lst)
        while k < L - 1:
            if (P, k) in chosen:
                k1 = k
                while (P, k1 + 1) in chosen: k1 += 1
                runs.append((P, k, k1 + 1)); k = k1 + 1
            else: k += 1
    return runs, dict(pairs=len(pairs), chosen=len(chosen), runs=len(runs), base_max_busy=base_max, final_max=int(cov.max()))

def colour(occ, per, runs, scratch):
    tails = getattr(busy_periods, 'tails', {})
    pin = {q: v[0] for q, v in tails.items()}
    '''Interval colouring of busy periods + run intervals on the scratch qubits. Prefers each period's original qubit.'''
    scratch = sorted(scratch)
    items = []                                   # (start, end, kind, ref)
    for q, ps in per.items():
        for S, Z in ps: items.append((S, Z, 0, (q, S, Z)))
    for ri, (P, k0, k1) in enumerate(runs):
        lst = occ[P]; items.append((lst[k0][0], lst[k1][0], 1, ri))
    items.sort(key=lambda x: (x[0], x[2]))
    nxt = {q: sorted(S for S, Z in per.get(q, [])) for q in scratch}
    import heapq
    free = set(scratch); active = []             # heap (end, qubit)
    pc = {}; rh = {}
    tailset = {(q, v[0], v[1]) for q, v in tails.items()}
    for S, E, kind, ref in items:
        while active and active[0][0] < S:
            e, q = heapq.heappop(active); free.add(q)
        if kind == 0:
            q = ref[0]
            if ref in tailset: q = ref[0]; assert q in free, 'pinned tail conflict'
            elif q not in free or (q in pin and E >= pin[q]):
                cs = [c for c in free if not (c in pin and E >= pin[c])]
                q = max(cs, key=lambda c: (bisect.bisect_left(nxt[c], S) >= len(nxt[c]) and 1 << 60 or nxt[c][bisect.bisect_left(nxt[c], S)], c))
            pc[ref] = q
        else:
            cs = [c for c in free if not (c in pin and E >= pin[c])]
            q = max(cs, key=lambda c: (bisect.bisect_left(nxt[c], S) >= len(nxt[c]) and 1 << 60 or nxt[c][bisect.bisect_left(nxt[c], S)], c))
            rh[ref] = q
        free.discard(q); heapq.heappush(active, (E, q))
    return pc, rh

def rewrite(src, dst, occ, per, runs, pc, rh, first_new_bit):
    '''Stream src to dst: rename busy periods per pc, replace occurrences of retained runs.'''
    import collections
    act = {}                                     # qubit -> new qubit (active renames)
    start_ev = collections.defaultdict(list); end_ev = collections.defaultdict(list)
    for (q, S, Z), q2 in pc.items():
        if q2 != q: start_ev[S].append((q, q2)); end_ev[Z + 1].append(q)
    tmpl = {}; nb = first_new_bit
    for ri, (P, k0, k1) in enumerate(runs):
        lst = occ[P]; s = rh[ri]
        for k in range(k0, k1 + 1):
            L, a, b, t = lst[k]
            tmpl[L] = (ri, k - k0, k1 - k0, nb if k == k1 else None)
        nb += 1
    nlines = 0
    with open(src) as f, open(dst, 'w') as g:
        for i, line in enumerate(f):
            if i in end_ev:
                for q in end_ev[i]: del act[q]
            if i in start_ev:
                for q, q2 in start_ev[i]: act[q] = q2
            if act or i in tmpl:
                p = line.split()
                if act and p:
                    for j in range(1, len(p)):
                        v = act.get(p[j])
                        if v is not None: p[j] = v
                if i in tmpl:
                    ri, pos, last, bit = tmpl[i]; s = rh[ri]
                    a, b, t = p[1], p[2], p[3]
                    out = []
                    if pos == 0: out.append(f"CCX {a} {b} {s}\n")
                    out.append(f"CX {s} {t}\n")
                    if pos == last: out += [f"HMR {s} b{bit}\n", f"CZ {a} {b} if b{bit}\n"]
                    g.writelines(out)
                else:
                    g.write(' '.join(p) + '\n' if (act and p) else line)
            else: g.write(line)
            nlines += 1
    return nlines, nb - first_new_bit

def build(base_kmb: str | pathlib.Path, out_kmb: str | pathlib.Path) -> str:
    """Rebuild Asterios's 5778cdd5 retained-product circuit from 4c81b726."""
    base_kmb = pathlib.Path(base_kmb)
    out_kmb = pathlib.Path(out_kmb)
    base_kmx = out_kmb.with_suffix('.base.kmx')
    ret_kmx = out_kmb.with_suffix('.ret.kmx')
    km.Circuit.from_file(base_kmb, format='kmb').to_file(base_kmx, format='kmx')
    regq = read_registers(base_kmx)
    occ, idle, n, maxbit = scan(base_kmx, regq, 892)
    per = busy_periods(idle, n)
    runs, stats = plan(occ, per, 52, maxbit + 1, order='end')
    print('plan', stats, 'maxbit', maxbit, 'runs', len(runs), flush=True)
    pc, rh = colour(occ, per, runs, [f'q{i}' for i in range(840, 892)])
    lines, newbits = rewrite(base_kmx, ret_kmx, occ, per, runs, pc, rh, maxbit + 1)
    km.Circuit.from_file(ret_kmx, format='kmx').to_file(out_kmb, format='kmb')
    digest = hashlib.sha256(pathlib.Path(out_kmb).read_bytes()).hexdigest()
    print('hash', digest, 'lines', lines, 'newbits', newbits, flush=True)
    base_kmx.unlink(missing_ok=True)
    ret_kmx.unlink(missing_ok=True)
    return digest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_kmb', type=pathlib.Path)
    parser.add_argument('out_kmb', type=pathlib.Path)
    args = parser.parse_args()
    digest = build(args.base_kmb, args.out_kmb)
    raise SystemExit(0 if digest == '5778cdd5d710567b970544b8929547cf3be37fe84f2a11643d49edc74eca96cc' else 2)

