# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_math: plain word-level model of the public DQI decoder (Syed Asad Ali v12, Apache-2.0) in mathematical
form. Written from reading the source; imports nothing from it. GF(2^12) = F_2[x]/(0x1053), primitive element 2
(official km.GF2Field(12)). K = GF(2^12)[theta]/(theta^2+theta+2048).

Stages modelled (formulas of runs/20261113T223736Z-dqi-math/DQI_PUBLIC_ALGORITHM.md):
  syndromes S_1..S_70 -> node values Y_i = G(alpha_i), G = sum_r S_r (U div x^r)
  extractor: three public charts, projective Thiele chain with carry, rolling tail (zero pivot -> swap, head 0)
  gauge + scalar seed, synthesis (N,D) <- (D, q_i N + P_i D)
  conversion: z = Bez(D,D')^{-1} N via sqrt basis, odd border, Euclid on (b, a - q b) with two right-hand sides
  finish: K = M*R mod D, R = H(D) z (= N/D' mod D)
Usage: python3 -B model.py SHOTS SEED [J_MIN] [WEIGHTS e.g. 35,31]
"""
import random
import sys

MOD, DELTA = 0x1053, 2048
EXP = [0] * 8190
LOG = [-1] * 4096
_x = 1
for _i in range(4095):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 4096:
        _x ^= MOD
EXP[4095:] = EXP[:4095]


def mul(a, b):
    return EXP[LOG[a] + LOG[b]] if a and b else 0


def inv(a):
    assert a, 'inverse of zero'
    return EXP[(4095 - LOG[a]) % 4095]


def div(a, b):
    return mul(a, inv(b))


def sqrt(a):
    return EXP[(2048 * LOG[a]) % 4095] if a else 0


def trace(a):
    v = 0
    for _ in range(12):
        v ^= a
        a = mul(a, a)
    return v


# ---- K = GF(2^12)[theta], elements (lo, hi) = lo + hi*theta ----
def kmul(x, y):
    a0, a1 = x
    b0, b1 = y
    aa, bb = mul(a0, b0), mul(a1, b1)
    return (aa ^ mul(DELTA, bb), mul(a0 ^ a1, b0 ^ b1) ^ aa)


def knorm(x):
    a, b = x
    return mul(a, a) ^ mul(a, b) ^ mul(DELTA, mul(b, b))


def kinv(x):
    n = knorm(x)
    assert n, 'K inverse of zero'
    r = inv(n)
    return (mul(x[0] ^ x[1], r), mul(x[1], r))


def kinv0(x):  # zero-safe inverse used by the third chart: inv(0) = 0
    return (0, 0) if x == (0, 0) else kinv(x)


def kadd(x, y):
    return (x[0] ^ y[0], x[1] ^ y[1])


def kscale(x, c):
    return (mul(x[0], c), mul(x[1], c))


# ---- nodes: t_i = 2i, alpha_i = t_i + theta, q_i = x^2 + x + kappa_i, kappa_i = 2048 + t_i^2 + t_i ----
def t_of(i):
    return 2 * i


def kappa(i):
    t = t_of(i)
    return DELTA ^ mul(t, t) ^ t


def alpha(i):
    return (t_of(i), 1)


def peval(p, x):  # p over GF(2^12), x in GF(2^12)
    v = 0
    for c in reversed(p):
        v = mul(v, x) ^ c
    return v


def pevalK(p, a):  # p over GF(2^12), a in K
    v = (0, 0)
    for c in reversed(p):
        v = kadd(kmul(v, a), (c, 0))
    return v


def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0) for i in range(n)]


def pmul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] ^= mul(x, y)
    return out


def pscale(a, c):
    return [mul(x, c) for x in a]


def pdivmod(a, b):
    a, b = trim(a), trim(b)
    assert b
    q = [0] * max(0, len(a) - len(b) + 1)
    lead = inv(b[-1])
    while len(a) >= len(b):
        s = len(a) - len(b)
        f = mul(a[-1], lead)
        q[s] = f
        for i, x in enumerate(b):
            a[i + s] ^= mul(f, x)
        a = trim(a)
    return q, a


def pmod(a, b):
    return pdivmod(a, b)[1]


def qpoly(i):
    return [kappa(i), 1, 1]


U = [1]
for _i in range(35):
    U = pmul(U, qpoly(_i))
M = [1]
for _i in range(35, 51):
    M = pmul(M, qpoly(_i))
assert len(U) == 71 and len(M) == 33


def padding(j):  # census reference.py PADDING[j]
    p = [0, 1] if j % 2 == 0 else [1]
    for i in range(j, 34 - (j % 2 == 0), 2):
        p = pmul(p, qpoly(i))
    return p


# ---- stage 0: syndromes and node values ----
def syndromes(err):
    return [0] + [_xor(mul(e, EXP[(LOG[X] * r) % 4095]) for X, e in err.items()) for r in range(1, 71)]


def _xor(it):
    v = 0
    for a in it:
        v ^= a
    return v


def node_values(S):
    """Y_i = G(alpha_i), G(z) = sum_{r=1}^{70} S_r (U div z^r) = polynomial part of U(z) S(z)."""
    G = [0] * 70
    for r in range(1, 71):
        for j in range(71 - r):
            G[j] ^= mul(S[r], U[j + r])
    return [pevalK(G, alpha(i)) for i in range(35)], G


# ---- stage 1: extractor ----
def head_coeffs(v, i):  # K value at alpha_i of c0 + c1 z  ->  (c0, c1);  node_view: lo ^= t_i * hi
    return (v[0] ^ mul(t_of(i), v[1]), v[1])


def head_at(c, k):  # (c0, c1) -> value c0 + c1 alpha_k
    return (c[0] ^ mul(t_of(k), c[1]), c[1])


class DomainFailure(Exception):
    pass


def extractor(Y, j_min):
    """Returns heads P_i (coefficient form), final carry (K), tail flags f_i."""
    P = [None] * 35
    # chart 0: P0 = 1/Y0
    if Y[0] == (0, 0):
        raise DomainFailure('chart0: Y0 = 0')
    P[0] = head_coeffs(kinv(Y[0]), 0)
    # chart 1: P1 = q0(alpha1) / (1/Y1 + P0(alpha1)),  q0(alpha1) = kappa0 + kappa1 = 6
    if Y[1] == (0, 0):
        raise DomainFailure('chart1: Y1 = 0')
    w = kadd(kinv(Y[1]), head_at(P[0], 1))
    if w == (0, 0):
        raise DomainFailure('chart1: zero inner value')
    assert kappa(0) ^ kappa(1) == 6
    P[1] = head_coeffs(kinv(kscale(w, inv(6))), 1)
    # chart 2 (zero-safe in Y2): P2 = 18 / (20/(1/Y2 + P0(alpha2)) + P1(alpha2)), Y2 = 0 -> 18/P1(alpha2)
    assert (kappa(0) ^ kappa(2), kappa(1) ^ kappa(2)) == (20, 18)
    w = kinv0(Y[2])
    if Y[2] != (0, 0):
        w = kadd(w, head_at(P[0], 2))
    w = kinv0(w)
    w = kscale(w, 20)
    w = kadd(w, head_at(P[1], 2))
    w = kscale(w, inv(18))
    if w == (0, 0):
        raise DomainFailure('chart2: zero outer value')
    P[2] = head_coeffs(kinv(w), 2)
    # generic projective chain from slot 3, carry c = 1
    c = (1, 0)
    flags = {}
    queries = 0
    for i in range(3, 35):
        n = kmul(c, Y[i]) if i > 3 else Y[i]
        d = c
        for old in range(i):
            # (n, d) <- ((d + P_old(alpha_i) n) / q_old(alpha_i), n),  q_old(alpha_i) = kappa_old + kappa_i (classical)
            n, d = kscale(kadd(d, kmul(head_at(P[old], i), n)), inv(kappa(old) ^ kappa(i))), n
            queries += 1
        if i >= j_min:
            f = n == (0, 0)
            flags[i] = f
            if f:
                n, d = d, n
        u, v = n, d
        if u == (0, 0):
            raise DomainFailure(f'slot {i}: zero pivot u (n = d = 0 or n = 0 below j_min)')
        P[i] = head_coeffs(kmul(v, kinv(u)), i)   # head v/u, stored as linear-polynomial coefficients
        c = u                                       # the unit u becomes the carry
    return P, c, flags, queries


def seed_and_synthesis(P, c, flags):
    # gauge: lambda = nonzero 12-bit half of the carry (lo unless lo = 0)
    lam = c[0] if c[0] else c[1]
    assert lam
    f34 = flags.get(34, False)
    if f34:
        N, D = [0], [mul(lam, P[34][0]), lam]   # P34 = 0 here; seed swap moves lambda into D_x
        assert P[34] == (0, 0)
    else:
        N, D = [lam], [mul(lam, P[34][0]), mul(lam, P[34][1])]
    products = 0
    for i in range(33, -1, -1):
        r = len(N)
        # (N, D) <- (D, q_i N + P_i D); the circuit forms q_i N + P_i D by r+2 pointwise mul12 at beta = 0..r+1
        newD = padd(pmul(qpoly(i), N), pmul(list(P[i]), D))
        newD = newD + [0] * (r + 2 - len(newD))
        assert len(newD) == r + 2
        products += r + 2
        N, D = D, newD
    assert len(N) == 35 and len(D) == 36
    return N, D, products, lam


# ---- stage 3: conversion (preimage) ----
def bezout(a, b):  # even_forney_classical.bezout convention
    n = max(len(a), len(b)) - 1
    aa = list(a) + [0] * (n + 1 - len(a))
    bb = list(b) + [0] * (n + 1 - len(b))
    m = [[0] * n for _ in range(n)]
    for i in range(1, n + 1):
        for j in range(i):
            co = mul(aa[i], bb[j]) ^ mul(aa[j], bb[i])
            for k in range(i - j):
                m[i - 1 - k][j + k] ^= co
    return m


class Euclid:
    def __init__(self):
        self.profile = []       # degrees of the remainder sequence (half-Euclid profile)
        self.inv12 = 0          # 1/beta and 1/(quotient head) inversions (math count, one each per step)
        self.steps = []


def bez_solve(A, B, rhss, n, ev):
    """Solve Bez_n(A,B) x = rhs for every rhs (n x n, deg A = n exactly).
    Step: A = Q B + C, k = n - deg B; W = [e_0..e_{dB-1} | B, xB, .., x^{k-1}B];
    Bez(A,B) = W diag(Bez_{dB}(B,C), H_Q) W^T, H_Q[i][j] = Q_{i+j+1}."""
    A, B = trim(A), trim(B)
    assert len(A) == n + 1
    if n == 0:
        return [[] for _ in rhss]
    if not B:
        raise DomainFailure('gcd nonconstant')
    dB = len(B) - 1
    k = n - dB
    ev.profile.append(dB)
    ev.steps.append(k)
    beta = B[-1]
    rb = inv(beta)
    ev.inv12 += 1
    Q, C = pdivmod(A, B)
    assert len(Q) == k + 1
    out = []
    lows, highs = [], []
    for y in rhss:
        y = list(y)
        # w = W^{-1} y: back-substitute the k high columns (triangular, diagonal beta), top row first
        wh = [0] * k
        for r in reversed(range(k)):
            val = y[dB + r]
            wh[r] = mul(val, rb)
            for p in range(dB + 1):   # subtract column x^r B from y
                y[r + p] ^= mul(B[p], wh[r])
        lows.append(y[:dB])
        highs.append(wh)
    # H_Q^{-1}: Hankel with Q_k on the anti-diagonal (k = 1: divide by q1; k = 2: [[q1,q2],[q2,0]])
    rq = inv(Q[k])
    ev.inv12 += 1
    sol_hi = []
    for wh in highs:
        # H x = wh, H[i][j] = Q_{i+j+1} (anti-triangular): x_j = (wh_{k-1-j} + sum_{jj<j} Q_{k-j+jj} x_jj) / Q_k
        x = [0] * k
        for j in range(k):
            acc = wh[k - 1 - j]
            for jj in range(j):
                acc ^= mul(Q[k - j + jj], x[jj])
            x[j] = mul(acc, rq)
        sol_hi.append(x)
    sol_lo = bez_solve(B, C, lows, dB, ev) if dB else [[] for _ in rhss]
    for xl, xh in zip(sol_lo, sol_hi):
        # x = W^{-T} x': first dB rows identity, high rows: sum_p (x^r B)_p x_p = xh_r
        x = list(xl) + [0] * k
        for r in range(k):
            acc = xh[r]
            for p in range(dB):
                acc ^= mul(B[p], x[r + p])
            x[dB + r] = mul(acc, rb)
        out.append(x)
    return out


def conversion(D, N, ev):
    """z with Bez(D, D') z = N (D: 36 coefficients, N: 35). Public odd-degree (35) branch."""
    sD = [sqrt(x) for x in D]
    sN = [sqrt(x) for x in N]
    A, B = sD[::2], sD[1::2]            # a = sqrt(D_even) (18 words), b = sqrt(D_odd) (18 words)
    s, q = B[-1], A[-1]                  # s = sqrt(D_35) unit, q = sqrt(D_34)
    if not s:
        raise DomainFailure('D35 = 0')
    even, odd, H = sN[::2][:-1], sN[1::2], sN[-1]
    H, qq = div(H, s), div(q, s)         # paired divide of [H, q] by s
    u = [even[k] ^ mul(H, B[k]) for k in range(17)]      # odd border: u = sqrt(N_even) + h b
    v = list(odd)
    red = [A[k] ^ mul(qq, B[k]) for k in range(17)]      # elimination: a' = a - (q/s) b, degree <= 16
    xu, xv = bez_solve(B, red, [u, v], 17, ev)           # Bez(b, a') [x_u | x_v] = [u | v]
    h = H
    for k in range(17):
        h ^= mul(B[k], xv[k])
    h = div(h, s)
    roots = [w for pair in zip(xv, xu) for w in pair] + [h]
    return [mul(w, w) for w in roots]


def horner_R(D, z):
    """R = H(D) z = sum_j z_j (D div x^{j+1}); coefficient i = sum_j D_{i+j+1} z_j."""
    return [_xor(mul(D[i + j + 1], z[j]) for j in range(35 - i)) for i in range(35)]


def finish(D, R):
    return pmod(pmul(M, R), D) + [0] * 35


def half_profile_admitted(D):
    """census reference.half_profile reasons (window starts {17,15} and {14,12}, drop > 2, gcd)."""
    a = trim([sqrt(x) for x in D[1::2]])
    evens = [sqrt(x) for x in D[::2]]
    qt = div(evens[-1], a[-1])
    b = trim([x ^ mul(qt, y) for x, y in zip(evens[:-1], a[:-1])])
    degrees = [len(a) - 1]
    while b:
        degrees.append(len(b) - 1)
        a, b = b, pmod(a, b)
    drops = [x - y for x, y in zip(degrees, degrees[1:])]
    padded = {x for x, y in zip(degrees, degrees[1:]) if x - y == 2}
    reasons = []
    if degrees[-1] != 0:
        reasons.append('gcd')
    if max(drops, default=1) > 2:
        reasons.append('drop>2')
    if {17, 15} <= padded:
        reasons.append('window17')
    if {14, 12} <= padded:
        reasons.append('window14')
    return degrees, reasons


def shot(rng, t, j_min):
    pos = rng.sample(range(4095), t)
    err = {EXP[p]: rng.randrange(1, 4096) for p in pos}
    S = syndromes(err)
    Y, G = node_values(S)
    lam_poly = [1]
    for X in err:
        lam_poly = pmul(lam_poly, [X, 1])
    Omega = []
    for X, e in err.items():
        quo, rem = pdivmod(lam_poly, [X, 1])
        assert not rem
        Omega = padd(Omega, pscale(quo, mul(e, mul(X, peval(U, X)))))
    # node values are Omega/Lambda at alpha_i
    for i in range(35):
        assert kmul(Y[i], pevalK(lam_poly, alpha(i))) == pevalK(Omega, alpha(i))
    res = dict(t=t)
    try:
        P, c, flags, queries = extractor(Y, j_min)
        N, D, products, lam = seed_and_synthesis(P, c, flags)
        res.update(queries=queries, synth_products=products)
        # D = lambda' * Lambda * PAD[t], N = lambda' * Omega * PAD[t]
        full = pmul(lam_poly, padding(t))
        Dt, Nt = trim(D), trim(N)
        scale_ = div(Dt[-1], full[-1])
        res['D_is_Lambda_PAD'] = Dt == trim(pscale(full, scale_))
        res['N_is_Omega_PAD'] = Nt == trim(pscale(pmul(Omega, padding(t)), scale_))
        degrees, reasons = half_profile_admitted(D)
        res['half_reasons'] = reasons
        ev = Euclid()
        z = conversion(D, N, ev)
        res['profile'] = ev.profile
        res['steps'] = ev.steps
        # direct check: Bez(D, D') z = N
        Dp = [D[i + 1] if i % 2 == 0 else 0 for i in range(35)]
        Bm = bezout(D, Dp)
        res['bez_ok'] = all(_xor(mul(Bm[i][j], z[j]) for j in range(35)) == N[i] for i in range(35))
        R = horner_R(D, z)
        res['R_times_Dprime_ok'] = trim(pmod(pmul(R, Dp), D)) == trim(N)
        K = finish(D, R)
        ok_D = ok_R = ok_K = True
        for X, e in err.items():
            ok_D &= peval(D, X) == 0
            cX = mul(X, peval(U, X))
            ok_R &= peval(R, X) == mul(cX, e)
            ok_K &= peval(K, X) == mul(peval(M, X), mul(cX, e))
        # no other position a in GF(2^12)* is a root of D
        roots = sum(1 for a in range(1, 4096) if peval(D, a) == 0)
        res.update(D_roots_ok=ok_D, R_ok=ok_R, K_ok=ok_K, D_root_count=roots)
        res['pass'] = ok_D and ok_R and ok_K and res['bez_ok'] and roots == t
    except DomainFailure as exc:
        res['failure'] = str(exc)
        res['pass'] = False
    return res


def main():
    shots = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    j_min = int(sys.argv[3]) if len(sys.argv) > 3 else 18
    rng = random.Random(seed)
    import collections
    weights = [int(w) for w in sys.argv[4].split(',')] if len(sys.argv) > 4 else [35, 31]
    for t in weights:
        summary = collections.Counter()
        for _ in range(shots):
            r = shot(rng, t, j_min)
            summary['pass' if r['pass'] else 'fail'] += 1
            if 'failure' in r:
                summary['domain_failure:' + r['failure']] += 1
            else:
                for key in ('D_is_Lambda_PAD', 'N_is_Omega_PAD', 'bez_ok', 'R_times_Dprime_ok', 'D_roots_ok',
                            'R_ok', 'K_ok'):
                    summary[key + '=' + str(r[key])] += 1
                summary['half_reasons=' + ','.join(r['half_reasons'])] += 1
                summary['queries=%d synth_products=%d' % (r['queries'], r['synth_products'])] += 1
                summary['drop2_steps=%d' % sum(1 for k in r['steps'] if k == 2)] += 1
        print(f't={t} shots={shots} j_min={j_min} seed={seed}')
        for k, v in sorted(summary.items()):
            print(f'   {v:6d}  {k}')


if __name__ == '__main__':
    main()
