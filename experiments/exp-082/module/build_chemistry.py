from __future__ import annotations

import base64
import hashlib
import io
import json
import lzma
from pathlib import Path
import zipfile
import zlib

import numpy as np


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_chemistry(base_table: str | Path, work_dir: str | Path, submission_dir: str | Path, kickmix_module):
    """Build V22 chemistry loaders from packed source descriptions."""
    BASE = str(base_table)
    WORK = str(work_dir)
    SUB = str(submission_dir)
    km = kickmix_module
    shab = sha256
    payload = Path(__file__).resolve().parent / "payload"
    OURS = {
        "sha_W_H2I": "5b63a8f6d0be88249a8b0bdd2d56bc42e9c456e3936dfa35e5e066fb0886d2c1",
        "shape_W": [9, 127, 46],
        "shape_H2_I": [9, 46],
        "data": (payload / "chemistry_weights.b85").read_text(encoding="ascii").strip(),
    }
    raw = lzma.decompress(base64.b85decode(OURS["data"]))
    if shab(raw) != OURS["sha_W_H2I"]:
        raise ValueError("Embedded chemistry weights failed their SHA-256 check")
    nW = int(np.prod(OURS["shape_W"])) * 8
    with np.load(BASE, allow_pickle=False) as src:
        arrays = {k: src[k] for k in ("U", "W", "H2_I", "H1_I", "Hsym_lower", "tree_edges", "angle_words")}
        source_weights = src["W"].copy()
    arrays["W"] = np.frombuffer(raw[:nW], dtype="<f8").reshape(OURS["shape_W"]).copy()
    arrays["H2_I"] = np.frombuffer(raw[nW:], dtype="<f8").reshape(OURS["shape_H2_I"]).copy()
    dW = arrays["W"] - source_weights
    print(f"refitted weights: {int((dW != 0).sum()):,} changed; zeros {int((source_weights == 0).sum()):,} -> {int((arrays['W'] == 0).sum()):,}")

    def npz_bytes(values):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as archive:
            for key, value in values.items():
                member = io.BytesIO()
                np.lib.format.write_array(member, np.asarray(value), allow_pickle=False)
                archive.writestr(zipfile.ZipInfo(key + ".npy", date_time=(1980, 1, 1, 0, 0, 0)), member.getvalue())
        return buf

    # --- Our chemistry loaders: decoded from a compact description, emitted as circuits, simulated, compared ---
    # A loader for batch k XORs D(a) = words_k(a) xor words_{k-1}(a) (35 bits) into the word registers, for 1,219 addresses a.
    # Address = bank (bits 4-10, 77 banks) and low part (bits 0-3).  Each loader is
    #   * 99 linear "features": 1, the 11 address bits, 5 products of low bits that the incoming words already contain
    #     (bit 5 xor bit 6 of every slot), and 82 cached ANDs (68 bank, 6 low, 8 mixed), one per ancilla qubit;
    #   * word products: (u . features)(v . features) xored into the outputs of a mask, one Toffoli each;
    #   * a linear rest.
    # Only which features are combined is stored below (about 5 KB per loader).  The circuit follows maoxin123's layout: cache
    # the features, add the products, remove the features with measurements (HMR + CZ), so 128 qubits as before.
    # The group-start loaders (batches 5, 7, 11) need 143 bank features, more than the ancillas can hold.  They slide through them:
    # a feature is computed when a product needs it and measured away when nothing later needs it (stored as a program of steps).
    NV, OUTS = 1219, [o for o in range(35) if o % 7 != 6]
    ADDR = np.arange(NV); BANK, LOW = ADDR >> 4, ADDR & 15
    LOW_ANDS = [((2,), 3), ((0, 1), 2), ((0, 1), 3), ((0, 2), 3), ((1, 2), 3), ((0, 1, 2), 3)]
    QUADS = [(0, 1), (0, 2), (1, 2), (0, 3), (1, 3)]
    fun = lambda f: int.from_bytes(np.packbits(np.asarray(f, bool), bitorder='little').tobytes(), 'little')

    class Lin:                                            # write a function of the address as an XOR of tracked qubits
        def __init__(self): self.b = {}; self.add(fun(np.ones(NV, bool)), frozenset(['1']))
        def red(self, v, c):
            while v:
                t = v.bit_length() - 1
                if t not in self.b: return v, c
                pv, pc = self.b[t]; v ^= pv; c = c ^ pc
            return 0, c
        def add(self, v, c):
            v, c = self.red(v, c)
            if v: self.b[v.bit_length() - 1] = (v, c)
        def expr(self, v):
            r, c = self.red(v, frozenset()); assert r == 0
            return c - {'1'}, '1' in c

    def controls(su, cu, sv, cv):                         # CNOTs that put u and v on two qubits
        for qa in sorted(su):
            inA = qa in sv; s2 = (sv ^ su) if inA else sv; cand = [q for q in s2 if q != qa]
            if cand: break
        qb = min(cand); pre = [('CX', q, qa) for q in sorted(su) if q != qa] + ([('X', qa)] if cu else [])
        pre += [('CX', q, qb) for q in sorted(s2) if q not in (qb, qa)] + ([('CX', qa, qb)] if inA else [])
        return pre + ([('X', qb)] if cv ^ (cu if inA else False) else []), qa, qb

    def build_loader(P, sel, wq, anc0=46):
        inv = lambda s: s[::-1]; swap = P['early'] > 0; nb, nmix = (66, 9) if swap else (68, 8); ops, names, recs, L = [], ['1'], [], Lin(); free = iter(range(anc0, 128))
        def track(q, f): names.append(q); L.add(f, frozenset([q]))
        for i, q in enumerate(sel): track(q, fun((ADDR >> i) & 1))
        for j, (x, y) in enumerate(QUADS):
            ops.append(('CX', wq[7 * j + 5], wq[7 * j + 6])); track(wq[7 * j + 6], fun((LOW >> x) & 1 & (LOW >> y)))
        def compute(u, v, q=None):
            pre, qa, qb = controls(*L.expr(u), *L.expr(v)); q = next(free) if q is None else q
            ops.extend(pre + [('CCX', qa, qb, q)] + inv(pre)); return q, pre, qa, qb
        def uncompute(q, pre, qa, qb): ops.extend(pre + [('HMR', q), ('CZ', qa, qb)] + inv(pre))
        def cache(u, v): recs.append(compute(u, v)); track(recs[-1][0], u & v)
        gens = [sum(((x >> i) & 1) << x for x in range(77)) for i in range(7)]
        up = lambda b: fun(np.array([(b >> i) & 1 for i in range(77)], bool)[BANK])
        def pair(row):
            u = v = 0
            for i in row[:3]: u ^= gens[i] if i < 255 else 0
            for i in row[3:]: v ^= gens[i] if i < 255 else 0
            return u, v
        for row in P['ands'][:nb]:
            u, v = pair(row); gens.append(u & v); cache(up(u), up(v))
        if swap:                                          # e1 and e3 share one ancilla: e1 first, e3 after the early products
            (u1, v1), (u3, v3) = pair(P['ands'][66]), pair(P['ands'][67]); e1 = compute(up(u1), up(v1)); names += [e1[0], e1[0]]; i1, i3 = len(names) - 2, len(names) - 1
        lb = [fun((LOW >> i) & 1) for i in range(4)]
        for s, t in LOW_ANDS:
            u = fun(np.ones(NV, bool))
            for x in s: u &= lb[x]
            cache(u, lb[t])
        for g in range(nmix): recs.append(compute(fun(LOW == P['cols'][0 if g < nmix - 4 else 1]), fun(P['B'][g][BANK]))); names.append(recs[-1][0])
        sup = lambda bits, skip=(): (frozenset(names[i] for i in np.nonzero(bits)[0] if i and i not in skip), bool(bits[0]))
        def product(u, v, m):
            pre, qa, qb = controls(*sup(u), *sup(v)); tg = [wq[OUTS[i]] for i in np.nonzero(m)[0]]; fan = [('CX', tg[0], q) for q in tg[1:]]
            ops.extend(pre + fan + [('CCX', qa, qb, tg[0])] + inv(fan) + inv(pre))
        prods = list(zip(P['U'], P['V'], P['M']))
        for p in prods[:P['early']]: product(*p)
        if swap:
            assert not any(p[0][i3] or p[1][i3] for p in prods[:P['early']]) and not any(p[0][i1] or p[1][i1] for p in prods[P['early']:])
            ops.extend([('CX', e1[0], wq[o]) for i, o in enumerate(OUTS) if P['R'][i][i1]]); uncompute(*e1); e3 = compute(up(u3), up(v3), e1[0])
        for p in prods[P['early']:]: product(*p)
        for i, o in enumerate(OUTS):
            s, c = sup(P['R'][i], (i1,) if swap else ()); ops += [('CX', q, wq[o]) for q in sorted(s)] + ([('X', wq[o])] if c else [])
        for n, r in enumerate(reversed(recs)):
            if swap and n == nmix + 6: uncompute(*e3)
            uncompute(*r)
        ops += [('CX', wq[7 * j + 5], wq[7 * j + 6]) for j in reversed(range(5))]
        out = []
        for t in ops:
            if out and out[-1] == t and t[0] in ('CX', 'X'): out.pop()
            else: out.append(t)
        return out

    def read_loader(path):                                # header lines, operations and registers of a loader file
        c = km.Circuit.from_file(path, 'kmb'); b = io.BytesIO(); c.to_file(b, format='kmx'); hdr, regs, items, ops = [], {}, {}, []
        for line in b.getvalue().decode().splitlines():
            t = line.split()
            if not t: continue
            if t[0] == 'REGISTER': regs[t[1]] = t[2].strip('"'); hdr.append(line)
            elif t[0] == 'APPEND_TO_REGISTER': items.setdefault(t[2], []).append(int(t[1][1:])); hdr.append(line)
            else: ops.append((t[0],) + tuple(int(x[1:]) for x in t[1:] if x[0] == 'q'))
        by = {regs[r]: items[r] for r in regs}
        return hdr, ops, by['selection'], [q for j in range(5) for q in by[f'word_{j}']]

    def run_loader(ops, sel, wq, zin):                    # values of the word bits after the loader, for all 1,219 addresses
        S = np.zeros((1 + max(max(t[1:]) for t in ops), NV), bool); S[wq] = zin
        for i, q in enumerate(sel): S[q] = (ADDR >> i) & 1
        for t in ops:
            if t[0] == 'CX': S[t[2]] ^= S[t[1]]
            elif t[0] == 'X': S[t[1]] ^= True
            elif t[0] == 'CCX': S[t[3]] ^= S[t[1]] & S[t[2]]
            elif t[0] == 'HMR': S[t[1]] = False           # measured ancilla; the CZ after it repairs the phase
            else: assert t[0] in ('CZ', 'Z'), t
        return S[wq].copy()

    def word_bits(W, k): return np.zeros((35, NV), bool) if k < 0 else np.stack([((W[:, 5 * k + j] >> i) & 1).astype(bool) for j in range(5) for i in range(7)])

    def build_window(b, wq):                              # a sliding-window loader: A = compute a feature, W = add a word product, D = release a feature
        inv = lambda s: s[::-1]; bits = lambda x: (lambda v: (frozenset(np.nonzero(v[:128])[0].tolist()), bool(v[128])))(np.unpackbits(np.frombuffer(x, np.uint8), bitorder='little'))
        outq = [wq[7 * j + i] for j in range(5) for i in range(6)]; ops = [('CX', wq[7 * j + 5], wq[7 * j + 6]) for j in range(5)]; i, first = 0, None
        while b[i] != 3:
            if b[i] < 2:
                p = i + (2 if b[i] == 0 else 5); pre, qa, qb = controls(*bits(b[p:p + 17]), *bits(b[p + 17:p + 34]))
                if b[i] == 0: ops += pre + [('CCX', qa, qb, b[i + 1])] + inv(pre); first = first or (b[i + 1], qa, qb)
                else:
                    m = int.from_bytes(b[i + 1:i + 5], 'little'); tg = [outq[j] for j in range(30) if m >> j & 1]; fan = [('CX', tg[0], q) for q in tg[1:]]; ops += pre + fan + [('CCX', qa, qb, tg[0])] + inv(fan) + inv(pre)
                i = p + 34
            else:
                q, m, n = b[i + 1], int.from_bytes(b[i + 2:i + 6], 'little'), int.from_bytes(b[i + 40:i + 42], 'little')
                ops += [('CX', q, r) for r in sorted(bits(b[i + 6:i + 23])[0])] + [('CX', q, outq[j]) for j in range(30) if m >> j & 1] + [('HMR', q)]
                ops += [('CZ', b[i + 42 + 2 * j], b[i + 43 + 2 * j]) for j in range(n)] + [('Z', r) for r in sorted(bits(b[i + 23:i + 40])[0])]; i += 42 + 2 * n
        for j in range(30):
            s, c = bits(b[i + 1 + 17 * j:i + 18 + 17 * j]); ops += [('CX', q, outq[j]) for q in sorted(s)] + ([('X', outq[j])] if c else [])
        ops += [('HMR', first[0]), ('CZ',) + first[1:]] + [('CX', wq[7 * j + 5], wq[7 * j + 6]) for j in reversed(range(5))]; out = []
        for t in ops:
            if out and out[-1] == t and t[0] in ('CX', 'X'): out.pop()
            else: out.append(t)
        return out

    PACK = (Path(__file__).resolve().parent / "payload" / "v22_loader_programs.b85").read_text(encoding="ascii").strip()
    blob = base64.b85decode(PACK.replace('\n', '')); assert shab(blob) == '48b38a9696df977e8de79787d860084483ab696340769ff2c794879eeb802d86', 'embedded loaders corrupted'
    KS, BS, pos, LOADER = [[2, 131, 0, 5, 13], [3, 130, 0, 7, 3], [4, 131, 0, 3, 7], [6, 131, 0, 4, 11], [8, 123, 0, 11, 4], [9, 130, 0, 13, 7], [10, 130, 0, 7, 6], [12, 127, 0, 6, 8], [13, 124, 0, 11, 3], [14, 124, 0, 6, 9]], [[1, 20881], [5, 20896], [7, 20978], [11, 20826]], 0, {}
    def take(shape):
        nonlocal pos
        n = int(np.prod(shape)); a = np.frombuffer(blob[pos:pos + n], np.uint8).reshape(shape); pos += n; return a
    for k, nP, early, c1, c2 in KS:                       # early > 0: one bank feature is replaced after that many products (100 features)
        nf, nm = (100, 9) if early else (99, 8)
        LOADER[k] = dict(early=early, cols=(c1, c2), ands=take((68, 6)), B=np.unpackbits(take((nm, 10)), axis=1)[:, :77], U=np.unpackbits(take((nP, 13)), axis=1)[:, :nf], V=np.unpackbits(take((nP, 13)), axis=1)[:, :nf],
                         M=np.unpackbits(take((nP, 4)), axis=1)[:, :30], R=np.unpackbits(take((30, 13)), axis=1)[:, :nf])
    for k, n in BS: LOADER[k] = zlib.decompress(bytes(take((n,))))
    assert pos == len(blob)
    W_OLD = arrays['angle_words']; W_NEW = W_OLD.copy(); FMT = {'CX': 'CX q%d q%d', 'X': 'X q%d', 'CCX': 'CCX q%d q%d q%d', 'HMR': 'HMR q%d b0', 'CZ': 'CZ q%d q%d if b0', 'Z': 'Z q%d if b0'}
    # amplitude of the rotated orbital before every rotation: a word is dead where it is zero
    AMP = np.zeros((NV, 75)); vec = np.zeros((NV, 76)); vec[:, 0] = 1.0
    for r, (p, c) in enumerate(arrays['tree_edges']):
        AMP[:, r] = np.abs(vec[:, p]); th = np.pi * W_OLD[:, r] / 64; pv, cv = vec[:, p].copy(), vec[:, c].copy(); vec[:, p] = np.cos(th) * pv - np.sin(th) * cv; vec[:, c] = np.sin(th) * pv + np.cos(th) * cv
    TOF_PUB, TOF = [], []
    print(f'{"batch":>6s}{"public":>8s}{"ours":>6s}{"qubits":>8s}   forward / back on all 1,219 addresses     dead words used')
    for k in range(15):
        hdr, pub_ops, sel, wq = read_loader(f'{WORK}/public_loaders/angle_k_{k}.kmb'); path = f'{SUB}/dfthcsos/angle_k_{k}.kmb'; TOF_PUB.append(sum(t[0] in ('CCX', 'CCZ') for t in pub_ops)); ours = k in LOADER
        # Source-built base circuits provide register metadata; batch 0 stays source-built and other loaders are rebuilt below.
        if ours:
            ops = build_window(LOADER[k], wq) if isinstance(LOADER[k], bytes) else build_loader(LOADER[k], sel, wq)
            km.Circuit.from_file(io.BytesIO(('\n'.join(hdr + [FMT[t[0]] % t[1:] for t in ops]) + '\n').encode()), format='kmx').to_file(path, format='kmb')
        _, ops2, _, _ = read_loader(path); zin = word_bits(W_NEW, k - 1); zout = run_loader(ops2, sel, wq, zin); TOF.append(sum(t[0] in ('CCX', 'CCZ') for t in ops2))
        assert np.array_equal(run_loader(ops2, sel, wq, zout), zin)
        for j in range(5): W_NEW[:, 5 * k + j] = sum(zout[7 * j + i].astype(W_OLD.dtype) << i for i in range(7))
        ch = W_NEW[:, 5 * k:5 * k + 5] != W_OLD[:, 5 * k:5 * k + 5]; assert not ch.any() or AMP[:, 5 * k:5 * k + 5][ch].max() < 1e-9
        print(f'{k:6d}{TOF_PUB[k]:8d}{TOF[k]:6d}{1 + max(max(t[1:]) for t in ops2):8d}   {"ours" if ours else "public"}: loads its batch and undoes itself   {int(ch.sum()):10d}')
    if sum(TOF) != 3324:
        raise RuntimeError(f"Source-built V22 loader gate failed: expected 3324 Toffolis/pass, got {sum(TOF)}")
    print(f'one pass: {sum(TOF_PUB):,} -> {sum(TOF):,} Toffolis;  T = 2 x {sum(TOF):,} + 6,500 = {2 * sum(TOF) + 6500:,}')
    arrays['angle_words'] = W_NEW; buf = npz_bytes(arrays); open(f'{SUB}/dfthcsos/submission.npz', 'wb').write(buf.getvalue()); ch = W_NEW != W_OLD
    print(f'{int(ch.sum()):,} of {int((AMP < 1e-9).sum()):,} dead words are new; they only occur where the amplitude is zero (largest {AMP[ch].max():.1e}), so lambda_eff does not change.')
    chemistry_npz = Path(SUB) / "dfthcsos" / "submission.npz"
    weights_path = payload / "chemistry_weights.b85"
    loader_path = payload / "v22_loader_programs.b85"
    return {
        "upstream_notebook": "goodpjw2008/qcc-shorter-chemistry-loaders-lb-33-25737",
        "upstream_notebook_sha256": "ee75f7d419f3f687edf2fc1f1e6899e8a1eca94694b695c8c122e85aec29da7a",
        "source_weight_hash": OURS["sha_W_H2I"],
        "source_weight_payload_sha256": hashlib.sha256(weights_path.read_bytes()).hexdigest(),
        "source_loader_payload_sha256": hashlib.sha256(loader_path.read_bytes()).hexdigest(),
        "loader_toffoli_per_pass": int(sum(TOF)),
        "loader_toffoli_by_batch": [int(value) for value in TOF],
        "source_base_toffoli_by_batch": [int(value) for value in TOF_PUB],
        "chemistry_table_sha256": sha256(chemistry_npz.read_bytes()),
        "dead_word_changes": int((W_NEW != W_OLD).sum()),
        "angle_qubit_cap": int(max(max(operation[1:]) for operation in ops2) + 1),
    }
