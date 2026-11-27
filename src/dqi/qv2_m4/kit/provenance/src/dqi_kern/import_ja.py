# SPDX-License-Identifier: Apache-2.0
# Import of lane dqi890's exported public joint kernels (derived from the compiled DQI decoder of Syed Asad Ali,
# Apache-2.0; original builder Syed Asad Ali) into kernels.json (lane kernel_flip, own code).
"""python3 import_ja.py EXPORT.json [S]
Expects the kernel_JB_173.json export layout (U, V, W, F_free_linear, T0_wire_to_m, T_e_basis, Z_free_e, node_t):
as wired, out = W (U h AND V n_wire) + F n_wire with h = (c0, c1), a = c0 + t c1, b = c1, m = T0 n_wire,
first output = X m, second output = T^-1 (e_wire + Z n_wire). The terms are moved to the standard basis and
verified (all basis pairs + 10,000 random) against J_A[s]; S from the argument, the export's 's' field, or found
by trying every s in F. Only a verified kernel is written into kernels.json['JA'][s]."""
import json, random, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import kernels as Kn

par = Kn.par


def mask(bits): return sum(b << i for i, b in enumerate(bits))


def inv_rows(M):
    n = len(M); A = [mask(r) | (1 << (n + i)) for i, r in enumerate(M)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i] >> c & 1); A[c], A[p] = A[p], A[c]
        for i in range(n):
            if i != c and A[i] >> c & 1: A[i] ^= A[c]
    return [[(A[i] >> (n + j)) & 1 for j in range(n)] for i in range(n)]


def mat(M, x): return sum(par(mask(r) & x) << i for i, r in enumerate(M))


def standard_terms(d):
    U, V, W = d['U'], d['V'], d['W']; r = len(U); nout = len(W)
    wired = [(mask(U[t]), mask(V[t]), sum(W[o][t] << o for o in range(nout))) for t in range(r)]
    if 'P_e' in d:   # kernel_JA_s*.json layout: m = M0 n_wire, n'_true = T0B n'_wire, e_true = P_e e_wire + P_n' n'_wire
        al = d['alpha'][0]; assert d['alpha'][1] == 1
        M0inv = inv_rows(d['M0_nwire_to_m']); T0B = d['T0B_nprime_wire_to_true']
        hX = lambda X: ((X & 4095) ^ Kn.fmul(al, X >> 12)) | ((X >> 12) << 12)
        return [(Kn.compose_left(u, hX), Kn.compose_left(v, lambda m: mat(M0inv, m)),
                 mat(T0B, w & 0xFFFFFF) | ((mat(d['P_e'], w >> 24) ^ mat(d['P_nprime'], w & 0xFFFFFF)) << 24))
                for u, v, w in wired]
    if 'T0B' in d:   # kernel_JA_186.json layout: m = M0 n_wire, T0B n_out = (c0 + c1 alpha) m, P (e + Z n) = Y m
        al = d['alpha'][0]; assert d['alpha'][1] == 1
        M0inv = inv_rows(d['M0'])
        hX = lambda X: ((X & 4095) ^ Kn.fmul(al, X >> 12)) | ((X >> 12) << 12)
        return [(Kn.compose_left(u, hX), Kn.compose_left(v, lambda m: mat(M0inv, m)),
                 mat(d['T0B'], w & 0xFFFFFF) | (mat(d['P'], w >> 24) << 24)) for u, v, w in wired]
    t = d['node_t']; T0inv = inv_rows(d['T0_wire_to_m']); Tinv = inv_rows(d['T_e_basis'])
    hX = lambda X: ((X & 4095) ^ Kn.fmul(t, X >> 12)) | ((X >> 12) << 12)
    return [(Kn.compose_left(u, hX), Kn.compose_left(v, lambda m: mat(T0inv, m)),
             (w & 0xFFFFFF) | (mat(Tinv, w >> 24) << 24)) for u, v, w in wired]


if __name__ == '__main__':
    d = json.load(open(sys.argv[1]))
    terms = standard_terms(d)
    cand = [int(sys.argv[2])] if len(sys.argv) > 2 else ([d['s']] if 's' in d else list(range(4096)))
    rng = random.Random(5); pts = [(rng.getrandbits(24), rng.getrandbits(24)) for _ in range(12)]
    hit = [s for s in cand if all(Kn.evaluate(terms, X, n) == Kn.map_ja(s)(X, n) for X, n in pts)]
    print('rank', len(terms), 's candidates passing 12 random points:', hit[:10])
    if not hit: sys.exit('no s verifies: export layout differs from the J_B one; not imported')
    s = hit[0]; res = Kn.verify(terms, Kn.map_ja(s)); print('s', s, res)
    if not res['ok']: sys.exit('verification failed; not imported')
    K = Kn.load(); K['JA'][str(s)] = {'map': f'J_A[s={s}]', 'source': sys.argv[1], 'terms': [list(x) for x in terms],
                                      'verification': res}
    tmp = Kn.HERE / 'kernels.json.tmp'; tmp.write_text(json.dumps(K)); tmp.replace(Kn.HERE / 'kernels.json')
    print('written JA', s)
