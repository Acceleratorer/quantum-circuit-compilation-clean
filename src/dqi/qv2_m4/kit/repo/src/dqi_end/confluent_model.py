# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_pair: CONFLUENT double-node extractor in the word model (root's hypothesis for the public 890-q decoder,
to be ported into Syed Asad Ali's v12 DQI decoder, Apache-2.0; original builder Syed Asad Ali). Diagnostic.

Nodes: one single quadratic node (index 0) + 17 double nodes (indices 1..17), moduli per slot
  m_0 = q_0, m_{2a-1} = m_{2a} = q_a (a = 1..17).  U = q_0 prod q_a^2 (degree 70).
Data: G = polynomial part of U(z) S(z); single node: Y = G(alpha_0); double node: Y = G(alpha_a), Y' = G'(alpha_a).
Value recursion per new double node beta (state n, d, w = n d_z + d n_z; start n = Y, d = 1, w = Y'):
  one old step (head P = c0 + c1 z, kappa = q(beta) in F):  n+ = (d + P(beta) n)/kappa, d+ = n,
                                                         w+ = (w + c1 n^2)/kappa + n+ n/kappa
  (checked against explicit derivatives n_z, d_z, and against the two-step closed form
   w2 = (w0 + c1_A n0^2)/kappa^2 + P_B(beta + kappa) n1^2/kappa^2).
  own slot 1: [tail: n = 0 -> swap n, d; w is symmetric] P1 = d/n;  N+ = (w + c1_1 n^2)/n, D+ = n
  own slot 2: [tail: N+ = 0 -> swap] P2 = D+/N+.
Reference: polynomial continued fraction on (Omega, Lambda) with the same moduli; synthesis (N,D) <- (D, m N + P D)
from the v12 seed; checks N Lambda = Omega D, D squarefree, D has exactly t roots in F*.
  confluent_model.py SHOTS SEED J_MIN WEIGHTS"""
import sys, random, collections, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dqi_math'))
import model as M

import os
NODES = list(range(18))
SINGLE_LAST = os.environ.get('DQI_SINGLE', 'first') == 'last'
if SINGLE_LAST:   # doubles on nodes 0..16 (slots 0..33), single node 17 (slot 34)
    SLOT_NODE = [a for a in range(17) for _ in (0, 1)] + [17]
else:             # single node 0 (slot 0), doubles on nodes 1..17
    SLOT_NODE = [0] + [a for a in range(1, 18) for _ in (0, 1)]
SEED_XOR = os.environ.get('DQI_SEED', 'xor') == 'xor'
assert len(SLOT_NODE) == 35


def q(i):
    return [M.kappa(i), 1, 1]


U = [1]
for _s in range(35):
    U = M.pmul(U, q(SLOT_NODE[_s]))
assert len(U) == 71


def deriv(p):
    return [p[k] if k % 2 == 1 else 0 for k in range(1, len(p))]   # formal derivative in char 2


def data(S):
    G = [0] * 70
    for r in range(1, 71):
        for j in range(71 - r):
            G[j] ^= M.mul(S[r], U[j + r])
    Gd = deriv(G)
    return G, {a: (M.pevalK(G, M.alpha(a)), M.pevalK(Gd, M.alpha(a))) for a in NODES}


def kap(old_node, node):
    return M.kappa(old_node) ^ M.kappa(node)          # q_old(alpha_node), an F constant


counts = collections.Counter()
WZERO = {}


def old_step(P, old_node, beta, n, d, w, nz=None, dz=None):
    """One old step on the new node beta; P in coefficient form (c0, c1)."""
    k = M.inv(kap(old_node, beta))
    x = M.head_at(P, beta)
    n1 = M.kscale(M.kadd(d, M.kmul(x, n)), k); counts['KxK'] += 1
    w1 = M.kadd(M.kscale(M.kadd(w, M.kscale(M.kmul(n, n), P[1])), k), M.kscale(M.kmul(n1, n), k))
    out = (n1, n, w1)
    if nz is not None:   # explicit derivatives: n+_z = (d_z + c1 n + P n_z)/kappa + n+/kappa (q' = 1)
        n1z = M.kadd(M.kscale(M.kadd(M.kadd(dz, M.kscale(n, P[1])), M.kmul(x, nz)), k), M.kscale(n1, k))
        out = out + (n1z, nz)
    return out


def extractor_conf(Yd, j_min, check_w=True):
    P = [None] * 35
    flags = {}
    # slot 0: single node 0, P0 = 1/Y0 (chart)
    Y0 = Yd[0][0]
    if Y0 == (0, 0): raise M.DomainFailure('slot 0: Y0 = 0')
    P[0] = M.head_coeffs(M.kinv(Y0), 0)
    for a in range(1, 18):
        s = 2 * a - 1
        Y, Yp = Yd[a]
        n, d, w = Y, (1, 0), Yp
        nz, dz = Yp, (0, 0)
        # old slot 0 (single), then old double nodes b < a
        olds = [(0, 0)] + [(sl, SLOT_NODE[sl]) for sl in range(1, s)]
        prev = None
        for sl, on in olds:
            n0 = n
            n, d, w, nz, dz = old_step(P[sl], on, a, n, d, w, nz, dz)
            if check_w:
                assert w == M.kadd(M.kmul(n, dz), M.kmul(d, nz)), 'w recursion'
            if sl >= 1 and sl % 2 == 0:            # closed form over the pair (sl-1, sl)
                nA0, wA0, PA, nB0 = prev
                kk = M.inv(M.mul(kap(on, a), kap(on, a)))
                xB = M.kadd(M.head_at(P[sl], a), (M.mul(P[sl][1], kap(on, a)), 0))   # P_B(beta + kappa)
                w2 = M.kadd(M.kscale(M.kadd(wA0, M.kscale(M.kmul(nA0, nA0), PA[1])), kk),
                            M.kscale(M.kmul(xB, M.kmul(nB0, nB0)), kk))
                assert w2 == w, 'two-step closed form'
            if sl >= 1 and sl % 2 == 1:
                prev = (n0, w_before, P[sl], n)
            w_before = w
        # own slot 1
        if s >= j_min and n == (0, 0):
            n, d = d, n; flags[s] = True
        elif s >= j_min:
            flags[s] = False
        if n == (0, 0): raise M.DomainFailure(f'slot {s}: zero pivot')
        x1 = M.kmul(d, M.kinv(n)); counts['div'] += 1
        P[s] = M.head_coeffs(x1, a)
        c1 = P[s][1]
        Np = M.kmul(M.kadd(w, M.kscale(M.kmul(n, n), c1)), M.kinv(n)); Dp = n
        # own slot 2
        if s + 1 >= j_min and Np == (0, 0):
            Np, Dp = Dp, Np; flags[s + 1] = True
        elif s + 1 >= j_min:
            flags[s + 1] = False
        if Np == (0, 0): raise M.DomainFailure(f'slot {s + 1}: zero pivot')
        P[s + 1] = M.head_coeffs(M.kmul(Dp, M.kinv(Np)), a); counts['div'] += 1
    return P, flags


def extractor_gen(Yd, j_min):
    """Any layout: every slot that starts a node builds (n, d, w) from all older slots by old_step."""
    P = [None] * 35; flags = {}
    s = 0
    while s < 35:
        a = SLOT_NODE[s]
        double = s + 1 < 35 and SLOT_NODE[s + 1] == a
        Y, Yp = Yd[a]
        n, d, w = Y, (1, 0), Yp
        for sl in range(s):
            n, d, w = old_step(P[sl], SLOT_NODE[sl], a, n, d, w)
        if s >= j_min:
            flags[s] = n == (0, 0)
            if double: WZERO[s] = w == (0, 0)
            if flags[s]: n, d = d, n
        if n == (0, 0): raise M.DomainFailure(f'slot {s}: zero pivot')
        P[s] = M.head_coeffs(M.kmul(d, M.kinv(n)), a); counts['div'] += 1
        if double:
            c1 = P[s][1]
            Np, Dp = M.kmul(M.kadd(w, M.kscale(M.kmul(n, n), c1)), M.kinv(n)), n
            if s + 1 >= j_min:
                flags[s + 1] = Np == (0, 0)
                if flags[s + 1]: Np, Dp = Dp, Np
            if Np == (0, 0): raise M.DomainFailure(f'slot {s + 1}: zero pivot')
            P[s + 1] = M.head_coeffs(M.kmul(Dp, M.kinv(Np)), a); counts['div'] += 1
            s += 2
        else:
            s += 1
    return P, flags


def synthesis(P, flags, lam=1):
    # seed swap: f33 XOR f34 (= [t even] with a terminal); v12 uses f34 alone
    if (flags.get(34, False) != flags.get(33, False)) if SEED_XOR else flags.get(34, False):
        assert P[34] == (0, 0)
        N, D = [0], [0, lam]
    else:
        N, D = [lam], [M.mul(lam, P[34][0]), M.mul(lam, P[34][1])]
    for s in range(33, -1, -1):
        N, D = D, M.padd(M.pmul(q(SLOT_NODE[s]), N), M.pmul(list(P[s]), D))
    return M.trim(N), M.trim(D)


def pgcd(a, b):
    a, b = M.trim(a), M.trim(b)
    while b:
        a, b = b, M.trim(M.pmod(a, b))
    return a


def shot(rng, t, j_min):
    pos = rng.sample(range(4095), t)
    err = {M.EXP[p]: rng.randrange(1, 4096) for p in pos}
    S = M.syndromes(err)
    G, Yd = data(S)
    lam = [1]
    for X in err: lam = M.pmul(lam, [X, 1])
    Om = []
    for X, e in err.items():
        quo, rem = M.pdivmod(lam, [X, 1])
        Om = M.padd(Om, M.pscale(quo, M.mul(e, M.mul(X, M.peval(U, X)))))
    assert not M.trim(M.pmod(M.padd(M.pmul(G, lam), Om), U)), 'G = Omega/Lambda mod U'
    try:
        if os.environ.get('DQI_E'):
            P, flags, _, _ = extractor_e(Yd, j_min)
        else:
            P, flags = (extractor_gen if SINGLE_LAST else extractor_conf)(Yd, j_min)
    except M.DomainFailure as e:
        return 'fail:' + str(e).split(':')[0]
    # confluent tail witnesses: second-slot flag = zero(own head); first-slot flag = zero(w at that slot)
    sec = [s_ for s_ in range(j_min, 34) if SLOT_NODE[s_] == SLOT_NODE[s_ - 1]]
    fir = [s_ for s_ in range(j_min, 34) if s_ not in sec]
    # rolling first-slot flag E: E_prev = f_first(a) AND zero(P_second(a-1)); slot 34 uses f34 the same way
    starts = [s_ for s_ in range(j_min, 35) if s_ not in sec]
    w_ok = all((P[s_] == (0, 0)) == flags[s_] for s_ in sec)
    for k in range(1, len(starts)):
        cur, prev = starts[k], starts[k - 1]
        w_ok &= flags[prev] == (flags[cur] and P[cur - 1] == (0, 0))
    WZERO.clear()
    if SINGLE_LAST and os.environ.get('DQI_TAIL') == 'conf':
        return ('witness_ok ' if w_ok else 'witness_BROKEN ') + _finish(P, flags, lam, Om, t)
    inv_ok = all((P[i] == (0, 0)) == (flags[i - 1] != flags[i]) for i in range(j_min + 1, 35))
    if not inv_ok and not os.environ.get('DQI_NOINV'): return 'tail_invariant_broken'
    if not inv_ok: return 'INVBROKEN ' + _finish(P, flags, lam, Om, t)
    return _finish(P, flags, lam, Om, t)


def _finish(P, flags, lam, Om, t):
    N, D = synthesis(P, flags)
    if not D: return 'D=0'
    ratio = M.trim(M.padd(M.pmul(N, lam), M.pmul(Om, D))) == []
    sqf = len(pgcd(D, deriv(D))) == 1
    roots = sum(1 for a_ in range(1, 4096) if M.peval(D, a_) == 0)
    lamdiv = not M.trim(M.pmod(D, lam))
    return f'ratio={ratio} squarefree={sqf} Lambda|D={lamdiv} roots_ok={roots == t} degD={len(D) - 1}'


# ---- e-form (e = sqrt(w)), exactly the planned circuit order; carry tracked ----
def fsqrt(a):
    return M.sqrt(a)


def ksq(x):          # Frobenius in K: (x0 + x1 th)^2 = x0^2 + delta x1^2 + x1^2 th
    return (M.mul(x[0], x[0]) ^ M.mul(M.DELTA, M.mul(x[1], x[1])), M.mul(x[1], x[1]))


def ksqrt(x):        # inverse Frobenius (linear)
    y1 = fsqrt(x[1])
    return (fsqrt(x[0] ^ M.mul(M.DELTA, M.mul(y1, y1))), y1)


def lin_at(P, gamma):  # value of c0 + c1 z at gamma in K
    return M.kadd((P[0], 0), M.kscale(gamma, P[1]))


def extractor_e(Yd, j_min, check=None):
    P = [None] * 35; flags = {}
    c = (1, 0)
    ecount = collections.Counter()
    for a in range(17):
        s = 2 * a
        Y, Yp = Yd[a]
        n, d, e = M.kmul(c, Y), c, M.kmul(c, ksqrt(Yp))
        for b in range(a):
            PA, PB = P[2 * b], P[2 * b + 1]
            kp = kap(b, a); ki = M.inv(kp)
            e = M.kadd(e, M.kscale(n, fsqrt(PA[1]))); ecount['FxK'] += 1
            n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(PA, a), n)), ki), n; ecount['KxK'] += 1
            gam = ksqrt(M.kadd(M.alpha(a), (kp, 0)))
            xB = M.kadd((fsqrt(PB[0]), 0), M.kscale(gam, fsqrt(PB[1])))
            e = M.kadd(e, M.kmul(xB, n)); ecount['KxK_e'] += 1
            n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(PB, a), n)), ki), n; ecount['KxK'] += 1
            e = M.kscale(e, ki)
        if check is not None:
            check.append((a, n, d, e))
        if s >= j_min:
            flags[s] = n == (0, 0)
            if flags[s]: n, d = d, n
        if n == (0, 0): raise M.DomainFailure(f'slot {s}: zero pivot')
        P[s] = M.head_coeffs(M.kmul(d, M.kinv(n)), a); ecount['div'] += 1
        c = n
        e = M.kadd(e, M.kscale(c, fsqrt(P[s][1]))); ecount['FxK'] += 1
        nn, dd = e, c
        if s + 1 >= j_min:
            flags[s + 1] = nn == (0, 0)
            if flags[s + 1]: nn, dd = dd, nn
        if nn == (0, 0): raise M.DomainFailure(f'slot {s + 1}: zero pivot')
        root = M.kmul(dd, M.kinv(nn)); ecount['div'] += 1
        P[s + 1] = M.head_coeffs(ksq(root), a)
        c = nn
    # single node 17 at slot 34
    n, d = M.kmul(c, Yd[17][0]), c
    for sl in range(34):
        n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(P[sl], 17), n)), M.inv(kap(SLOT_NODE[sl], 17))), n
        ecount['KxK'] += 1
    flags[34] = n == (0, 0)
    if flags[34]: n, d = d, n
    if n == (0, 0): raise M.DomainFailure('slot 34: zero pivot')
    P[34] = M.head_coeffs(M.kmul(d, M.kinv(n)), 17); ecount['div'] += 1
    return P, flags, n, ecount


def check_e_vs_w(rng, t):
    """e^2 = w for the direct definition on the real data, and heads equal extractor_gen."""
    pos = rng.sample(range(4095), t); err = {M.EXP[p]: rng.randrange(1, 4096) for p in pos}
    G, Yd = data(M.syndromes(err))
    try:
        Pg, fg = extractor_gen(Yd, 17)
    except M.DomainFailure as ex:
        Pg = 'fail'
    try:
        Pe, fe, c, cnt = extractor_e(Yd, 17)
    except M.DomainFailure as ex:
        Pe, cnt = 'fail', None
    return Pg == Pe, cnt


if __name__ == '__main__':
    shots, seed, j_min = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    for t in [int(x) for x in sys.argv[4].split(',')]:
        tal = collections.Counter()
        counts.clear()
        for _ in range(shots):
            tal[shot(rng, t, j_min)] += 1
        print(f't={t} shots={shots} j_min={j_min} seed={seed}', dict(tal),
              f"per-shot KxK={counts['KxK'] / shots:.0f} div={counts['div'] / shots:.0f}", flush=True)

