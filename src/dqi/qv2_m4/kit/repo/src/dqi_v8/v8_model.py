# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_v8: word model of kit v8 = v7 (single-first, doubles 1..16 on slots 1..32) with the PUBLIC END NODE
(Syed Asad Ali's 890-qubit decoder, Apache-2.0; original builder Syed Asad Ali; layout decoded by lane dqi_fnode):
slot 33 = modulus x^2 (u = 0), slot 34 = the point at infinity; U = q_0 prod_{a=1..16} q_a^2 x^2 (deg 68) + 2 conditions
at infinity. Both end points run 12-bit passes over the 33 stored heads (no tests), then the end block gives the
synthesis state after r = 1:  N = lam P34, D = lam (x^2 + P33 P34).   python3 v8_model.py SHOTS SEED WEIGHTS"""
import sys, random, collections, os
os.environ['DQI_SINGLE'] = 'first'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dqi_end'))
import confluent_model as C
M = C.M
FIRST_TEST = 19
Z = (0, 0)
X2 = [0, 0, 1]
SLOT_NODE = [0] + [a for a in range(1, 17) for _ in (0, 1)]          # slots 0..32
U = [1]
for _s in range(33): U = M.pmul(U, C.q(SLOT_NODE[_s]))
U = M.pmul(U, X2)
assert len(U) == 69


def data8(S):
    G = [0] * 68
    for r in range(1, 69):
        for j in range(69 - r): G[j] ^= M.mul(S[r], U[j + r])
    Gd = C.deriv(G)
    Yd = {a: (M.pevalK(G, M.alpha(a)), M.pevalK(Gd, M.alpha(a))) for a in range(17)}
    f1 = f2 = 0
    for j in range(69):
        f1 ^= M.mul(U[j], S[j + 1]); f2 ^= M.mul(U[j], S[j + 2])
    return G, Yd, (G[0], G[1]), (f1, f2)


def extractor_old(Yd):
    """slots 0..32 exactly as sf6_model (v7 circuit rules), returns heads, first-slot flags, carry."""
    P = [None] * 33; flags = {}
    Y0 = Yd[0][0]
    if Y0 == Z: raise M.DomainFailure('slot 0: Y0 = 0')
    P[0] = M.head_coeffs(M.kinv(Y0), 0)
    c = (1, 0)
    for a in range(1, 17):
        s = 2 * a - 1
        Y, Yp = Yd[a]
        k0 = C.kap(0, a)
        e_geo = M.kadd(M.kscale(C.ksqrt(Yp), C.fsqrt(k0)), C.ksqrt(Y))
        n, d, e = M.kmul(c, Y), c, M.kmul(c, e_geo)
        gam = C.ksqrt(M.kadd(M.alpha(a), (k0, 0)))
        x0 = M.kadd((C.fsqrt(P[0][0]), 0), M.kscale(gam, C.fsqrt(P[0][1])))
        e = M.kadd(e, M.kmul(x0, n))
        ki = M.inv(k0)
        n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(P[0], a), n)), ki), n
        e = M.kscale(e, ki)
        for b in range(1, a):
            PA, PB = P[2 * b - 1], P[2 * b]
            kp = C.kap(b, a); ki = M.inv(kp)
            e = M.kadd(e, M.kscale(n, C.fsqrt(PA[1])))
            n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(PA, a), n)), ki), n
            gam = C.ksqrt(M.kadd(M.alpha(a), (kp, 0)))
            xB = M.kadd((C.fsqrt(PB[0]), 0), M.kscale(gam, C.fsqrt(PB[1])))
            e = M.kadd(e, M.kmul(xB, n))
            n, d = M.kscale(M.kadd(d, M.kmul(M.head_at(PB, a), n)), ki), n
            e = M.kscale(e, ki)
        if s >= FIRST_TEST:
            flags[s] = n == Z
            if flags[s]: n, d = d, n
        if n == Z: raise M.DomainFailure(f'slot {s}: zero pivot')
        P[s] = M.head_coeffs(M.kmul(d, M.kinv(n)), a)
        c = n
        e = M.kadd(e, M.kscale(c, C.fsqrt(P[s][1])))
        x = M.kmul(e, M.kinv(c))
        P[s + 1] = M.head_coeffs(C.ksq(M.kinv(x) if x != Z else Z), a)
    return P, flags, c


def fstep(st, h, kap, dq):
    """one query of an F-valued 2-jet chain state (n, d, w = (n d)'), head value h and head derivative hd = st's
    caller-supplied (h, hd); modulus value kap, derivative dq."""
    n, d, w = st
    hv, hd = h
    ki = M.inv(kap)
    n1 = M.mul(d ^ M.mul(hv, n), ki)
    w1 = M.mul(w ^ M.mul(hd, M.mul(n, n)), ki) ^ (M.mul(M.mul(n1, n), ki) if dq else 0)
    return (n1, n, w1)


def passes(P, g, f):
    s0 = (g[0], 1, g[1]); si = (f[0], 1, f[1])
    for k in range(33):
        c0, c1 = P[k]
        s0 = fstep(s0, (c0, c1), M.kappa(SLOT_NODE[k]), 1)
        si = fstep(si, (c1, c0), 1, 1)
    return s0, si


def head2(st):   # (c_value, c_derivative) of d/n as a 2-jet: value d/n, derivative w/n^2
    n, d, w = st
    ni = M.inv(n)
    return M.mul(d, ni), M.mul(w, M.mul(ni, ni))


def end_generic(s0, si, swap=False):
    """N = P34, D = x^2 + P33 P34 (normal) or N = P34, D = 1 + P33 P34 (swapped: infinity first). lam = 1."""
    A, B = (si, s0) if swap else (s0, si)
    if A[0] == 0: raise M.DomainFailure('end: first pivot 0')
    v, dv = head2(A)                       # first point head (value, derivative) in its own coordinate
    # first head as z-polynomial: at 0: c0 = v, c1 = dv; at infinity: c1 = v, c0 = dv
    P33 = (dv, v) if swap else (v, dv)
    # second point through the first head; modulus x^2 seen from the second point: value 1, derivative 0
    hB = (P33[0], P33[1]) if swap else (P33[1], P33[0])   # (value, derivative) of P33 at the second point
    B2 = fstep(B, hB, 1, 0)
    if B2[0] == 0: raise M.DomainFailure('end: second pivot 0')
    v2, dv2 = head2(B2)
    P34 = (v2, dv2) if swap else (dv2, v2)
    N = list(P34)
    D = M.padd([0, 0, 1] if not swap else [1], M.pmul(list(P33), list(P34)))
    return M.trim(N), M.trim(D), P33, P34


def synth(P, N, D):
    for s in range(32, -1, -1):
        N, D = D, M.padd(M.pmul(C.q(SLOT_NODE[s]), N), M.pmul(list(P[s]), D))
    return M.trim(N), M.trim(D)


def finish(N, D, lam, Om, t):
    if not D: return 'D=0'
    ratio = M.trim(M.padd(M.pmul(N, lam), M.pmul(Om, D))) == []
    sqf = len(C.pgcd(D, C.deriv(D))) == 1
    roots = sum(1 for a_ in range(1, 4096) if M.peval(D, a_) == 0)
    return f'ratio={ratio} sqf={sqf} roots_ok={roots == t} degD={len(D) - 1}'


def make(rng, t):
    pos = rng.sample(range(4095), t)
    err = {M.EXP[p]: rng.randrange(1, 4096) for p in pos}
    lam = [1]
    for X in err: lam = M.pmul(lam, [X, 1])
    Om = []
    for X, ev in err.items():
        quo, rem = M.pdivmod(lam, [X, 1])
        Om = M.padd(Om, M.pscale(quo, M.mul(ev, M.mul(X, M.peval(U, X)))))
    return err, lam, Om


# ---------------- circuit-faithful pieces ----------------
def gauge_or(c):
    """g = [lo = 0] xor [hi = 0]; if g: lo ^= hi; hi ^= 2 lo  -> both halves nonzero (c != 0)."""
    lo, hi = c
    g = (lo == 0) != (hi == 0)
    if g:
        lo ^= hi; hi ^= M.mul(2, lo)
    assert lo and hi
    return lo, hi, g


def pass_e(P, n, d, e, at_zero):
    """12-bit pass over the 33 stored heads in the e (= sqrt Wronskian) form with the closed-form multipliers
    (lane dqi_fnode echain.py): per old slot k: e ^= mult_k * n; d ^= h_k * n; d /= kappa_k; swap(n, d)."""
    pi = [1] * 34; sg = [0] * 34
    for k in range(32, -1, -1):
        kk = M.kappa(SLOT_NODE[k]) if at_zero else 1
        pi[k] = M.mul(pi[k + 1], M.inv(kk)); sg[k] = sg[k + 1] ^ M.inv(kk)
    for k in range(33):
        c0, c1 = P[k]
        h, hd = (c0, c1) if at_zero else (c1, c0)
        mult = M.mul(M.sqrt(pi[k]), M.sqrt(hd) ^ M.mul(M.sqrt(sg[k]), M.sqrt(h)))
        e ^= M.mul(mult, n)
        kk = M.kappa(SLOT_NODE[k]) if at_zero else 1
        n, d = M.mul(d ^ M.mul(h, n), M.inv(kk)), n
    return n, d, e


def e_init(lam, g0, g1, at_zero):
    """initial e word = lam * sqrt(pi_0) (sqrt(g1) + sqrt(sigma_0) sqrt(g0)) (a geometry word times lam)."""
    pi = 1; sg = 0
    for k in range(33):
        kk = M.kappa(SLOT_NODE[k]) if at_zero else 1
        pi = M.mul(pi, M.inv(kk)); sg ^= M.inv(kk)
    return M.mul(lam, M.mul(M.sqrt(pi), M.sqrt(g1) ^ M.mul(M.sqrt(sg), M.sqrt(g0))))


def end_block(A, B):
    """A = (n, d, e) at 0, B at infinity (any nonzero scales).  Returns (N, D) (lam-free: output scale 1 here,
    the circuit's scale is a unit) and the flags (s, h, C).
    s = [n_A = 0]: swap the triples (infinity first, D constant term 1 instead of x^2).
    h = [first pivot = 0] (after the swap; = odd t <= 33): D = (pad) beta x^2 + x + 1 (beta = delta, Tr = 1).
    C = [second pivot = 0] (even t <= 34): N = z, D = z P33 (no x^2 term)."""
    s = A[0] == 0
    F1, F2 = (B, A) if s else (A, B)
    h = F1[0] == 0
    def inv0(x): return M.inv(x) if x else 0
    ni = inv0(F1[0])
    v = M.mul(F1[1], ni); dv = M.mul(M.mul(F1[2], ni), M.mul(F1[2], ni))   # d/n, (e/n)^2
    P33 = (dv, v) if s else (v, dv)                                        # z-polynomial (c0, c1)
    hv, hd = (P33[0], P33[1]) if s else (P33[1], P33[0])                   # head value/derivative at the 2nd point
    n2 = F2[1] ^ M.mul(hv, F2[0]); d2 = F2[0]; e2 = F2[2] ^ M.mul(M.sqrt(hd), F2[0])
    C = n2 == 0
    ni2 = inv0(n2)
    v2 = M.mul(d2, ni2); dv2 = M.mul(M.mul(e2, ni2), M.mul(e2, ni2))
    P34 = (v2, dv2) if s else (dv2, v2)
    N = [0, 1] if C else list(P34)
    D = M.padd(M.pmul(list(P33), N), [] if C else ([1] if s else [0, 0, 1]))
    if h: D = M.padd(D, [0, 1, M.DELTA])
    return M.trim(N), M.trim(D), (s, h, C), P33, P34


def closing_safe(P, N, D):
    """native synthesis closing recovers P_i = (PD)(alpha_i)/D(alpha_i): needs D_old(alpha_i) != 0 or P_i = 0."""
    bad = []
    for s_ in range(32, -1, -1):
        a = SLOT_NODE[s_]
        if P[s_] != Z and M.pevalK(D, M.alpha(a)) == Z: bad.append(s_)
        N, D = D, M.padd(M.pmul(C.q(a), N), M.pmul(list(P[s_]), D))
    return bad


def native_return(P, N1, D1, fl3):
    """Synthesis forward (32..0) then the NATIVE closings (0..32): P_i(alpha) = D'(alpha)/D_old(alpha) (0/0 -> 0),
    N_old = (D' - P_i D_old)/q_i. Then the end-block return reads Q = D/N... in the C case Q = D/z (N = z) and v7's
    head_ripple (z = [head(s+1) = 0]; cswap(head s, head s+2), s = 31..17, carrier head 33 = Q) runs. Checks: heads
    and the r = 1 state come back exact (Q = P33 true; P33 = 0 for t <= 32)."""
    st = []; N, D = N1, D1
    for s_ in range(32, -1, -1):
        st.append((N, D)); a = SLOT_NODE[s_]
        N, D = D, M.padd(M.pmul(C.q(a), N), M.pmul(list(P[s_]), D))
    H = {}
    for s_ in range(0, 33):
        a = SLOT_NODE[s_]; Nn, Dn = N, D            # Nn = D_old, Dn = q N_old + P D_old
        Dold = Nn; al = M.alpha(a)
        dv = M.pevalK(Dold, al)
        pv = M.kmul(M.pevalK(Dn, al), M.kinv(dv)) if dv != Z else Z
        H[s_] = M.head_coeffs(pv, a)
        num = M.padd(Dn, M.pmul(list(H[s_]), Dold))
        qq, rr = M.pdivmod(num, C.q(a)) if M.trim(num) else ([], [])
        if M.trim(rr): return 'RET_NONDIV'
        N, D = M.trim(qq), M.trim(Dold)
    exact_state = (M.trim(N), M.trim(D)) == (M.trim(N1), M.trim(D1))
    s_, h_, Cf = fl3
    if Cf:   # end-block return in the C case: N must read z; Q = D / z
        if M.trim(N) != [0, 1]: return 'RET_C_N!=z'
        Dq = M.trim(D) + [0, 0, 0]
        if Dq[0]: return 'RET_C_D0!=0'
        Q = (Dq[1], Dq[2])
    else:
        Q = 'exact' if exact_state else None
        if Q is None: return 'RET_STATE_WRONG'
    heads = [H[i] for i in range(33)] + [Q if Cf else Z]
    for sl in range(31, 16, -2):
        if heads[sl + 1] == Z: heads[sl], heads[sl + 2] = heads[sl + 2], heads[sl]
    ok = heads[:33] == [tuple(x) for x in P[:33]]
    q33 = heads[33] if Cf else None
    return ('ret_ok' if ok else 'RET_HEADS_WRONG') + ('' if not Cf else (' Q=P33' if q33 == tuple(_true_P33[0]) else ' Q_WRONG'))


_true_P33 = [None]


def shot(rng, t):
    err, lamP, Om = make(rng, t)
    G, Yd, g, f = data8(M.syndromes(err))
    try:
        P, fl, c = extractor_old(Yd)
    except M.DomainFailure as ex:
        return 'old_fail:' + str(ex).split(':')[0]
    lo, hi, gg = gauge_or(c)
    A = (M.mul(lo, g[0]), lo, e_init(lo, g[0], g[1], True))
    B = (M.mul(hi, f[0]), hi, e_init(hi, f[0], f[1], False))
    A = pass_e(P, *A, True); B = pass_e(P, *B, False)
    # cross-check the e form against the exact Wronskian recursion (fstep)
    s0, si = passes(P, g, f)
    okA = M.mul(A[0], M.inv(lo)) == s0[0] if lo else False
    okW = M.mul(A[2], A[2]) == M.mul(M.mul(lo, lo), s0[2]) and M.mul(B[2], B[2]) == M.mul(M.mul(hi, hi), si[2])
    N, D, fl3, P33, P34 = end_block(A, B)
    _true_P33[0] = P33
    sfx = f' s{int(fl3[0])}h{int(fl3[1])}C{int(fl3[2])}' + ('' if okA and okW else ' EFORM_BROKEN')
    if fl3[0] and fl3[1] and t == 35: return 'double_pivot' + sfx
    if fl3[0] and fl3[2]: return 'swap_and_C' + sfx
    Nf, Df = synth(P, N, D)
    bad = closing_safe(P, N, D)
    rt = native_return(P, N, D, fl3)
    return finish(Nf, Df, lamP, Om, t) + sfx + (f' unsafe{bad}' if bad else '') + ' ' + rt


if __name__ == '__main__':
    shots, seed = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(seed)
    for t in [int(x) for x in sys.argv[3].split(',')]:
        tal = collections.Counter(shot(rng, t) for _ in range(shots))
        print(f't={t} shots={shots} seed={seed}', dict(tal), flush=True)
