"""Inputs and independent checks for flip.c (lane kernel_flip, own code).
Decomposition file: first line r, then r lines "u v w" (ints): f(x, y) = sum_t par(u_t & x) par(v_t & y) w_t.
Kinds (true maps):
  gf:N:MOD     x*y in GF(2)[z]/(MOD), N bits            (f12 = gf:12:0x1053, the DQI field F)
  scal:K       s in F (12 bits) times (n_1..n_K) in F^K, n_c in bits 12c..12c+11 -> (s n_1, .., s n_K)
  kq           K = F[t]/(t^2+t+2048): n = n0 + n1 t, n0 bits 0-11, n1 bits 12-23
Commands:
  python3 kf.py naive N MOD OUT         schoolbook start
  python3 kf.py copies START K OUT      K copies of a 12x12->12 decomposition as a scal:K start
  python3 kf.py verify KIND FILE [JSON] all basis pairs + 10,000 random pairs; JSON gets U, V, W + result
"""
import json, random, sys


def par(x): return bin(x).count('1') & 1


def gfmul(a, b, n, mod):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a >> n: a ^= mod
    return r


F = lambda a, b: gfmul(a, b, 12, 0x1053)


def kind_fn(kind):
    if kind == 'f12': kind = 'gf:12:0x1053'
    if kind.startswith('gf:'):
        _, n, mod = kind.split(':'); n = int(n); mod = int(mod, 0)
        return n, n, (lambda x, y: gfmul(x, y, n, mod))
    if kind.startswith('scal:'):
        k = int(kind.split(':')[1]); m = 4095
        return 12, 12 * k, (lambda s, v: sum(F(s, (v >> 12 * c) & m) << 12 * c for c in range(k)))
    if kind == 'kq':
        m = 4095
        def kmul(a, b):
            a0, a1, b0, b1 = a & m, a >> 12, b & m, b >> 12
            hh = F(a1, b1)  # t^2 = t + 2048
            return (F(a0, b0) ^ F(hh, 2048)) | ((F(a0, b1) ^ F(a1, b0) ^ hh) << 12)
        return 24, 24, kmul
    if kind == 'z':    # (b, m) -> b m | sqrt(b) m << 12, b, m in F
        return 12, 12, (lambda b, m: F(b, m) | (F(f_sqrt(b), m) << 12))
    if kind == 'jb':   # (X, n) -> X n | sqrt(b) n << 24, X = a + b t
        return 24, 24, (lambda X, n: K_mul(X, n) | (sum(F(f_sqrt(X >> 12), (n >> 12 * c) & 4095) << 12 * c for c in range(2)) << 24))
    if kind == 'ja':   # (X, n) -> X n | Y n << 24, Y = sqrt(a) + sqrt(b) t
        return 24, 24, (lambda X, n: K_mul(X, n) | (K_mul(Ysq(X), n) << 24))
    if kind == 'jaz':  # (X, n) -> X n | Y n << 24, Y = sqrt(a) + sqrt(b) zeta, zeta = 2545 + theta
        return 24, 24, (lambda X, n: K_mul(X, n) | (K_mul(Yzeta(X), n) << 24))
    raise SystemExit('unknown kind ' + kind)


def load(path):
    L = open(path).read().split()
    r = int(L[0]); vals = list(map(int, L[1:1 + 3 * r]))
    return [tuple(vals[3 * t:3 * t + 3]) for t in range(r)]


def evaluate(terms, x, y):
    acc = 0
    for u, v, w in terms:
        if par(u & x) and par(v & y): acc ^= w
    return acc


def verify(kind, terms, nrand=10000, seed=12345):
    na, nb, f = kind_fn(kind)
    bad_basis = sum(evaluate(terms, 1 << i, 1 << j) != f(1 << i, 1 << j) for i in range(na) for j in range(nb))
    rng = random.Random(seed); bad_rand = 0
    for _ in range(nrand):
        x, y = rng.getrandbits(na), rng.getrandbits(nb)
        bad_rand += evaluate(terms, x, y) != f(x, y)
    return {'kind': kind, 'rank': len(terms), 'basis_pairs': na * nb, 'basis_fail': bad_basis,
            'random_pairs': nrand, 'random_seed': seed, 'random_fail': bad_rand, 'ok': bad_basis == 0 and bad_rand == 0}


def write(path, terms):
    open(path, 'w').write(f'{len(terms)}\n' + ''.join(f'{u} {v} {w}\n' for u, v, w in terms))


# ---- K basis transport and joint maps (root's J_A / J_B) ----
def f_sqrt(b):
    for _ in range(11): b = F(b, b)
    return b


def K_mul(a, b):
    m = 4095; a0, a1, b0, b1 = a & m, a >> 12, b & m, b >> 12
    hh = F(a1, b1)
    return (F(a0, b0) ^ F(hh, 2048)) | ((F(a0, b1) ^ F(a1, b0) ^ hh) << 12)


def find_root_in_K(mod=0x100001B):
    """vectorised search for alpha in K with mod(alpha) = 0"""
    import numpy as np
    exp = [0] * 8190; log = [0] * 4096; x = 1
    g = next(g for g in range(2, 4096) if all(True for _ in [0]) and _order(g) == 4095)
    for i in range(4095):
        exp[i] = x; log[x] = i; x = F(x, g)
    for i in range(4095, 8190): exp[i] = exp[i - 4095]
    E = np.array(exp, dtype=np.int64); Lg = np.array(log, dtype=np.int64)
    def fm(a, b):
        r = E[Lg[a] + Lg[b]]; return np.where((a == 0) | (b == 0), 0, r)
    def km(a, b):
        a0, a1, b0, b1 = a & 4095, a >> 12, b & 4095, b >> 12
        hh = fm(a1, b1)
        return (fm(a0, b0) ^ fm(hh, np.full_like(hh, 2048))) | ((fm(a0, b1) ^ fm(a1, b0) ^ hh) << 12)
    for start in range(1, 1 << 24, 1 << 21):
        al = np.arange(start, min(start + (1 << 21), 1 << 24), dtype=np.int64)
        pw = [np.ones_like(al), al]
        for k in range(2, 25): pw.append(km(pw[-1], al))
        acc = np.zeros_like(al)
        for k in range(25):
            if (mod >> k) & 1: acc ^= pw[k]
        hit = np.nonzero(acc == 0)[0]
        if len(hit): return int(al[hit[0]])


def _order(g):
    x = g
    for k in range(1, 4095):
        if x == 1: return k
        x = F(x, g)
    return 4095


def transport_g24_to_K(terms, mod=0x100001B):
    """G = GF(2)[z]/(mod) -> K by z -> alpha. Returns the decomposition of K-multiplication."""
    al = find_root_in_K(mod)
    cols = [1]
    for k in range(1, 24): cols.append(K_mul(cols[-1], al))  # phi(z^k)
    phi = lambda w: _apply(cols, w)
    # M = phi^-1 as matrix; u' = M^T u: par(u & M X) = par(u' & X), u'_j = par(u & M e_j) = par(u & phi^-1(e_j))
    inv = _inverse_cols(cols)
    out = []
    for u, v, w in terms:
        u2 = sum(par(u & inv[j]) << j for j in range(24)); v2 = sum(par(v & inv[j]) << j for j in range(24))
        out.append((u2, v2, phi(w)))
    return out, al


def _apply(cols, w):
    r = 0
    for k in range(len(cols)):
        if (w >> k) & 1: r ^= cols[k]
    return r


def _inverse_cols(cols):
    """columns of phi^-1: inv[j] = phi^-1(e_j) as bit vector"""
    n = len(cols)
    A = [[(cols[k] >> i) & 1 for k in range(n)] for i in range(n)]  # A[i][k]: bit i of phi(e_k)
    aug = [sum(A[i][k] << k for k in range(n)) | (1 << (n + i)) for i in range(n)]
    for c in range(n):
        p = next(i for i in range(c, n) if aug[i] >> c & 1); aug[c], aug[p] = aug[p], aug[c]
        for i in range(n):
            if i != c and aug[i] >> c & 1: aug[i] ^= aug[c]
    # row c of inverse: phi^-1 matrix rows; inv matrix B with B[c][i] = bit (n+i) of aug[c]
    return [sum(((aug[c] >> (n + j)) & 1) << c for c in range(n)) for j in range(n)]


def sqrt_T(u, shift):
    """mask u on sqrt(b) (12 bits) -> mask on b at bit offset shift: u'_j = par(u & sqrt(e_j))"""
    return sum(par(u & f_sqrt(1 << j)) << (j + shift) for j in range(12))


def Ysq(X):
    m = 4095
    return f_sqrt(X & m) | (f_sqrt(X >> 12) << 12)


ZETA = 2545 | (1 << 12)   # zeta = 2545 + theta


def Yzeta(X):
    """root's J_A first instance: Y = sqrt(a) + sqrt(b) zeta"""
    return f_sqrt(X & 4095) ^ K_mul(f_sqrt(X >> 12), ZETA)


def build_joint(kq99, f42, outdir):
    k = load(kq99); f = load(f42)
    jb = k + [(sqrt_T(u, 12), v << 12 * c, w << (24 + 12 * c)) for c in range(2) for u, v, w in f]
    yT = lambda u: sum(par(u & Ysq(1 << j)) << j for j in range(24))
    ja = k + [(yT(u), v, w << 24) for u, v, w in k]
    write(outdir + '/jb_183.txt', jb); write(outdir + '/ja_198.txt', ja)
    return verify('jb', jb), verify('ja', ja)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'naive':
        n, mod = int(sys.argv[2]), int(sys.argv[3], 0)
        write(sys.argv[4], [(1 << i, 1 << j, gfmul(1 << i, 1 << j, n, mod)) for i in range(n) for j in range(n)])
    elif c == 'copies':
        t, k = load(sys.argv[2]), int(sys.argv[3])
        write(sys.argv[4], [(u, v << 12 * q, w << 12 * q) for q in range(k) for u, v, w in t])
    elif c == 'verify':
        terms = load(sys.argv[3]); res = verify(sys.argv[2], terms)
        print(json.dumps(res))
        if len(sys.argv) > 4:
            json.dump({'U': [t[0] for t in terms], 'V': [t[1] for t in terms], 'W': [t[2] for t in terms],
                       'source_file': sys.argv[3], 'verification': res}, open(sys.argv[4], 'w'), indent=1)
        sys.exit(0 if res['ok'] else 1)
