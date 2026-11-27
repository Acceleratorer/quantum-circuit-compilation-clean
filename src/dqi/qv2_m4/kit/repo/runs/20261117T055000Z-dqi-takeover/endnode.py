# Copyright 2026 Syed Asad Ali (original builder of the v12 DQI decoder this extends). SPDX-License-Identifier: Apache-2.0.
# Lane dqi_v8b (2026-11-16): SEQUENTIAL end node at 889 qubits, after the end node of Syed Asad Ali's compiled
# 890-qubit decoder (slot 33 = modulus x^2 at the field point 0, slot 34 = the point at infinity, 12-bit chains over
# the 33 stored heads; layout decoded by lanes dqi_fnode / dqi_v8). Word model: src/dqi_v8b/seq_model.py.
# Lineage starting from Syed Asad Ali.
"""12-bit chain passes at 0 / infinity and the helpers of the end node (installed by confluent_ext)."""
import kickmix as km
from tower_inverse import apply_inplace_linear as lin, rows_from_columns, xor_product, phase_product, kernel
from tower_inverse import invert_inplace

F = km.GF2Field(12)
DELTA = 2048


def _sqrt(x):
    return F.pow(x, 2048) if x else 0


def _kappa(i):
    t = 2 * i
    return DELTA ^ F.mul(t, t) ^ t


def const_rows(c):                                   # w <- c w  (c != 0)
    return rows_from_columns([F.mul(c, 1 << j) for j in range(12)])


R_SQ = rows_from_columns([F.mul(1 << j, 1 << j) for j in range(12)])
R_SQRT = rows_from_columns([_sqrt(1 << j) for j in range(12)])


def pass_constants(slot_node, at_zero):
    n = len(slot_node)
    kap = [(_kappa(slot_node[k]) if at_zero else 1) for k in range(n)]
    pi = [1] * (n + 1); sg = [0] * (n + 1)
    for k in range(n - 1, -1, -1):
        ki = F.invert(kap[k]); pi[k] = F.mul(pi[k + 1], ki); sg[k] = sg[k + 1] ^ ki
    return kap, pi, sg


def mult_rows(pi_k, sg_k, at_zero):
    """Linear map on a head word (c0 = bits 0..11, c1 = bits 12..23): the hd half becomes
    m = sqrt(pi_k) (sqrt(hd) + sqrt(sg_k) sqrt(h)); h = c0 (at 0) or c1 (at infinity) is unchanged."""
    sp, ss = _sqrt(pi_k), _sqrt(sg_k)
    h_off, hd_off = (0, 12) if at_zero else (12, 0)
    cols = [0] * 24
    for j in range(12):
        x = 1 << j
        cols[h_off + j] = (x << h_off) | (F.mul(sp, F.mul(ss, _sqrt(x))) << hd_off)
        cols[hd_off + j] = F.mul(sp, _sqrt(x)) << hd_off
    fwd = rows_from_columns(cols)
    # inverse: hd = (m / sp + ss sqrt(h))^2
    spi = F.invert(sp)
    icols = [0] * 24
    for j in range(12):
        x = 1 << j
        icols[h_off + j] = (x << h_off) | (F.mul(F.mul(ss, _sqrt(x)), F.mul(ss, _sqrt(x))) << hd_off)
        y = F.mul(spi, x)
        icols[hd_off + j] = F.mul(y, y) << hd_off
    return fwd, rows_from_columns(icols)


class Pass:
    """One 12-bit chain over the stored heads (e = sqrt of the Wronskian form, closed-form multipliers):
    per head k: e ^= m_k n; d ^= h_k n; d /= kappa_k; (n, d) <- (d, n).  84 T per head."""

    def __init__(self, slot_node, at_zero):
        self.at_zero = at_zero
        self.kap, self.pi, self.sg = pass_constants(slot_node, at_zero)
        self.rows = [mult_rows(self.pi[k], self.sg[k], at_zero) for k in range(len(slot_node))]
        self.kr = [(const_rows(F.invert(k)), const_rows(k)) for k in self.kap]

    def halves(self, head):
        return (head[:12], head[12:]) if self.at_zero else (head[12:], head[:12])   # (h, hd/m)

    def forward(self, b, heads, n, d, e):
        for k, head in enumerate(heads):
            hh, mh = self.halves(head)
            fwd, inv = self.rows[k]
            lin(b, head, fwd); xor_product(b, mh, n, e); lin(b, head, inv)
            xor_product(b, hh, n, d)
            if self.kap[k] != 1: lin(b, d, self.kr[k][0])
            n, d = d, n
        return n, d, e

    def reverse(self, b, heads, n, d, e):
        for k in reversed(range(len(heads))):
            head = heads[k]
            n, d = d, n
            if self.kap[k] != 1: lin(b, d, self.kr[k][1])
            hh, mh = self.halves(head)
            fwd, inv = self.rows[k]
            xor_product(b, hh, n, d)
            lin(b, head, fwd); xor_product(b, mh, n, e); lin(b, head, inv)
        return n, d, e


def deferred_scale(b, target, multiplier):
    """target <- target * multiplier (42 T); returns the HMR mask of the old target (Syed Asad Ali's
    gauge_park_lender.deferred_scale)."""
    tmp = b.alloc_qubits(12)
    xor_product(b, target, multiplier, tmp)
    b.swap(target, tmp)
    m = b.alloc_bits(12); b.hmr(tmp, m); b.free(tmp)
    return m


def repay(b, value, inverse_multiplier, mask):
    """pay (-1)^(mask . (value * inverse_multiplier)) (gauge_park_lender.repay_scale)."""
    phase_product(b, value, inverse_multiplier, mask, kernel(12))
    b.free(mask)


def scale_words(b, words, mult):
    return [deferred_scale(b, w, mult) for w in words]


def unscale_words(b, words, mult, masks):
    """Return of scale_words: words were w*mult with forward masks (old w). Inverts mult in place twice."""
    invert_inplace(b, mult)
    rm = [deferred_scale(b, w, mult) for w in words]          # w <- w / mult (= old w)
    for w, m in zip(words, masks):
        b.cz(m, w); b.free(m)                                  # forward debts on old w
    invert_inplace(b, mult)
    for w, m in zip(words, rm):
        repay(b, w, mult, m)                                   # debts on w*mult = old w * mult


# ---------------- lane dqi_v9b: SEQUENTIAL end node at 890 (nopark), word model src/dqi_v8b/seq_model.py ----------------
R_DEL, R_DELI = const_rows(DELTA), const_rows(F.invert(DELTA))


def hmr_word(b, w):
    m = b.alloc_bits(len(w)); b.hmr(w, m); b.free(w)
    return m


def one(b):
    return b.alloc_qubits(1)[0]


def ccx_word(b, c, src, dst):                        # dst ^= c * src (12 Toffoli)
    for x, y in zip(src, dst):
        b.ccx(c, x, y)


class SeqEnd:
    """End node after the 33 stored heads: chain A at 0 (scale lam), kernel A, chain B at infinity (scale 1/U), query,
    kernel B, class fixups and the r = 1 step.  Output N (2 words), D (3 words) = the synthesis state after r = 1:
    N = sig P34, D = sig (x^2 + P33 P34) (orientation and low-weight classes as v8_model.end_block)."""

    def __init__(self, slot_node, Tail):
        self.PA, self.PB, self.Tail = Pass(slot_node, True), Pass(slot_node, False), Tail

    def zx(self, b, word, flag):
        self.Tail.zero_xor(b, word, flag)

    def forward(self, b, heads, S66, S67, S68, S69, lam):
        from compact_inverse22 import compact_inverse_twelve as ci22
        from phase_inverse12 import phase_inverse_twelve_polynomial as pinv
        R = {}
        R['mA'] = [deferred_scale(b, S66, lam), deferred_scale(b, S67, lam)]          # F1 (debts: return)
        nA, dA, eA = self.PA.forward(b, heads, S66, lam, S67)                         # F2
        s = one(b); self.zx(b, nA, s); b.cswap(s, nA, dA)                             # F3
        U = nA
        T = ci22(b, U); b.swap(U, T); U, T = T, U                                     # F4 (T kept in U's register)
        # Lane DQI takeover 2026-11-17: retire U before the four scales. Pay their old-target
        # masks jointly through T^{-1}; native gadget:24->22 helpers at+62 executed Toffolis.
        mU = hmr_word(b, U); pinv(b, T, mU); b.free(mU)
        scaled_words = (dA, eA, S68, S69)
        scaled_masks = [deferred_scale(b, w, T) for w in scaled_words]
        import multi_qphase
        multi_qphase.emit(b, T, list(zip(scaled_words, scaled_masks)))
        for mask in scaled_masks: b.free(mask)
        a, bw = dA, eA
        nB, dB, eB = self.PB.forward(b, heads, S68, T, S69)                           # F5
        lin(b, bw, R_SQ); xor_product(b, bw, nB, dB)                                  # F6 (bw = B2 from here)
        lin(b, a, R_SQRT); xor_product(b, a, nB, eB); lin(b, a, R_SQ)
        n2, d2, e2 = dB, nB, eB
        b.cswap(s, n2, d2)                                                            # F7
        c0 = one(b); self.zx(b, n2, c0); b.cswap(c0, n2, d2)
        mc0 = hmr_word(b, km.array([c0]))
        u = n2
        Ui = ci22(b, u); b.swap(u, Ui); u, Ui = Ui, u; mu = hmr_word(b, u); pinv(b, Ui, mu); b.free(mu)            # F8
        R['md2'] = deferred_scale(b, d2, Ui); R['me2'] = deferred_scale(b, e2, Ui)
        v2, w2 = d2, e2
        Cm = one(b); self.zx(b, km.array([*v2, *w2]), Cm); b.cz(mc0[0], Cm); b.free(mc0)
        lin(b, w2, R_SQ)                                                              # F9: q0 = W2 = w2^2
        p0, p1, q0, q1 = a, bw, w2, v2
        ccx_word(b, s, p1, q1)
        b.cswap(s, p0, q1); b.cswap(s, p1, q0)
        h = one(b); b.ccx(s, Cm, h); C = one(b); b.cx(Cm, C); b.cx(h, C)
        b.cswap(C, p0, p1)
        R['mq0'] = deferred_scale(b, q0, Ui); R['mq1'] = deferred_scale(b, q1, Ui)    # F10
        d0, d1 = q0, q1
        ccx_word(b, C, Ui, d0); ccx_word(b, C, d0, Ui)
        xor_product(b, p1, d1, Ui)
        t1 = b.alloc_qubits(12); xor_product(b, p0, d1, t1); xor_product(b, p1, d0, t1)
        b.swap(p1, t1); p1, t1 = t1, p1
        R['mp1'] = hmr_word(b, p1)
        t0 = b.alloc_qubits(12); xor_product(b, p0, d0, t0)
        b.swap(p0, t0); p0, t0 = t0, p0
        R['mp0'] = hmr_word(b, p0)
        D0, D1, D2 = t0, t1, Ui
        ccx_word(b, h, D2, D1)
        lin(b, D2, R_DEL); ccx_word(b, h, D2, D0); lin(b, D2, R_DELI)
        rho = one(b); b.cx(s, rho); b.cx(C, rho)
        b.cswap(rho, d0, d1); b.cswap(rho, D0, D2)
        b.cx(C, rho); b.cx(s, rho); b.free(km.array([rho]))
        b.cx(h, C); b.cx(Cm, C); b.free(km.array([C])); b.ccx(s, Cm, h); b.free(km.array([h]))
        R['ms'] = hmr_word(b, km.array([s])); R['mCm'] = hmr_word(b, km.array([Cm]))
        R['reg'] = dict(nA=nA, dA=dA, eA=eA, T=T, S68=S68, S69=S69, nB=nB, dB=dB, eB=eB, a=a, bw=bw)
        return [d0, d1], [D0, D1, D2], R

    def reverse(self, b, heads, N, D, R, ext=None, mE31=None, ripple=None):
        """Return of forward from the exact (N, D). With ext/mE31: also rebuilds f31 = h and [head 32 = 0] (paid
        with mE31) and returns (Ep, mz) for ext.closing."""
        from compact_inverse22 import compact_inverse_twelve as ci22
        from phase_inverse12 import phase_inverse_twelve_polynomial as pinv
        g = R['reg']; a, bw, nB, dB, eB = g['a'], g['bw'], g['nB'], g['dB'], g['eB']
        d0, d1 = N; D0, D1, D2 = D
        assert [tuple(x) for x in (d0, d1, D0, D1, D2)] == [tuple(x) for x in (eB, nB, a, bw, dB)]
        zx, free1 = self.zx, (lambda q: b.free(km.array([q])))
        # R0: class flags from (N, D): h = [N = 0], C = [N0 = 0 and D0 = 0], s = [N0 = 0] xor C, Cm = C xor h
        hw = one(b); zx(b, km.array([*d0, *d1]), hw)
        Cw = one(b); zx(b, km.array([*d0, *D0]), Cw)
        s = one(b); zx(b, d0, s); b.cx(Cw, s)
        b.cx(hw, Cw); Cm = Cw
        b.ccx(s, Cm, hw); free1(hw)
        b.cz(R['ms'][0], s); b.free(R['ms']); b.cz(R['mCm'][0], Cm); b.free(R['mCm'])
        # R1: inverse of the F10 tail
        h = one(b); b.ccx(s, Cm, h); C = one(b); b.cx(Cm, C); b.cx(h, C)
        rho = one(b); b.cx(s, rho); b.cx(C, rho)
        b.cswap(rho, D0, D2); b.cswap(rho, d0, d1)
        b.cx(C, rho); b.cx(s, rho); free1(rho)
        lin(b, D2, R_DEL); ccx_word(b, h, D2, D0); lin(b, D2, R_DELI)
        ccx_word(b, h, D2, D1)
        b.cx(h, C); b.cx(Cm, C); free1(C); b.ccx(s, Cm, h); free1(h)
        mCr = hmr_word(b, km.array([Cm]))
        # Narrow dependent quotient session: 18 helpers, +22 T versus cached reciprocal.
        from norm_division import dependent
        dependent(b, D0, D1, d0, d1)
        p0, p1 = D0, D1
        if ripple is not None:   # C class: (p1, p0) = the lost head Q (c0, c1); after the ripple = P33
            ripple(km.array([*p1, *p0]))
        b.cz(R['mp0'], p0); b.free(R['mp0']); b.cz(R['mp1'], p1); b.free(R['mp1'])
        sg = D2
        xor_product(b, p1, d1, sg)
        z = one(b); zx(b, sg, z)                                       # z = C ([sigma word = 0] only in C)
        ccx_word(b, z, d0, sg); ccx_word(b, z, sg, d0)
        y = one(b); zx(b, d0, y); hh = one(b); b.ccx(s, y, hh)         # h = s and [d0 = 0]
        b.cz(mCr[0], hh); b.cz(mCr[0], z); b.free(mCr)
        b.ccx(s, y, hh); free1(hh); zx(b, d0, y); free1(y)
        mz = hmr_word(b, km.array([z]))
        Si = ci22(b, sg)                                               # q = d / sigma
        for w, mq in ((d0, R['mq0']), (d1, R['mq1'])):
            m = deferred_scale(b, w, Si); repay(b, w, sg, m)
            b.cz(mq, w); b.free(mq)
        mS = hmr_word(b, Si); pinv(b, sg, mS); b.free(mS)
        q0, q1 = d0, d1
        Cm = one(b); zx(b, km.array([*q0, *q1]), Cm)
        C = one(b); b.cx(Cm, C); b.ccx(s, Cm, C)
        b.cz(mz[0], C); b.free(mz)
        # inverse of F9
        b.cswap(C, p0, p1)
        b.ccx(s, Cm, C); b.cx(Cm, C); free1(C)
        b.cswap(s, p1, q0); b.cswap(s, p0, q1)
        ccx_word(b, s, p1, q1)
        lin(b, q0, R_SQRT)
        assert [tuple(x) for x in (p0, p1, q0, q1, sg)] == [tuple(x) for x in (a, bw, eB, nB, dB)]
        v2, w2, Ui = q1, q0, sg
        # inverse of F8 (Cm -> HMR, recomputed after as c0 = [d2 = 0 and e2 = 0])
        mCk = hmr_word(b, km.array([Cm]))
        u = ci22(b, Ui)
        for w, md in ((v2, R['md2']), (w2, R['me2'])):
            m = deferred_scale(b, w, u); repay(b, w, Ui, m)
            b.cz(md, w); b.free(md)
        b.swap(Ui, u); Ui, u = u, Ui
        mu = hmr_word(b, Ui); pinv(b, u, mu); b.free(mu)
        n2, d2, e2 = u, v2, w2
        c0 = one(b); zx(b, km.array([*d2, *e2]), c0); b.cz(mCk[0], c0); b.free(mCk)
        b.cswap(c0, n2, d2); zx(b, n2, c0); free1(c0)
        b.cswap(s, n2, d2)
        # inverse of F6
        lin(b, a, R_SQRT); xor_product(b, a, nB, eB); lin(b, a, R_SQ)
        xor_product(b, bw, nB, dB); lin(b, bw, R_SQRT)
        S68, T, S69 = self.PB.reverse(b, heads, nB, dB, eB)
        assert [tuple(x) for x in (S68, T, S69)] == [tuple(x) for x in (g['S68'], g['T'], g['S69'])]
        # inverse of F4
        U = ci22(b, T)
        for w in (a, bw, S68, S69):
            m = deferred_scale(b, w, U); repay(b, w, T, m)
        b.swap(T, U); T, U = U, T
        mT = hmr_word(b, T); pinv(b, U, mT); b.free(mT)
        nA, dA, eA = U, a, bw
        assert [tuple(x) for x in (nA, dA, eA)] == [tuple(x) for x in (g['nA'], g['dA'], g['eA'])]
        # inverse of F3
        b.cswap(s, nA, dA); zx(b, nA, s); free1(s)
        out = None
        if ext is not None:   # f31 = h and [head 32 = 0], h = [nA = 0 and eA = 0] here
            hh = one(b); zx(b, km.array([*nA, *eA]), hh)
            out = ext.prev_flag(hh, heads[32], mE31)
            zx(b, km.array([*nA, *eA]), hh); free1(hh)
        S66, lam, S67 = self.PA.reverse(b, heads, nA, dA, eA)
        # inverse of F1
        Li = ci22(b, lam)
        for w, mA in zip((S66, S67), R['mA']):
            m = deferred_scale(b, w, Li); repay(b, w, lam, m)
            b.cz(mA, w); b.free(mA)
        mL = hmr_word(b, Li); pinv(b, lam, mL); b.free(mL)
        return (S66, lam, S67), out
