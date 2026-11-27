# Copyright 2026 Syed Asad Ali (original builder of the v12 DQI decoder this extends). SPDX-License-Identifier: Apache-2.0.
# Modifications 2026-11-15 by lane dqi_pair: confluent double-node key extractor (17 double quadratic nodes + 1 single),
# confluent syndrome geometry U = q_17 prod_{a<17} q_a^2, slot -> node map for the synthesis, extractor cutoff 17.
# Modifications 2026-11-15 by lane dqi_guard: synthesis-return Guard3 (no derivative view on X; N from all points).
# Modifications 2026-11-15 by lane dqi_guard: Guard3; then RIPPLE: native synthesis return + head ripple after the seed.
# Modifications 2026-11-15 by lane dqi_tail: tail flags erased by HMR with the phase paid at the return's existing
# zero queries (forward: rolling first-slot flag and second-slot flag; return: the zero(P_{s-1}) witness; the head
# ripple's z = [head(s+1) = 0]).
# Modifications 2026-11-16 by lane dqi_tail (v6): node normalisation as in Syed Asad Ali's compiled v13 decoder
# (decoded in runs/20261115T235213Z-dqi-norm/LANE.md): one shared 1/N(n) for d/n and e/n, x = e/n + sqrt(c1) (linear),
# head2 = 1/x by an in-place inverse (inv0), the unit stays n; no second-slot test or swap.
# Modifications 2026-11-16 by lane dqi_end / dqi_int (v7): SINGLE-FIRST layout (slot 0 = single node 0 with P0 = 1/Y0
# in place and carry 1; doubles 1..17 on slots (2a-1, 2a), all with the v6 normalisation; the single step = one J_A[2a]
# half; second-slot geometry word sqrt(k) sqrt(G') + sqrt(G); seed bit [P34 = 0] xor F33 from one zero test at slot 34;
# head ripple on slots 31..17). Models: src/dqi_end/sf_model.py, src/dqi_int/sf6_model.py.
# Modifications 2026-11-16 by lane dqi_close (v7): the regular return node pays the quotient debts of both divided
# targets (d/n, e/n) with ONE selected-parity quotient phase (84 T instead of 2 x 84), as in Syed Asad Ali's compiled
# v13 return (decoded in runs/20261116T010637Z-dqi-close/LANE.md). Functions touched: restore_multi, quotient_phase_multi (new).
# Lineage starting from Syed Asad Ali. Installed at runtime on top of the unchanged v12 source (v7_pipeline), like the
# extractor-cutoff wrapper of Ertugrul Ozer. Word-level reference: src/dqi_pair/confluent_model.py (extractor_e).
"""Install with install(V7) after V7.configure(). Then V7.emit(...) builds the confluent decoder."""
import sys
import kickmix as km

JMIN = 17
import os as _os
USE_JA = True   # J_A per s (ja_terms.py; 198 fallback where no public kernel)
NODE0_INVERSE = True   # node 0 first head P = 1/Y by an in-place inverse (d = 1)
RET_JB = True   # return node: J_B for the d1 multiply-back + sqrt(b) n (kernel_flip, change 2)
USE_JB = True   # public joint kernel J_B (jb_terms.py); False = separate 84 + 99 products
NEWNORM = True   # nodes 1..16: shared-norm two-target division + in-place inverse second slot (no g test)
MERGED_QPHASE = _os.environ.get('DQI_MERGED_QPHASE', '1') == '1'   # lane dqi_close v7: one quotient phase per return node
NEG_DROP = False   # set by component.py mode extrtneg (negative control)
# lane x_dqiheads 2026-11-20: hoisted prefix (stage A, J = 3 analogue; mechanism credit ThemBones, Apache-2.0):
# for these new double nodes the single step and the 'A' half of old double 1 run as plain queries; their e terms
# are added in one block A_a * Y_a + (s1, 0) on the raw words (order ORDER_a of lane F_dqi5, model hoist3_model.py).
HOIST_NODES = tuple(range(2, 17))
STAGE_B = True   # J = 4: also the 'B' half of old double 1 is a plain query; block = hoist_block4 (lane F_dqi8)
ALIGNED = (7, 8, 9, 10, 11, 12, 13, 14, 15, 16)   # driver's aligned_native chart nodes
# (I1) node 1's carry R_1 = kappa_{0,1} + P0(alpha_1) PA_1(alpha_1) is X-measured at the top of node 2 (bilinear phase
# paid), node 2 runs with carry 1 (no scale-in); the return rebuilds R_1 with one K product before node 1's flip_out.
CARRY_ERASE = True
SKIP_SLOT17 = True   # no tail test at slot 17 (t = 17 is already a declared failure: key fails at t = 17 by design)
SLOT_NODE = tuple([0] + [a for a in range(1, 17) for _ in (0, 1)])   # v8: slots 0..32; 33 = x^2 at 0, 34 = infinity
F = km.GF2Field(12)
DELTA = 2048


def _sqrt(x):
    return F.pow(x, 2048) if x else 0


def _kappa(i):
    t = 2 * i
    return DELTA ^ F.mul(t, t) ^ t


def _kmul(a, b):
    a0, a1, b0, b1 = a & 4095, a >> 12, b & 4095, b >> 12
    aa, bb = F.mul(a0, b0), F.mul(a1, b1)
    return (aa ^ F.mul(DELTA, bb)) | ((F.mul(a0 ^ a1, b0 ^ b1) ^ aa) << 12)


def _ksqrt(x):
    y1 = _sqrt(x >> 12)
    return _sqrt((x & 4095) ^ F.mul(DELTA, F.mul(y1, y1))) | (y1 << 12)


def _ksquare(x):
    x0, x1 = x & 4095, x >> 12
    return (F.mul(x0, x0) ^ F.mul(DELTA, F.mul(x1, x1))) | (F.mul(x1, x1) << 12)


def _alpha(i):
    return (2 * i) | (1 << 12)


# ---------------- geometry ----------------
def confluent_U():
    U = [1]
    for s in range(33):
        k = _kappa(SLOT_NODE[s]); out = [0] * (len(U) + 2)
        for j, c in enumerate(U):
            out[j] ^= F.mul(c, k); out[j + 1] ^= c; out[j + 2] ^= c
        U = out
    U = [0, 0] + U                                   # v8: times x^2 (slot 33); slot 34 = 2 conditions at infinity
    assert len(U) == 69 and U[-1] == 1
    return U


def _gf2_inverse_columns(columns, n):
    rows = [0] * n                                   # rows[i] = bitmask over inputs
    for j, col in enumerate(columns):
        for i in range(n):
            if col >> i & 1: rows[i] |= 1 << j
    aug = [(rows[i], 1 << i) for i in range(n)]
    for c in range(n):
        p = next(i for i in range(c, n) if aug[i][0] >> c & 1)
        aug[c], aug[p] = aug[p], aug[c]
        for i in range(n):
            if i != c and aug[i][0] >> c & 1:
                aug[i] = (aug[i][0] ^ aug[c][0], aug[i][1] ^ aug[c][1])
    inv_rows = [aug[i][1] for i in range(n)]       # inverse matrix rows
    return [sum((inv_rows[i] >> j & 1) << i for i in range(n)) for j in range(n)]


def confluent_geometry_factory(rows_from_columns):
    cache = {}

    def geometry():
        if cache: return cache['spec']
        U = confluent_U()
        V, Dv = {}, {}
        LU = len(U)
        for a in range(17):
            al = _alpha(a); pw = [1]
            for _ in range(70): pw.append(_kmul(pw[-1], al))
            for r in range(1, 71):
                v = d = 0
                for j in range(max(0, LU - r)):
                    v ^= _kmul(U[j + r], pw[j])
                    if j % 2: d ^= _kmul(U[j + r], pw[j - 1])
                V[a, r], Dv[a, r] = v, d
        columns = []
        pi0, sg0 = 1, 0
        for s in range(33):
            ki = F.invert(_kappa(SLOT_NODE[s])); pi0 = F.mul(pi0, ki); sg0 ^= ki
        SP0, SS0 = _sqrt(pi0), _sqrt(sg0)
        for k in range(70):                          # input register S_{k+1}
            r = k + 1
            for bit in range(12):
                c = 1 << bit; out = 0
                for s in range(33):
                    a = SLOT_NODE[s]
                    first = s == 0 or (s % 2 == 1)
                    if first:
                        val = _kmul(c, V[a, r])
                    else:   # single-first e-start: sqrt(k) sqrt(G'(alpha)) + sqrt(G(alpha)), k = q_0(alpha_a)
                        rk = _sqrt(_kappa(0) ^ _kappa(a))
                        val = _kmul(rk, _kmul(_sqrt(c), _ksqrt(Dv[a, r]))) ^ _ksqrt(_kmul(c, V[a, r]))
                    out |= val << (24 * s)
                Ux = lambda i: U[i] if 0 <= i < LU else 0
                out |= F.mul(c, Ux(r)) << 792                                   # S66 = G0
                out |= F.mul(SP0, _sqrt(F.mul(c, Ux(r + 1))) ^ F.mul(SS0, _sqrt(F.mul(c, Ux(r))))) << 804   # S67
                out |= F.mul(c, Ux(r - 1)) << 816                               # S68 = f1
                out |= (_sqrt(F.mul(c, Ux(r - 2))) ^ _sqrt(F.mul(c, Ux(r - 1)))) << 828   # S69
                columns.append(out)
        inv_columns = _gf2_inverse_columns(columns, 840)
        cache['spec'] = dict(U=tuple(U), field_matrix=None, forward_rows=rows_from_columns(columns),
                             inverse_rows=rows_from_columns(inv_columns), confluent=True, slot_node=SLOT_NODE)
        return cache['spec']
    return geometry


# ---------------- tail (seed interface of rolling_tail_early) ----------------
class ConfTail:
    def __init__(self, builder, Tail):
        self.b, self.T = builder, Tail
        self.current = None; self.seed_mask = None; self.released = False; self.resumed = False

    def release_spare(self):
        self.released = True

    def seed_prefix(self, numerator_constant, denominator_x):
        assert self.released and self.seed_mask is None and self.current is not None
        self.b.cswap(self.current, numerator_constant, denominator_x)
        self.seed_mask = self.b.alloc_bits(1)
        self.b.hmr(km.array([self.current]), self.seed_mask)
        self.b.free(km.array([self.current]))
        self.current = None

    def seed_return(self, numerator_constant, denominator_x):
        assert self.current is None and self.seed_mask is not None
        self.current = self.b.alloc_qubits(1)[0]
        self.T.zero_xor(self.b, numerator_constant, self.current)
        self.b.cz(self.seed_mask[0], self.current)
        self.b.free(self.seed_mask)
        self.seed_mask = None
        self.b.cswap(self.current, numerator_constant, denominator_x)

    def resume_return(self):
        self.resumed = True


def restore_d1_premultiplied(Last, builder, source, target, record, product):
    """last_return_retained_norm.restore_with_shared_norm (Syed Asad Ali, Apache-2.0), no-next path, with the
    multiply-back source*target already XORed into the fresh 24-wire register `product` (by the J_B kernel that also
    emits the node's sqrt(b) n term). Same mask ABI and phase payments as the original."""
    from tower_inverse import init_norm, phase_product
    A, Original = Last.A, Last.Original
    assert record.builder_id == id(builder) and not record.closed
    assert tuple(source) == record.source and tuple(target) == record.target and record.delta == 2048
    delta = record.delta
    builder.swap(target, product)
    mask = builder.alloc_bits(24)
    builder.hmr(product, mask)
    builder.free(product)
    head_return = A.make_record(builder, mask, A.tensor24(delta), delta, False)
    inverse_norm = init_norm(builder, source[:12], source[12:], delta)
    norm_masks, child = Last.inverse_twelve_keep_child(builder, inverse_norm)
    A._repay_norm_source_masks(builder, source, norm_masks, delta)
    builder.cz(record.old_target_mask, target)
    builder.free(record.old_target_mask)
    builder.cx(source[12:], source[:12])
    phase_product(builder, source, target,
                  km.array([*record.adjoint_masks[0], *record.adjoint_masks[1]]), A.tensor24(delta))
    builder.cx(source[12:], source[:12])
    for m in record.adjoint_masks:
        builder.free(m)
    builder.cz(record.inverse_norm_mask, inverse_norm)
    builder.free(record.inverse_norm_mask)
    Original._quotient_phase_with_norm(builder, source, inverse_norm, target, head_return.old_target_mask, delta)
    A.free_product_mask(builder, head_return)
    Last._repay_inverse_and_child(builder, source, inverse_norm, child, delta)
    record.closed = True


def divide_two(Original, builder, source, t1, t2, delta=2048):
    """direct_carry_arithmetic.divide_deferred (Syed Asad Ali, Apache-2.0) for TWO targets sharing one 1/N(u):
    t1 <- t1/u, t2 <- t2/u, u kept. Two DivisionRecords; the inverse-norm mask is carried by the first only."""
    o1 = Original._adjoint_consume(builder, source, t1, delta)
    o2 = Original._adjoint_consume(builder, source, t2, delta)
    norm = Original._inverse_norm(builder, source, delta)
    a1 = Original._consume_halves(builder, norm, t1)
    a2 = Original._consume_halves(builder, norm, t2)
    m = builder.alloc_bits(12); builder.hmr(norm, m); builder.free(norm)
    R = Original.DivisionRecord
    return (R(id(builder), tuple(source), tuple(t1), o1, a1, m, delta),
            R(id(builder), tuple(source), tuple(t2), o2, a2, None, delta))


def restore_multi(Original, builder, source, targets, next_words, next_records):
    """restore_two (Syed Asad Ali's restore_with_shared_norm, Apache-2.0, extended) for several divided targets
    [(word, DivisionRecord)] and pending next words u*Y, all sharing one inverse norm of u."""
    A = Original.A
    from tower_inverse import init_norm, erase_norm, phase_product, kernel
    delta = targets[0][1].delta
    for t, r in targets:
        assert r.builder_id == id(builder) and not r.closed and tuple(source) == r.source and tuple(t) == r.target
    heads = [A.emit_prefix(builder, source, t, delta) for t, _ in targets]
    olds = [Original._adjoint_consume(builder, source, w, delta) for w in next_words]
    inverse_norm = Original._inverse_norm(builder, source, delta)
    adjs = [Original._consume_halves(builder, inverse_norm, w) for w in next_words]
    for (t, r), hr in zip(targets, heads):
        builder.cz(r.old_target_mask, t); builder.free(r.old_target_mask)
        builder.cx(source[12:], source[:12])
        phase_product(builder, source, t, km.array([*r.adjoint_masks[0], *r.adjoint_masks[1]]), A.tensor24(delta))
        builder.cx(source[12:], source[:12])
        for mask in r.adjoint_masks:
            builder.free(mask)
        if r.inverse_norm_mask is not None:
            builder.cz(r.inverse_norm_mask, inverse_norm); builder.free(r.inverse_norm_mask)
        if not MERGED_QPHASE:
            Original._quotient_phase_with_norm(builder, source, inverse_norm, t, hr.old_target_mask, delta)
            A.free_product_mask(builder, hr)
        r.closed = True
    if MERGED_QPHASE:   # one quotient phase for all targets (as the public v13 return): dot(m_i, t_i/u) summed
        quotient_phase_multi(Original, builder, source, inverse_norm,
                             [(t, hr.old_target_mask) for (t, _), hr in zip(targets, heads)], delta)
        for hr in heads:
            A.free_product_mask(builder, hr)
    for w, old, rec in zip(next_words, olds, next_records):
        phase_product(builder, source, w, old, A.tensor24(delta))
        builder.free(old)
        A.repay_product_input(builder, w, rec)
    inverse_mask = builder.alloc_bits(12)
    builder.hmr(inverse_norm, inverse_mask)
    builder.free(inverse_norm)
    norm = init_norm(builder, source[:12], source[12:], delta)
    Original.Phase12.phase_inverse_twelve_polynomial(builder, norm, inverse_mask)
    builder.free(inverse_mask)
    for w, adj in zip(next_words, adjs):
        for half, mask in zip((w[:12], w[12:]), adj):
            phase_product(builder, norm, half, mask, kernel(12))
            builder.free(mask)
    erase_norm(builder, source[:12], source[12:], norm, delta)
    builder.free(norm)


def quotient_phase_multi(Original, builder, source, reciprocal_norm, pairs, delta):
    """direct_carry_arithmetic._quotient_phase_with_norm (Syed Asad Ali, Apache-2.0) for SEVERAL targets sharing the
    unit u and its live 1/N(u): applies sum_i dot(mask_i, t_i/u) with 84 T in all (the selected-parity CCZ runs over
    all target words at once; the phase is linear in the target). Lane dqi_close, after the public v13 return."""
    A, Narrow, parity_pivot, kernel = Original.A, Original.Narrow, Original.parity_pivot, Original.kernel
    assert len(source) == 24 and len(reciprocal_norm) == 12 and pairs
    assert all(len(t) == len(m) == 24 for t, m in pairs)
    if NEG_DROP: pairs = pairs[:1]   # negative control only: second target's debt left unpaid
    words = tuple(t for t, _ in pairs)
    for component, half in ((0, source[12:]), (1, source[:12])):
        for first_form, second_form, weight in kernel(12):
            first = parity_pivot(builder, reciprocal_norm, first_form)
            second = parity_pivot(builder, half, second_form)
            rows = A._component_mask_rows(delta, component, weight)
            coefficients = []
            for _, mask in pairs:
                c = A._classical_word(builder, 24)
                for bit, row in enumerate(rows):
                    for k in range(24):
                        if row >> k & 1:
                            builder.cx(mask[k], c[bit])
                coefficients.append(c)
            Narrow._selected_parity_ccz(builder, first, second, words, km.array([x for c in coefficients for x in c]))
            for c in coefficients:
                builder.free(c)
            parity_pivot(builder, half, second_form)
            parity_pivot(builder, reciprocal_norm, first_form)


def restore_two(Original, builder, source, target, record, next_words, next_records):
    """direct_carry_arithmetic.restore_with_shared_norm (Syed Asad Ali, Apache-2.0) extended to TWO pending next words
    u*Y1, u*Y2 sharing one inverse norm of u. Same mask ABI; each next word costs adjoint 99 + halves 84 + its phases."""
    A = Original.A
    from tower_inverse import init_norm, erase_norm, phase_product, kernel
    assert record.builder_id == id(builder) and not record.closed
    assert tuple(source) == record.source and tuple(target) == record.target
    delta = record.delta
    head_return = A.emit_prefix(builder, source, target, delta)
    olds = [Original._adjoint_consume(builder, source, w, delta) for w in next_words]
    inverse_norm = Original._inverse_norm(builder, source, delta)
    adjs = [Original._consume_halves(builder, inverse_norm, w) for w in next_words]
    builder.cz(record.old_target_mask, target)
    builder.free(record.old_target_mask)
    builder.cx(source[12:], source[:12])
    phase_product(builder, source, target,
                  km.array([*record.adjoint_masks[0], *record.adjoint_masks[1]]), A.tensor24(delta))
    builder.cx(source[12:], source[:12])
    for mask in record.adjoint_masks:
        builder.free(mask)
    builder.cz(record.inverse_norm_mask, inverse_norm)
    builder.free(record.inverse_norm_mask)
    Original._quotient_phase_with_norm(builder, source, inverse_norm, target, head_return.old_target_mask, delta)
    A.free_product_mask(builder, head_return)
    for w, old, rec in zip(next_words, olds, next_records):
        phase_product(builder, source, w, old, A.tensor24(delta))
        builder.free(old)
        A.repay_product_input(builder, w, rec)
    inverse_mask = builder.alloc_bits(12)
    builder.hmr(inverse_norm, inverse_mask)
    builder.free(inverse_norm)
    norm = init_norm(builder, source[:12], source[12:], delta)
    Original.Phase12.phase_inverse_twelve_polynomial(builder, norm, inverse_mask)
    builder.free(inverse_mask)
    for w, adj in zip(next_words, adjs):
        for half, mask in zip((w[:12], w[12:]), adj):
            phase_product(builder, norm, half, mask, kernel(12))
            builder.free(mask)
    erase_norm(builder, source[:12], source[12:], norm, delta)
    builder.free(norm)
    record.closed = True


class Ext:
    """Confluent extractor; heads stored in coefficient view at their node, carry = last unit."""

    def __init__(self, V7):
        P = V7.P
        self.A = P.Arithmetic
        self.Ar = P.Extractor.Arithmetic
        self.Original = P.DirectArithmetic
        self.Tail = P.Tail
        import raw_query_extractor as RQ
        from tower_inverse import apply_inplace_linear, rows_from_columns, xor_product, erase_product
        self.erase_product = erase_product
        from monic_forney import add_scaled
        self.RQ, self.lin, self.xp, self.add_scaled = RQ, apply_inplace_linear, xor_product, add_scaled
        r = rows_from_columns
        self.R_sqrt12 = r([_sqrt(1 << j) for j in range(12)])
        self.R_sq12 = r([F.mul(1 << j, 1 << j) for j in range(12)])
        self.R_ksqrt = r([_ksqrt(1 << j) for j in range(24)])
        self.R_ksq = r([_ksquare(1 << j) for j in range(24)])

    # linear helpers
    def sqrt12(self, w): self.lin(self.b, w, self.R_sqrt12)
    def sq12(self, w): self.lin(self.b, w, self.R_sq12)

    def fxk(self, s12, n, e):                        # e ^= s * n   (s in F, n in K): 2 x 42 T
        self.xp(self.b, s12, n[:12], e[:12]); self.xp(self.b, s12, n[12:], e[12:])

    def a_term(self, PA, n, e):                      # e ^= sqrt(c1_A) n
        self.sqrt12(PA[12:]); self.fxk(PA[12:], n, e); self.sq12(PA[12:])

    def b_term(self, PB, n, e, g0):                  # e ^= (sqrt c0 + g0 sqrt c1 + sqrt c1 th) n
        self.sqrt12(PB[:12]); self.sqrt12(PB[12:]); self.add_scaled(self.b, PB[12:], PB[:12], g0)
        self.A.product(self.b, PB, n, e)
        self.add_scaled(self.b, PB[12:], PB[:12], g0); self.sq12(PB[12:]); self.sq12(PB[:12])

    @staticmethod
    def g0(a, b):
        return _sqrt((2 * a) ^ _kappa(a) ^ _kappa(b) ^ DELTA)

    def zero(self, word, flag):
        self.Tail.zero_xor(self.b, word, flag)

    def hmr_flag(self, q):                           # X-measure a flag wire; returns its 1-bit mask (phase debt)
        m = self.b.alloc_bits(1); self.b.hmr(km.array([q]), m); self.b.free(km.array([q]))
        return m

    def pay(self, m, q):                             # pay (-1)^(m . q) with q holding the debt's predicate again
        self.b.cz(m[0], q); self.b.free(m)

    def prev_flag(self, E, head_word, mE, rz=None):
        """Return: Eprev = E and zero(head) (= f_{s-2}); pay the forward HMR debt of f_{s-2} on it. The witness
        z = zero(head) = g_{s-1} is X-measured; its mask is paid at node a-1's second-slot zero(carry) query."""
        Ep = self.b.alloc_qubits(1)[0]; z = self.b.alloc_qubits(1)[0]
        self.zero(head_word, z); self.b.ccx(E, z, Ep); self.pay(mE, Ep)
        if rz is not None: self.pay(rz, z)   # the head ripple's debt on the same predicate [head = 0]
        return Ep, self.hmr_flag(z)

    def joint_half(self, kind, head, n, d, e, b, a, reverse=False):
        """One half step of an old double node in the square-root domain (e = sqrt of the Wronskian):
        kind 'A': e ^= sqrt(c1) n, then the query (n, d) <- ((d + P(alpha_a) n)/kappa, n);
        kind 'B': e ^= (sqrt c0 + g0 sqrt c1 + sqrt c1 theta) n, then the query.  Reverse: query back, same e term.
        Stage A emits the two products separately (A: 84 + 99, B: 99 + 99); a joint kernel can replace this call."""
        q = self.RQ.query_step
        if kind == 'A' and USE_JB:
            from field_tensor import accumulate_product
            import jb_terms
            kp = _kappa(b) ^ _kappa(a)
            nv = self.RQ.node_view
            if not reverse:
                nv(self.b, head, a); accumulate_product(self.b, head, n, km.array([*d, *e]), jb_terms.TERMS); nv(self.b, head, a)
                self.RQ.public_scale(self.b, d, F.invert(kp)); self.b.swap(n, d)
            else:
                self.b.swap(n, d); self.RQ.public_scale(self.b, d, kp)
                nv(self.b, head, a); accumulate_product(self.b, head, n, km.array([*d, *e]), jb_terms.TERMS); nv(self.b, head, a)
            return
        if kind == 'B' and USE_JA:
            from field_tensor import accumulate_product
            import ja_terms
            kp = _kappa(b) ^ _kappa(a)
            terms = ja_terms.TERMS[str((2 * a) ^ (2 * b))]
            nv = self.RQ.node_view
            if not reverse:
                nv(self.b, head, a); accumulate_product(self.b, head, n, km.array([*d, *e]), terms); nv(self.b, head, a)
                self.RQ.public_scale(self.b, d, F.invert(kp)); self.b.swap(n, d)
            else:
                self.b.swap(n, d); self.RQ.public_scale(self.b, d, kp)
                nv(self.b, head, a); accumulate_product(self.b, head, n, km.array([*d, *e]), terms); nv(self.b, head, a)
            return
        term = (lambda: self.a_term(head, n, e)) if kind == 'A' else (lambda: self.b_term(head, n, e, self.g0(a, b)))
        if not reverse:
            term(); q(self.b, head, n, d, b, a)
        else:
            q(self.b, head, n, d, b, a, True); term()

    def half(self, kind, head, n, d, e, b, a, reverse=False):
        if a in HOIST_NODES and ((kind == 'B' and b == 0) or (b == 1 and (kind == 'A' or STAGE_B))):
            return self.plain_query(head, n, d, b, a, reverse)   # lane x_dqiheads: e term hoisted into hoist_block
        if a in HOIST_NODES and a in ALIGNED and kind == 'B' and b == 1:
            # chart entered after the two hoisted plain queries (the driver's initial chart update is skipped)
            if not reverse: self.chart_enter(n, e, d, a, 1)
            r = self.joint_half(kind, head, n, d, e, b, a, reverse)
            if reverse: self.chart_enter(n, e, d, a, 1)
            return r
        return self.joint_half(kind, head, n, d, e, b, a, reverse)

    def _patch_aligned(self):
        m = globals().get('aligned')
        if m is not None and not hasattr(m, '_orig_update'):
            m._orig_update = orig = m.update
            def update(ex, n, e, d, a, initial):
                if initial and a in HOIST_NODES: return
                return orig(ex, n, e, d, a, initial)
            m.update = update

    def chart_enter(self, n, e, d, a, j):
        """e ^= sqrt(kap a ^ kap j) * L_c(n d): the aligned chart term between the halves of old double j
        (lane F_dqi8's derivation; same gates as aligned_native.update). Self-inverse."""
        from field_tensor import accumulate_product
        al = globals()['aligned']; c = al.make(a); sk = al.F.sqrt(al.kap(a) ^ al.kap(j))
        def res(v):
            t = al.F.ksqrt(al.un(v)); return al.pack(al.sc(al.plus(al.F.kmul(c['c'], t), al.F.kmul(c['d'], al.cj(t))), sk))
        accumulate_product(self.b, n, d, e, [(u, v, w) for u, v, w in ((u, v, res(w)) for u, v, w in self.A.tensor24(2048)) if w])

    def plain_query(self, head, n, d, b, a, reverse):
        """(n, d) <- ((d + P(alpha_a) n)/kappa, n): the d part of the joint kernels, no e term (99 T)."""
        kp = _kappa(b) ^ _kappa(a); nv = self.RQ.node_view
        if not reverse:
            nv(self.b, head, a); self.A.product(self.b, head, n, d); nv(self.b, head, a)
            self.RQ.public_scale(self.b, d, F.invert(kp)); self.b.swap(n, d)
        else:
            self.b.swap(n, d); self.RQ.public_scale(self.b, d, kp)
            nv(self.b, head, a); self.A.product(self.b, head, n, d); nv(self.b, head, a)

    def hoist_block(self, words, carry, reverse):
        if STAGE_B:
            self._patch_aligned(); return self.hoist_block4(words, carry, reverse)   # supplied by lane F_dqi8
        """e_geo(a) ^= A_a Y_a + (s1, 0) for a in HOIST_NODES, A_a = x0(alpha_a) + s1 P0(alpha_a), s1 = sqrt(c1 of PA_1).
        words[0] = P0, words[1] = PA_1 in coefficient view. Forward: top of node 2 (all raw). Reverse: top of node 1's
        return, node 2 still scaled by the carry: there the constant is s1 x carry (84 T) instead of a CNOT."""
        b = self.b; P0, s1 = words[0], words[1][12:]
        self._patch_aligned()
        self.sqrt12(s1)
        W = b.alloc_qubits(24)
        self.xp(b, s1, P0[:12], W[:12]); self.xp(b, s1, P0[12:], W[12:])
        for a in HOIST_NODES:
            Y, e = words[2 * a - 1], words[2 * a]; g0 = self.g0(a, 0)
            self.add_scaled(b, W[12:], W[:12], 2 * a)
            self.sqrt12(P0[:12]); self.sqrt12(P0[12:]); self.add_scaled(b, P0[12:], P0[:12], g0)
            b.cx(P0, W)
            self.A.product(b, W, Y, e)
            b.cx(P0, W)
            self.add_scaled(b, P0[12:], P0[:12], g0); self.sq12(P0[12:]); self.sq12(P0[:12])
            self.add_scaled(b, W[12:], W[:12], 2 * a)
            if reverse and a == 2 and not CARRY_ERASE:
                self.fxk(s1, carry, e)
            else:
                b.cx(s1, e[:12])
        self.erase_product(b, s1, P0[:12], W[:12]); self.erase_product(b, s1, P0[12:], W[12:])
        b.free(W)
        self.sq12(s1)

    # ---- lane F_dqi8 2026-11-20: stage B block (stageB/hoist_block4.py, unit-tested in the official simulator)
    def _hb4_coeffs(self, a):
        """Packed K constants c_p(a) = l_p(alpha_a) / kappa_{1,a}, p = 0, 1, 2 (Lagrange basis on the points 0, 1, 2) and
        c_inf(a) = alpha_a (alpha_a + 1)(alpha_a + 2) / kappa_{1,a};  alpha_a = 2a + theta."""
        al = lambda r: ((2 * a) ^ r) | (1 << 12)
        ki = F.invert(_kappa(1) ^ _kappa(a))
        ks = lambda x, s: F.mul(x & 4095, s) | (F.mul(x >> 12, s) << 12)
        out = {}
        for p in (0, 1, 2):
            num, den = 1, 1
            for r in (0, 1, 2):
                if r != p:
                    num = _kmul(num, al(r)); den = F.mul(den, p ^ r)
            out[p] = ks(num, F.mul(ki, F.invert(den)))
        out['inf'] = ks(_kmul(_kmul(al(0), al(1)), al(2)), ki)
        return out


    def hoist_block4(self, words, carry, reverse):
        from tower_inverse import rows_from_columns
        b = self.b
        p0w, p1w = words[0][:12], words[0][12:]          # P0   = p0 + p1 z
        a0w, a1w = words[1][:12], words[1][12:]          # PA_1 = a0 + a1 z
        b0w, b1w = words[2][:12], words[2][12:]          # PB_1 = b0 + b1 z
        k0, k1 = _kappa(0), _kappa(1); sk0, sk1 = _sqrt(k0), _sqrt(k1)
        q = lambda i, p: F.mul(p, p) ^ p ^ _kappa(i)      # q_i at an F point
        cf = {a: self._hb4_coeffs(a) for a in HOIST_NODES}

        def viewB(p, on):      # PB.lo <-> xB1(p) = sqrt b0 + (sqrt kappa_1 + p) sqrt b1 ; PB.hi <-> sqrt b1
            if on:
                self.sqrt12(b0w); self.sqrt12(b1w); self.add_scaled(b, b1w, b0w, sk1 ^ p)
            else:
                self.add_scaled(b, b1w, b0w, sk1 ^ p); self.sq12(b1w); self.sq12(b0w)

        def viewA(p):          # involution: PA.lo <-> PA_1(p) = a0 + p a1
            self.add_scaled(b, a1w, a0w, p)

        def viewP(p):          # involution: P0.lo <-> P0(p) = p0 + p p1
            self.add_scaled(b, p1w, p0w, p)

        def s1_into(target, c):  # target ^= c * sqrt(a1)   (0 gates)
            self.sqrt12(a1w); self.add_scaled(b, a1w, target, c); self.sq12(a1w)

        def make_T(p):         # T ^= m'_p = xB1(p) PA_1(p) + q_1(p) s1      [viewB(p), viewA(p) on]   42
            self.xp(b, b0w, a0w, T); s1_into(T, q(1, p))

        def drop_T(p):         # erase T = m'_p                              [same views]               0
            s1_into(T, q(1, p)); self.erase_product(b, b0w, a0w, T)

        def lin_V(p, target):  # target ^= q_0(p) xB1(p) + q_1(p) x0(p)      [viewB(p) on]              0
            self.add_scaled(b, b0w, target, q(0, p))
            self.sqrt12(p0w); self.sqrt12(p1w); self.add_scaled(b, p1w, p0w, sk0 ^ p)
            self.add_scaled(b, p0w, target, q(1, p))
            self.add_scaled(b, p1w, p0w, sk0 ^ p); self.sq12(p1w); self.sq12(p0w)

        def shareB(p):         # e_a ^= c_p(a) * m'_p for every hoisted node  [T = m'_p live]            0
            for a in HOIST_NODES:
                e = words[2 * a]; c = cf[a][p]
                self.add_scaled(b, T, e[:12], c & 4095); self.add_scaled(b, T, e[12:], c >> 12)

        def make_Tinf():       # T ^= s1 + sqrt(b1) a1                                                  42
            self.sqrt12(b1w); self.xp(b, b1w, a1w, T); self.sq12(b1w); s1_into(T, 1)

        def drop_Tinf():       # erase T = s1 + sqrt(b1) a1                                              0
            s1_into(T, 1); self.sqrt12(b1w); self.erase_product(b, b1w, a1w, T); self.sq12(b1w)

        def lin_Vinf(target):  # target ^= sqrt(p1) + sqrt(b1)                                           0
            self.sqrt12(p1w); b.cx(p1w, target); self.sq12(p1w)
            self.sqrt12(b1w); b.cx(b1w, target); self.sq12(b1w)

        cs = F.mul(k1, sk0)                                # Nm(0) = cs sqrt(p1) + k1 sqrt(p0) + k0 xB1(0) + m'_0 p0
        R_cs = rows_from_columns([F.mul(cs, 1 << j) for j in range(12)])
        R_csi = rows_from_columns([F.mul(F.invert(cs), 1 << j) for j in range(12)])

        def inplace0(forward):  # P0.hi: p1 <-> Nm(0)      [viewB(0) on, T = m'_0 live; P0.lo = p0 is not changed]   42
            if forward:
                self.sqrt12(p1w); self.lin(b, p1w, R_cs)
                self.sqrt12(p0w); self.add_scaled(b, p0w, p1w, k1); self.sq12(p0w)
                self.add_scaled(b, b0w, p1w, k0)
                self.xp(b, T, p0w, p1w)
            else:
                self.xp(b, T, p0w, p1w)
                self.add_scaled(b, b0w, p1w, k0)
                self.sqrt12(p0w); self.add_scaled(b, p0w, p1w, k1); self.sq12(p0w)
                self.lin(b, p1w, R_csi); self.sq12(p1w)

        def mix_rows(c1, c2, inverse):   # 24-wire map (V1, V2) -> c1 V1 + c2 V2 as a K word (lo, hi), or its inverse
            m00, m01, m10, m11 = c1 & 4095, c2 & 4095, c1 >> 12, c2 >> 12
            if inverse:
                di = F.invert(F.mul(m00, m11) ^ F.mul(m01, m10))
                m00, m01, m10, m11 = F.mul(m11, di), F.mul(m01, di), F.mul(m10, di), F.mul(m00, di)
            return rows_from_columns([F.mul(m00, 1 << j) | (F.mul(m10, 1 << j) << 12) for j in range(12)] +
                                     [F.mul(m01, 1 << j) | (F.mul(m11, 1 << j) << 12) for j in range(12)])

        # ---- step 0: workspace.  live 864 -> 888 (peak of the block)
        b.x(carry[0])                                      # carry: K one -> 24 zero wires
        V = {1: carry[:12], 2: carry[12:]}                 # V1 = Nm(1), V2 = Nm(2)
        Wk = b.alloc_qubits(24); V3, T = Wk[:12], Wk[12:]   # V3 = leading coefficient of Nm, T = m' temporary
        # ---- step 1: values at p = 1, 2 (2 x 84 gates).  live 888
        for p in (1, 2):
            viewB(p, True); viewA(p)
            make_T(p); shareB(p)
            lin_V(p, V[p])
            viewP(p); self.xp(b, T, p0w, V[p]); viewP(p)
            drop_T(p)
            viewA(p); viewB(p, False)
        # ---- step 2: leading coefficient Nm_inf = sqrt(p1) + sqrt(b1) + (s1 + sqrt(b1) a1) p1 (84 gates).  live 888
        make_Tinf(); lin_Vinf(V3); self.xp(b, T, p1w, V3); drop_Tinf()
        # ---- step 3: p = 0 IN PLACE in head 0's c1 word (84 gates); built last, undone first.  live 888
        viewB(0, True); make_T(0); shareB(0); inplace0(True); drop_T(0); viewB(0, False)
        # ---- step 4: one K product per hoisted node (99 each).  live 888
        for a in HOIST_NODES:
            Y, e = words[2 * a - 1], words[2 * a]; c = cf[a]
            self.lin(b, carry, mix_rows(c[1], c[2], False))
            for src, cc in ((p1w, c[0]), (V3, c['inf'])):
                self.add_scaled(b, src, carry[:12], cc & 4095); self.add_scaled(b, src, carry[12:], cc >> 12)
            self.A.product(b, carry, Y, e)                 # e ^= (Nm(alpha_a) / kappa_{1,a}) * Y_a
            for src, cc in ((p1w, c[0]), (V3, c['inf'])):
                self.add_scaled(b, src, carry[:12], cc & 4095); self.add_scaled(b, src, carry[12:], cc >> 12)
            self.lin(b, carry, mix_rows(c[1], c[2], True))
        # ---- step 5: undo p = 0 (84 gates).  live 888
        viewB(0, True); make_T(0); inplace0(False); drop_T(0); viewB(0, False)
        # ---- step 6: erase V3, V2, V1 (3 x 42 gates).  live 888 -> 864
        make_Tinf(); lin_Vinf(V3); self.erase_product(b, T, p1w, V3); drop_Tinf()
        for p in (2, 1):
            viewB(p, True); viewA(p)
            make_T(p); lin_V(p, V[p])
            viewP(p); self.erase_product(b, T, p0w, V[p]); viewP(p)
            drop_T(p)
            viewA(p); viewB(p, False)
        b.free(Wk)
        b.x(carry[0])                                      # carry = K one again

    def carry_term(self, words):
        """Yield-free helper: node views of P0 and PA_1 at alpha_1 (involutions)."""
        self.RQ.node_view(self.b, words[0], 1); self.RQ.node_view(self.b, words[1], 1)

    def carry_erase(self, words, carry):
        b = self.b; k = _kappa(0) ^ _kappa(1)
        self.carry_term(words)
        for i in range(12):
            if k >> i & 1: b.x(carry[i])
        m = b.alloc_bits(24); b.hmr(carry, m)
        from tower_inverse import phase_product
        phase_product(b, words[0], words[1], m, self.A.tensor24(DELTA))
        b.free(m)
        self.carry_term(words)
        b.x(carry[0])

    def carry_rebuild(self, words, carry):
        b = self.b; k = _kappa(0) ^ _kappa(1)
        b.x(carry[0])
        self.carry_term(words)
        self.A.product(b, words[0], words[1], carry)
        for i in range(12):
            if k >> i & 1: b.x(carry[i])
        self.carry_term(words)

    def old_double(self, words, b, a, W1, W2, carry, reverse=False):
        PA, PB = words[2 * b - 1], words[2 * b]
        kp = _kappa(b) ^ _kappa(a)
        chart = STAGE_B and b == 1 and a in HOIST_NODES and a in ALIGNED
        if not reverse:
            self.half('A', PA, W1, carry, W2, b, a)
            self.half('B', PB, W1, carry, W2, b, a)
            self.RQ.public_scale(self.b, W2, F.invert(kp))
            if chart: globals()['aligned']._orig_update(self, W1, W2, carry, a, False)
        else:
            if chart: globals()['aligned']._orig_update(self, W1, W2, carry, a, False)
            self.RQ.public_scale(self.b, W2, kp)
            self.half('B', PB, W1, carry, W2, b, a, True)
            self.half('A', PA, W1, carry, W2, b, a, True)

    FIRST_TEST = 19   # first-slot tail tests at 19, 21, .., 33 (t = 17 is a declared failure)

    def single(self, words, a, W1, W2, carry, reverse=False):
        kp = _kappa(0) ^ _kappa(a)
        if not reverse:
            self.half('B', words[0], W1, carry, W2, 0, a)
            self.RQ.public_scale(self.b, W2, F.invert(kp))
        else:
            self.RQ.public_scale(self.b, W2, kp)
            self.half('B', words[0], W1, carry, W2, 0, a, True)

    def prefix(self, builder, words, carry, stage=lambda _: None):
        self.b = b = builder
        A, Ar, nv = self.A, self.Ar, self.RQ.node_view
        rec = dict(in1={}, in2={}, d1={}, d2={}, flags={}, mE={}, mg={}, inv2={})
        rec['d1'][0] = A.inverse_deferred(b, words[0]); nv(b, words[0], 0)   # P0 = 1/Y0; carry stays 1
        stage('confluent_prefix_single_00')
        E = None
        for a in range(1, 17):
            s = 2 * a - 1; W1, W2 = words[s], words[s + 1]
            if a == 2 and CARRY_ERASE: self.carry_erase(words, carry)
            if a == 2 and HOIST_NODES: self.hoist_block(words, carry, False)
            if a in HOIST_NODES and a in ALIGNED:
                # lane F_dqi8: PLAIN scale-in at hoisted chart nodes. The driver's fused source cell (source_fusion_native,
                # 'if a>=7') also adds the initial chart term sqrt(kap a ^ kap 0) L_c(n d); the hoisted steps run outside the chart.
                rec['in1'][a] = A.emit_prefix(b, carry, W1); rec['in2'][a] = A.emit_prefix(b, carry, W2)
            elif a >= 3 or (a == 2 and not CARRY_ERASE):
                rec['in1'][a] = A.emit_prefix(b, carry, W1)
                rec['in2'][a] = A.emit_prefix(b, carry, W2)
            self.single(words, a, W1, W2, carry)
            for bb in range(1, a):
                self.old_double(words, bb, a, W1, W2, carry)
            if s >= self.FIRST_TEST:
                f = b.alloc_qubits(1)[0]; self.zero(W1, f); b.cswap(f, W1, carry)
                if E is not None:   # HMR f_{s-2}; phase paid where the return recomputes it (prev_flag)
                    rec['mE'][s] = self.hmr_flag(E)
                E = f
            # carry <- d/n, W2 <- e/n with one 1/N(n); W1 = n stays the unit
            rec['d1'][a], rec['d2'][a] = divide_two(self.Original, b, W1, carry, W2); b.swap(W1, carry)
            nv(b, W1, a)
            self.sqrt12(W1[12:]); b.cx(W1[12:], W2[:12]); self.sq12(W1[12:])   # W2 = x = e/n + sqrt(c1)
            rec['inv2'][a] = A.inverse_deferred(b, W2)                         # W2 = 1/x (0 -> 0)
            self.lin(b, W2, self.R_ksq); nv(b, W2, a)
            stage(f'confluent_prefix_node_{a:02d}')
        rec['E'] = E   # v8: f31 (the caller keeps it or X-measures it)
        return rec

    def closing(self, builder, words, carry, rec, stage=lambda _: None):
        self.b = b = builder
        A, Ar, nv = self.A, self.Ar, self.RQ.node_view
        E, mz = rec.pop('E'), rec.pop('mz', None)   # v8: E = f31, mz = the debt on [head 32 = 0] (or None)
        assert E is not None
        for a in reversed(range(1, 17)):
            s = 2 * a - 1; W1, W2 = words[s], words[s + 1]
            if a == 1 and HOIST_NODES: self.hoist_block(words, carry, True)
            if a == 1 and CARRY_ERASE: self.carry_rebuild(words, carry)
            # debts on [head(s+1) = 0] (chain witness z, ripple z): conditional zero phases on the stored head
            for m in (mz, rec.get('rz', {}).pop(s + 1, None)):
                if m is not None: self.Tail.zero_phase(b, W2, m[0]); b.free(m)
            mz = None
            nv(b, W2, a); self.lin(b, W2, self.R_ksqrt)
            A.inverse_closed(b, W2); A.repay_source_masks(b, W2, rec['inv2'][a])     # W2 = x
            self.sqrt12(W1[12:]); b.cx(W1[12:], W2[:12]); self.sq12(W1[12:])         # W2 = e/n
            nv(b, W1, a); b.swap(W1, carry)                                           # W1 = n, carry = d/n
            if a < 16 and not (a == 1 and CARRY_ERASE):
                nxt, nrec = [words[s + 2], words[s + 3]], [rec['in1'][a + 1], rec['in2'][a + 1]]
            else:
                nxt, nrec = [], []
            restore_multi(self.Original, b, W1, [(carry, rec['d1'][a]), (W2, rec['d2'][a])], nxt, nrec)
            if s >= self.FIRST_TEST:
                assert E is not None
                Eprev = None
                if s - 2 >= self.FIRST_TEST:
                    Eprev, mz = self.prev_flag(E, words[s - 1], rec['mE'][s], rec.get('rz', {}).pop(s - 1, None))
                b.cswap(E, W1, carry); self.Tail.erase_zero_flag(b, W1, E); b.free(km.array([E]))
                E = Eprev
            for bb in reversed(range(1, a)):
                self.old_double(words, bb, a, W1, W2, carry, reverse=True)
            self.single(words, a, W1, W2, carry, reverse=True)
            stage(f'confluent_return_node_{a:02d}')
        nv(b, words[0], 0); A.inverse_closed(b, words[0]); A.repay_source_masks(b, words[0], rec['d1'][0])
        stage('confluent_return_single_00')
        assert E is None and mz is None and not rec.get('rz')


def install(V7):
    P = V7.P
    from tower_inverse import rows_from_columns
    import public_geometry as Public
    import fused_crt_synthesis as Syn
    original_geometry = Public.geometry
    new_geometry = confluent_geometry_factory(rows_from_columns)
    for mod in list(sys.modules.values()):
        if mod is not None and getattr(mod, 'geometry', None) is original_geometry:
            mod.geometry = new_geometry
    original_node = Syn.node
    Syn.node = lambda i: original_node(SLOT_NODE[i]) if i < 35 else original_node(i)
    ext = Ext(V7)
    guard = Guard3(Syn, P.Tail, P.Arithmetic)
    Seed, Tail, Synthesis = P.Seed, P.Tail, P.Synthesis

    import endnode as EN
    SE = EN.SeqEnd(SLOT_NODE, Tail)

    def emit_key_prefix(builder, syndromes, *, j_min=15, stage=lambda _: None):
        # lane dqi_v9b: extractor nodes 0..16 (slots 0..32), v7 gauge, sequential end node (slots 33 = x^2 at 0,
        # 34 = infinity; endnode.SeqEnd), then the synthesis from i = 32 (state after r = 1 from the end node)
        assert len(syndromes) == 70
        Public.emit(builder, syndromes)
        heads = [km.array([*syndromes[2 * i], *syndromes[2 * i + 1]]) for i in range(33)]
        carry = builder.alloc_qubits(24)
        builder.x(carry[0])
        extraction = ext.prefix(builder, heads, carry, stage=stage)
        mE31 = ext.hmr_flag(extraction.pop('E'))
        gauge = Tail.gauge_prefix(builder, carry)
        N, D, endrec = SE.forward(builder, heads, *syndromes[66:70], carry[:12])
        end_out = (list(N), list(D))
        stage('end_node_prefix')
        synthesis = []
        for i in range(32, -1, -1):
            Pw = [heads[i][:12], heads[i][12:]]
            rec = Synthesis.emit_prefix(builder, N, D, Pw, i, guarded=False)
            synthesis.append((N, D, Pw, rec))
            N, D = D, N + Pw
            stage(dict(stage='synthesis_prefix', node=i, degree=len(D) - 1))
        assert len(N) == 35 and len(D) == 36
        return dict(builder_id=id(builder), syndromes=syndromes, heads=heads, carry=carry, extraction=extraction,
                    gauge=gauge, mE31=mE31, endrec=endrec, end_out=end_out, synthesis=synthesis, N=N, D=D,
                    closed=False)

    def emit_key_closing(builder, record, *, stage=lambda _: None):
        assert record['builder_id'] == id(builder) and not record['closed']
        heads, carry, extraction, gauge = record['heads'], record['carry'], record['extraction'], record['gauge']
        deferred = {}
        for old_N, old_D, old_P, rec in reversed(record['synthesis']):
            if RIPPLE and rec.node_index in RIPPLE_SLOTS:
                # native closing; the old-P mask is paid after head_ripple (the closing gets an all-zero mask)
                deferred[rec.node_index] = rec.pair_record.old_target_mask
                dummy = builder.alloc_bits(24); builder.bit_store(dummy, False)
                rec.pair_record.old_target_mask = dummy
            Synthesis.emit_closing(builder, old_N, old_D, old_P, rec)
        N0, D0 = record['end_out']

        def ripple(carrier):
            head_ripple(builder, Tail, list(heads) + [carrier], extraction.setdefault('rz', {}))
            from monic_forney import add_scaled
            for sl, mask in deferred.items():   # old-P masks are in the alpha view of the head (c0 + t c1, c1)
                t_, _ = Syn.node(sl); h = heads[sl]
                add_scaled(builder, h[12:], h[:12], t_); builder.cz(mask, h); add_scaled(builder, h[12:], h[:12], t_)
                builder.free(mask)

        (_, lam, _), (Ep, mz) = SE.reverse(builder, heads, N0, D0, record['endrec'], ext=ext, mE31=record['mE31'],
                                          ripple=ripple if RIPPLE else None)
        assert tuple(lam) == tuple(carry[:12])
        stage('end_node_return')
        Tail.gauge_return(builder, carry, gauge)
        extraction['E'] = Ep; extraction['mz'] = mz
        ext.closing(builder, heads, carry, extraction, stage=stage)
        builder.x(carry[0])
        builder.free(carry)
        Public.emit(builder, record['syndromes'], True)
        record['closed'] = True

    V7.emit_key_prefix = emit_key_prefix
    V7.emit_key_closing = emit_key_closing
    return dict(ext=ext, prefix=emit_key_prefix, closing=emit_key_closing, Public=Public)


# ---------------- head ripple (lane dqi_guard): replaces the synthesis-return guard ----------------
RIPPLE = True
RIPPLE_SLOTS = tuple(range(31, 16, -2))


def head_ripple(b, Tail, heads, masks=None):
    """After the NATIVE synthesis return and the seed return: for odd t <= 33 the first-slot head t-1 reads 0 and its
    true value P sits in head 34 (model: src/dqi_guard/native_chain.py); every other head is exact. For s = 32, 30, ..
    18: z = [head(s+1) = 0] (the node's second-slot head: 1 iff s >= t-1 for odd t, s >= t for even t, untouched here);
    cswap(z; head(s), head(s+2)) carries P down one node (zeros only, for even t); z is erased exactly from the same
    word. 23 + 24 + 22 static T per node."""
    for sl in RIPPLE_SLOTS:
        z = b.alloc_qubits(1)[0]
        Tail.zero_xor(b, heads[sl + 1], z)
        b.cswap(z, heads[sl], heads[sl + 2])
        if masks is None:
            Tail.erase_zero_flag(b, heads[sl + 1], z)
            b.free(km.array([z]))
        else:   # lane dqi_tail: X-measure z = g_{sl+1}; paid at the extractor return's zero(carry) query of slot sl+1
            m = b.alloc_bits(1); b.hmr(km.array([z]), m); b.free(km.array([z])); masks[sl + 1] = m


def finish_after_swap_deferred(builder, scale, head, flag, record):
    """scalar_seed_padded.finish_after_swap (Syed Asad Ali, Apache-2.0) except that the CZs of the forward old-input
    masks with the head words are left to the caller (paid after head_ripple, when head 34 is exact again)."""
    from tower_inverse import phase_product, kernel
    assert not record.closed and record.builder_id == id(builder)
    assert tuple(scale) == record.source and tuple(head) == record.targets
    builder.cz(record.zero_mask[0], flag)
    builder.cz(record.inverse_mask[0], flag)
    builder.free(record.zero_mask)
    builder.free(record.inverse_mask)
    olds = []
    for i, (target, old_product, old_input) in enumerate(zip(
            (head[:12], head[12:]), record.product_masks, record.seed.old_masks)):
        phase_product(builder, scale, target, old_product, kernel(12))
        if i == 1:
            # Old padded Dx = lambda*P1 + f*lambda, since f=1 => P1=0.
            for q, classical in zip(scale, old_product):
                builder.ccz(classical, flag, q)
        builder.free(old_product)
        olds.append(old_input)
    record.seed.closed = True
    record.closed = True
    return olds


# ---------------- guarded synthesis closing (first slot of a double node in the tail region) ----------------
GUARDED = frozenset(range(18, 33, 2))


class Guard:
    """At the terminal of a second slot (odd t) the synthesized D of the preceding first slot has a simple zero at
    alpha with P != 0 and N = 0, X = P D: the unit closing X(alpha)/D(alpha) is replaced by X'(alpha)/D'(alpha) under
    h = [D(alpha) = 0] AND [D'(alpha) != 0]; N is then recovered from r-2 points and N(alpha) = X' + c1 D(alpha) + P D'."""

    def __init__(self, Syn, Tail, A):
        self.S, self.T, self.A = Syn, Tail, A
        from field_tensor import invert_field_matrix, accumulate_product
        from tower_inverse import apply_inplace_linear, xor_product
        from monic_forney import flat, add_scaled
        self.inv, self.acc, self.lin, self.xp, self.flat, self.add_scaled = (invert_field_matrix, accumulate_product,
                                                                          apply_inplace_linear, xor_product, flat, add_scaled)
        self.rows = {}

    def _powers(self, i, n):
        return self.S.residue_powers(i, n)

    def views(self, r, i):
        key = (r, i)
        if key in self.rows: return self.rows[key]
        Fm, fr = F, self.S.field_rows
        pw = self._powers(i, r + 2)
        # X (r+2 coefficients) -> X(beta) beta < r-2, X'(alpha) (2), X(alpha) (2)
        mx = [[Fm.pow(beta, j) for j in range(r + 2)] for beta in range(r - 2)]
        mx += [[pw[j - 1][c] if j % 2 else 0 for j in range(r + 2)] for c in (0, 1)]
        mx += [[pw[j][c] for j in range(r + 2)] for c in (0, 1)]
        # D (r+1 coefficients) -> D(alpha) (2), D'(alpha) (2) [r >= 3] or D_1 [r == 2], rest identity
        md = [[pw[j][c] for j in range(r + 1)] for c in (0, 1)]
        if r >= 3:
            md += [[pw[j - 1][c] if j % 2 else 0 for j in range(r + 1)] for c in (0, 1)]
            md += [[int(j == k) for j in range(r + 1)] for k in range(4, r + 1)]
        else:
            md += [[int(j == 1) for j in range(r + 1)]]
        _, kappa = self.S.node(i)
        mn = [[Fm.mul(Fm.mul(beta, beta) ^ beta ^ kappa, Fm.pow(beta, j)) for j in range(r)] for beta in range(r - 2)]
        mn += [[pw[j][c] for j in range(r)] for c in (0, 1)]
        out = dict(x=fr(mx), d=fr(md), dinv=fr(self.inv(md, Fm)), n=fr(self.inv(mn, Fm)))
        self.rows[key] = out
        return out

    def conj(self, b, target, zero_words, nonzero_words):
        """target ^= AND_w [w == 0] AND AND_v [v != 0]; words are lists of 12-bit registers (1 or 2)."""
        items = [(w, False) for w in zero_words] + [(v, True) for v in nonzero_words]
        made = []
        for halves, neg in items:
            fl = []
            for h12 in halves:
                q = b.alloc_qubits(1)[0]; self.T.zero_xor(b, h12, q); fl.append(q)
            if len(fl) == 2:
                z = b.alloc_qubits(1)[0]; b.ccx(fl[0], fl[1], z)
            else:
                z = fl[0]
            made.append((halves, fl, z, neg))
        zs = [m[2] for m in made]
        for m in made:
            if m[3]: b.x(m[2])
        assert len(zs) == 2
        b.ccx(zs[0], zs[1], target)
        for m in made:
            if m[3]: b.x(m[2])
        for halves, fl, z, neg in reversed(made):
            if len(fl) == 2:
                b.ccx(fl[0], fl[1], z); b.free(km.array([z]))
            for h12, q in reversed(list(zip(halves, fl))):
                self.T.erase_zero_flag(b, h12, q); b.free(km.array([q]))

    def closing(self, b, N, D, P, record):
        N, D, P = list(N), list(D), list(P)
        r, i = record.r, record.node_index
        assert len(N) == r and len(D) == r + 1 and len(P) == 2 and r >= 2
        V = self.views(r, i)
        flat = self.flat
        self.lin(b, flat(N + P), V['x'])
        self.lin(b, flat(D), V['d'])
        Dal = [D[0], D[1]]
        Dpr = [D[2], D[3]] if r >= 3 else [D[2]]
        Xal, Xpr = [P[0], P[1]], [N[r - 2], N[r - 1]]
        h = b.alloc_qubits(1)[0]
        self.conj(b, h, [Dal], [Dpr])
        for s_, t_ in zip(flat(Dpr), flat(Dal)): b.ccx(h, s_, t_)
        for s_, t_ in zip(flat(Xpr), flat(Xal)): b.ccx(h, s_, t_)

        def witness(h):   # h ^= [Dal xor Dpr == 0] and [Dpr != 0]  (exact except D(alpha) == D'(alpha) != 0)
            for s_, t_ in zip(flat(Dpr), flat(Dal)): b.cx(s_, t_)
            self.conj(b, h, [Dal], [Dpr])
            for s_, t_ in zip(flat(Dpr), flat(Dal)): b.cx(s_, t_)
        witness(h); b.free(km.array([h]))
        self.A.emit_closing(b, flat(Dal), flat(Xal), record.pair_record)
        h = b.alloc_qubits(1)[0]; witness(h)
        for s_, t_ in zip(flat(Dpr), flat(Dal)): b.ccx(h, s_, t_)
        self.conj(b, h, [Dal], [Dpr])
        b.free(km.array([h]))
        # N(alpha) = X'(alpha) + c1 D(alpha) + P(alpha) D'(alpha)   (P words hold P(alpha) in common K)
        c1 = P[1]
        self.xp(b, c1, Dal[0], Xpr[0]); self.xp(b, c1, Dal[1], Xpr[1])
        if r >= 3:
            self.A.product(b, flat(P), flat(Dpr), flat(Xpr))
        else:
            self.xp(b, Dpr[0], P[0], Xpr[0]); self.xp(b, Dpr[0], P[1], Xpr[1])
        self.lin(b, flat(D), V['dinv'])
        t, _ = self.S.node(i)
        self.add_scaled(b, P[1], P[0], t)
        for beta in range(r - 2):
            self.S.evaluation_view(b, D, beta); self.S.evaluation_view(b, P, beta)
            self.acc(b, D[0], P[0], N[beta])
            self.S.evaluation_view(b, P, beta); self.S.evaluation_view(b, D, beta)
        self.lin(b, flat(N), V['n'])


def closing_with_case1(A, builder, source, value, record, xpr, Tail):
    """gf24_nested_norm.emit_closing (Syed Asad Ali, Apache-2.0), unguarded, with one added repayment: when the source is
    0 (case 1 of the guard: S = 0, V = X'(alpha)), the adjoint temporary held V = xpr, whose HMR debt is not a function of
    source*value; pay (-1)^{m . xpr} under z = [source = 0] (classical-mask CCZs, z by a 24-bit zero test)."""
    assert id(builder) == record.builder_id and not record.closed and not record.guarded
    delta = record.delta
    temporary = builder.alloc_qubits(24)
    builder.cx(source[12:], source[:12])
    A.product(builder, source, value, temporary, delta, record.tensor)
    builder.cx(source[12:], source[:12])
    builder.swap(value, temporary)
    old_product_mask = builder.alloc_bits(24)
    builder.hmr(temporary, old_product_mask)
    builder.free(temporary)
    norm = A.init_norm(builder, source[:12], source[12:], delta)
    norm_masks = A.Prior.inverse_twelve_deferred(builder, norm)
    A._repay_norm_source_masks(builder, source, norm_masks, delta, None)
    temporary = builder.alloc_qubits(12)
    scaled_masks = []
    for half in (value[:12], value[12:]):
        A.xor_product(builder, half, norm, temporary)
        builder.swap(half, temporary)
        mask = builder.alloc_bits(12)
        builder.hmr(temporary, mask)
        scaled_masks.append(mask)
    builder.free(temporary)
    inverse_mask = builder.alloc_bits(12)
    builder.hmr(norm, inverse_mask)
    builder.free(norm)
    norm = A.init_norm(builder, source[:12], source[12:], delta)
    A.Phase12.phase_inverse_twelve_polynomial(builder, norm, inverse_mask)
    builder.free(inverse_mask)
    for half, mask in zip((value[:12], value[12:]), scaled_masks):
        A.phase_product(builder, half, norm, mask, A.kernel(12))
        builder.free(mask)
    A.erase_norm(builder, source[:12], source[12:], norm, delta)
    builder.free(norm)
    builder.cz(record.old_target_mask, value)
    builder.free(record.old_target_mask)
    A.phase_product(builder, source, value, old_product_mask, record.tensor)
    z = builder.alloc_qubits(1)[0]
    Tail.zero_xor(builder, source, z)
    for m, q in zip(old_product_mask, xpr):
        builder.ccz(m, z, q)
    Tail.erase_zero_flag(builder, source, z)
    builder.free(km.array([z]))
    builder.free(old_product_mask)
    record.closed = True


class Guard2(Guard):
    """Single-test guard: h = [D(alpha) = 0]; S = D(alpha) + h D'(alpha), V = X(alpha) + h X'(alpha).
    Case 1 (S = 0, V = N(alpha)) is closed by closing_with_case1. h is erased around the closing by the witness
    [S xor D' = 0] (exact except D(alpha) = D'(alpha) != 0, about 2^-24 per step)."""

    def closing(self, b, N, D, P, record):
        N, D, P = list(N), list(D), list(P)
        r, i = record.r, record.node_index
        assert len(N) == r and len(D) == r + 1 and len(P) == 2 and r >= 2
        V = self.views(r, i)
        flat = self.flat
        self.lin(b, flat(N + P), V['x'])
        self.lin(b, flat(D), V['d'])
        Dal = flat([D[0], D[1]])
        Dpr = flat([D[2], D[3]]) if r >= 3 else flat([D[2]])
        Xal, Xpr = flat([P[0], P[1]]), flat([N[r - 2], N[r - 1]])
        h = b.alloc_qubits(1)[0]
        self.T.zero_xor(b, Dal, h)
        for s_, t_ in zip(Dpr, Dal): b.ccx(h, s_, t_)
        for s_, t_ in zip(Xpr, Xal): b.ccx(h, s_, t_)
        def xor_dpr():
            for s_, t_ in zip(Dpr, Dal): b.cx(s_, t_)
        xor_dpr(); self.T.erase_zero_flag(b, Dal, h); xor_dpr(); b.free(km.array([h]))
        closing_with_case1(self.A, b, Dal, Xal, record.pair_record, Xpr, self.T)
        h = b.alloc_qubits(1)[0]
        xor_dpr(); self.T.zero_xor(b, Dal, h); xor_dpr()
        for s_, t_ in zip(Dpr, Dal): b.ccx(h, s_, t_)
        self.T.erase_zero_flag(b, Dal, h); b.free(km.array([h]))
        c1 = P[1]
        self.xp(b, c1, D[0], N[r - 2]); self.xp(b, c1, D[1], N[r - 1])
        if r >= 3:
            self.A.product(b, flat(P), Dpr, Xpr)
        else:
            self.xp(b, D[2], P[0], N[r - 2]); self.xp(b, D[2], P[1], N[r - 1])
        self.lin(b, flat(D), V['dinv'])
        t, _ = self.S.node(i)
        self.add_scaled(b, P[1], P[0], t)
        for beta in range(r - 2):
            self.S.evaluation_view(b, D, beta); self.S.evaluation_view(b, P, beta)
            self.acc(b, D[0], P[0], N[beta])
            self.S.evaluation_view(b, P, beta); self.S.evaluation_view(b, D, beta)
        self.lin(b, flat(N), V['n'])


class Guard3(Guard):
    """Guard v3 (lane dqi_guard): Guard2 without the derivative view on X. The X words keep the unguarded view
    (X(beta) at the r public points, X(alpha) in the P words). On every h = 1 class X(alpha) = P(alpha) D(alpha) = 0,
    so X'(alpha) = L(X(beta_0..beta_{r-1})) with L the beta-part of X'(alpha) in that view: an in-place F-linear map T on
    the N words alone brings L into two N words (0 T), V += h L (24 CCX), T is undone after the closing, and N is then
    recovered from all r points exactly as in the unguarded closing (no c1 D(alpha) and P D' products)."""

    def tmaps(self, r, i):
        key = ('T', r, i)
        if key in self.rows: return self.rows[key]
        Fm = F
        pw = self._powers(i, r + 2)
        C = [[Fm.pow(beta, j) for j in range(r + 2)] for beta in range(r)]
        C += [[pw[j][c] for j in range(r + 2)] for c in (0, 1)]
        Ci = self.inv(C, Fm)
        dx = [[pw[j - 1][c] if j % 2 else 0 for j in range(r + 2)] for c in (0, 1)]
        L = [[0] * (r + 2) for _ in (0, 1)]
        for c in (0, 1):
            for k in range(r + 2):
                v = 0
                for j in range(r + 2): v ^= Fm.mul(dx[c][j], Ci[j][k])
                L[c][k] = v
        L = [row[:r] for row in L]
        pick = None
        for k0 in range(r - 1, -1, -1):
            for k1 in range(k0 - 1, -1, -1):
                if Fm.mul(L[0][k1], L[1][k0]) ^ Fm.mul(L[0][k0], L[1][k1]):
                    pick = (k1, k0); break
            if pick: break
        assert pick is not None
        T = [[int(a == b) for b in range(r)] for a in range(r)]
        T[pick[0]], T[pick[1]] = L[0][:], L[1][:]
        out = dict(pick=pick, t=self.S.field_rows(T), tinv=self.S.field_rows(self.inv(T, Fm)))
        self.rows[key] = out
        return out

    def closing(self, b, N, D, P, record):
        N, D, P = list(N), list(D), list(P)
        r, i = record.r, record.node_index
        assert len(N) == r and len(D) == r + 1 and len(P) == 2 and r >= 2
        V = self.views(r, i); TM = self.tmaps(r, i)
        flat = self.flat
        self.lin(b, flat(N + P), self.S.crt_rows(r, i))
        self.lin(b, flat(D), V['d'])
        self.lin(b, flat(N), TM['t'])
        Dal = flat([D[0], D[1]])
        Dpr = flat([D[2], D[3]]) if r >= 3 else flat([D[2]])
        Xal, Xpr = flat([P[0], P[1]]), flat([N[TM['pick'][0]], N[TM['pick'][1]]])
        h = b.alloc_qubits(1)[0]
        self.T.zero_xor(b, Dal, h)
        for s_, t_ in zip(Dpr, Dal): b.ccx(h, s_, t_)
        for s_, t_ in zip(Xpr, Xal): b.ccx(h, s_, t_)
        def xor_dpr():
            for s_, t_ in zip(Dpr, Dal): b.cx(s_, t_)
        xor_dpr(); self.T.erase_zero_flag(b, Dal, h); xor_dpr(); b.free(km.array([h]))
        closing_with_case1(self.A, b, Dal, Xal, record.pair_record, Xpr, self.T)
        h = b.alloc_qubits(1)[0]
        xor_dpr(); self.T.zero_xor(b, Dal, h); xor_dpr()
        for s_, t_ in zip(Dpr, Dal): b.ccx(h, s_, t_)
        self.T.erase_zero_flag(b, Dal, h); b.free(km.array([h]))
        self.lin(b, flat(N), TM['tinv'])
        self.lin(b, flat(D), V['dinv'])
        t, _ = self.S.node(i)
        self.add_scaled(b, P[1], P[0], t)
        for beta in range(r):
            self.S.evaluation_view(b, D, beta); self.S.evaluation_view(b, P, beta)
            self.acc(b, D[0], P[0], N[beta])
            self.S.evaluation_view(b, P, beta); self.S.evaluation_view(b, D, beta)
        self.lin(b, flat(N), self.S.recover_n_rows(r, i))
