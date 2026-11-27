# SPDX-License-Identifier: Apache-2.0
# Joint DQI product kernels (lane kernel_flip). The algorithms (the 173-AND J_B, the 99-AND K product, the J_A
# patterns) come from the public DQI circuit and generator of Syed Asad Ali (Apache-2.0); original builder
# Syed Asad Ali. This file is own code that stores, transforms and checks them.
"""Bilinear kernels as terms (u, v, w): target ^= sum_t par(u_t & head) par(v_t & n) w_t.

Standard basis: F = GF(2)[x]/(x^12+x^6+x^4+x+1), bit i = x^i; K = F[theta]/(theta^2+theta+2048), a 24-bit word is
lo + hi theta (lo bits 0-11, hi bits 12-23). Head X = a + b theta, right operand n in K, target 48 bits = (d, e):
  J_B:     d ^= X n,  e ^= sqrt(b) n                                  (sqrt = inverse Frobenius of F)
  J_A[s]:  d ^= X n,  e ^= sqrt_K((a + kappa b) + b theta) n,  kappa = s^2 + s
           = (sqrt(a) + g sqrt(b) + sqrt(b) theta) n with g = sqrt(kappa) + sqrt(2048) = s + sqrt(s) + sqrt(2048)
  KMUL:    d ^= X n (24-bit target)
  python3 kernels.py build      writes kernels.json (J_B 173, KMUL 99, J_A fallbacks) and verifies every entry
  python3 kernels.py check      re-verifies kernels.json
"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MOD_F = 0x1053


def par(x): return bin(x).count('1') & 1


def fmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> 12: a ^= MOD_F
    return r


def fsqrt(b):
    for _ in range(11): b = fmul(b, b)
    return b


def kmul(x, y):
    a0, a1, b0, b1 = x & 4095, x >> 12, y & 4095, y >> 12
    hh = fmul(a1, b1)                      # theta^2 = theta + 2048
    return (fmul(a0, b0) ^ fmul(hh, 2048)) | ((fmul(a0, b1) ^ fmul(a1, b0) ^ hh) << 12)


def ksqrt(x):
    for _ in range(23): x = kmul(x, x)
    return x


def kappa(s): return fmul(s, s) ^ s


def ja_g(s): return fsqrt(kappa(s)) ^ fsqrt(2048)


def ja_y(s, X):
    """Y(X) = sqrt_K((a + kappa b) + b theta)"""
    a, b = X & 4095, X >> 12
    return ksqrt((a ^ fmul(kappa(s), b)) | (b << 12))


def map_jb(X, n):
    sb = fsqrt(X >> 12)
    return kmul(X, n) | ((fmul(sb, n & 4095) | (fmul(sb, n >> 12) << 12)) << 24)


def map_ja(s):
    return lambda X, n: kmul(X, n) | (kmul(ja_y(s, X), n) << 24)


def map_kmul(X, n): return kmul(X, n)


def evaluate(terms, X, n):
    acc = 0
    for u, v, w in terms:
        if par(u & X) and par(v & n): acc ^= w
    return acc


def verify(terms, fn, nrand=10000, seed=2026):
    bad_basis = sum(evaluate(terms, 1 << i, 1 << j) != fn(1 << i, 1 << j) for i in range(24) for j in range(24))
    rng = random.Random(seed); bad = 0
    for _ in range(nrand):
        X, n = rng.getrandbits(24), rng.getrandbits(24)
        bad += evaluate(terms, X, n) != fn(X, n)
    return {'rank': len(terms), 'basis_pairs': 576, 'basis_fail': bad_basis, 'random_pairs': nrand,
            'random_seed': seed, 'random_fail': bad, 'ok': bad_basis == 0 and bad == 0}


def compose_left(u, lin):
    """mask u' with par(u' & X) = par(u & lin(X)) for a GF(2)-linear lin on 24 bits"""
    return sum(par(u & lin(1 << j)) << j for j in range(24))


def ja_fallback(kmul_terms, s):
    """J_A[s] as two K products (198 ANDs): X n and Y(X) n"""
    y = lambda X: ja_y(s, X)
    return [tuple(t) for t in kmul_terms] + [(compose_left(u, y), v, w << 24) for u, v, w in kmul_terms]


def load(path=HERE / 'kernels.json'):
    d = json.loads(Path(path).read_text())
    return d


def get_ja(d, s):
    """public J_A[s] when present, else the 198-AND fallback built on the fly"""
    key = str(s)
    if key in d.get('JA', {}): return [tuple(t) for t in d['JA'][key]['terms']]
    return ja_fallback(d['KMUL']['terms'], s)


def _read_terms(path):
    L = Path(path).read_text().split(); r = int(L[0]); v = list(map(int, L[1:1 + 3 * r]))
    return [tuple(v[3 * t:3 * t + 3]) for t in range(r)]


def build():
    starts = ROOT / 'runs/20261115T190907Z-kernel-flip/starts'
    jb = _read_terms(starts / 'jb173_abstract.txt')
    k99 = _read_terms(starts / 'kq_99.txt')
    out = {
        'credit': 'Algorithms from the public DQI circuit/generator of Syed Asad Ali (Apache-2.0); original builder Syed Asad Ali.',
        'basis': 'F = GF(2)[x]/(x^12+x^6+x^4+x+1), bit i = x^i; K = F[theta]/(theta^2+theta+2048), word = lo | hi << 12 = lo + hi theta',
        'convention': 'target ^= sum_t par(u & head) par(v & n) w; head = a | b << 12, n = lo | hi << 12, target = d | e << 24',
        'JB': {'map': '(a,b,n) -> ((a+b theta) n, sqrt(b) n)', 'source': 'lane dqi890 export kernel_JB_173.json, '
               'transported to the standard basis by src/kernel_flip/import173.py', 'terms': [list(t) for t in jb]},
        'KMUL': {'map': '(X,n) -> X n', 'source': 'public 99-AND kernel (runs/20261111T232500Z-kernel-rank/flip24/kit99.txt, '
                 'GF(2)[z]/(z^24+z^4+z^3+z+1)) transported to K by z -> 113608 (src/kernel_flip/kf.py)', 'terms': [list(t) for t in k99]},
        'JA': {},
        'JA_note': 'JA[s] holds public patterns when exported; get_ja() falls back to two K products (198 ANDs).',
    }
    out['JB']['verification'] = verify(jb, map_jb)
    out['KMUL']['verification'] = verify(k99, map_kmul)
    assert out['JB']['verification']['ok'] and out['KMUL']['verification']['ok']
    (HERE / 'kernels.json').write_text(json.dumps(out))
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        o = build(); print('JB', o['JB']['verification']); print('KMUL', o['KMUL']['verification'])
        for s in (30, 1, 7):
            print('JA fallback s =', s, verify(get_ja(o, s), map_ja(s), nrand=2000))
    elif sys.argv[1] == 'check':
        d = load()
        print('JB', verify([tuple(t) for t in d['JB']['terms']], map_jb))
        for s, e in d['JA'].items(): print('JA', s, verify([tuple(t) for t in e['terms']], map_ja(int(s))))
