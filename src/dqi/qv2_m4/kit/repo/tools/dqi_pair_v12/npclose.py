# SPDX-License-Identifier: Apache-2.0
# Norm-preserving GF(2^24) closing (lane dqi_close, kit v11). Our own code after the public reference.
# Idea and reference implementation: Balram Srinivasan's team, dataset "VQCC 28.10 norm-preserving DQI closings"
# (tools/closing_norm_preserving_body.py, Apache-2.0). Original builder and every helper used here: Syed Asad Ali
# (v12 DQI decoder, gf24_nested_norm.emit_closing, Apache-2.0). Lineage starting from Syed Asad Ali.
"""Replacement for gf24_nested_norm.emit_closing on UNGUARDED records (guarded records keep the original).

Old: adjoint product 99 + norm 42 + GF(2^12) inverse 66 + two products 84 + norm 42 + phase 27 = 360 T.
New: the 12-bit norm N stays alive; value <- conj_6(N) * value (84; conj_6 = the GF(2^12)/GF(2^6) conjugation, linear),
so value = C v0 with C = N_6(N) in GF(64); C^-1 by the 6-bit deferred inverse (15 + 21, its entry masks paid on N's
halves); the four 6-bit quarters times C^-1 (60); C^-1 X-measured and paid by a 6-bit recompute of C (15) and
phase_inverse_six (6 static). 99 + 42 + 84 + 36 + 60 + 15 + 6 = 342 static, about 340 executed.

closing_with_case1: the same with the case-1 repayment of confluent_ext.closing_with_case1 (source = 0, the adjoint
temporary held xpr: pay (-1)^{m . xpr} under z = [source = 0])."""
import kickmix as km

CENSUS = {}


def _body(A, builder, source, value, record):
    from tower_inverse import quadratic_basis, apply_inplace_linear, init_norm, erase_norm, xor_product, \
        phase_product, kernel
    import nested_norm_inverse as Prior
    from scalar_inverse_phase import phase_inverse_six
    assert id(builder) == record.builder_id and not record.closed and not record.guarded
    assert len(source) == len(value) == 24
    delta = record.delta
    i12, i6 = quadratic_basis(12), quadratic_basis(6)
    # 1. value <- conj(source) * value = N v0 (as the original closing)
    temporary = builder.alloc_qubits(24)
    builder.cx(source[12:], source[:12])
    A.product(builder, source, value, temporary, delta, record.tensor)
    builder.cx(source[12:], source[:12])
    builder.swap(value, temporary)
    old_product_mask = builder.alloc_bits(24)
    builder.hmr(temporary, old_product_mask)
    builder.free(temporary)
    # 2. N = N_12(source)
    norm = init_norm(builder, source[:12], source[12:], delta)
    # 3. norm <- conj_6(N) (linear), value halves <- conj_6(N) * (N v0) = C v0; norm back to N
    apply_inplace_linear(builder, norm, i12['to_tower']); builder.cx(norm[6:], norm[:6])
    apply_inplace_linear(builder, norm, i12['from_tower'])
    temporary = builder.alloc_qubits(12)
    scaled = []
    for half in (value[:12], value[12:]):
        xor_product(builder, half, norm, temporary)
        builder.swap(half, temporary)
        m = builder.alloc_bits(12); builder.hmr(temporary, m); scaled.append(m)
    builder.free(temporary)
    apply_inplace_linear(builder, norm, i12['to_tower']); builder.cx(norm[6:], norm[:6])   # norm = N, tower basis
    # 4. child = C^-1 (inv0), entry masks paid on N's tower halves
    child = init_norm(builder, norm[:6], norm[6:], i12['delta'])
    cm = Prior.inverse_six_deferred(builder, child)
    Prior.repay_norm_entry(builder, norm[:6], norm[6:], i12['delta'], cm)
    # 5. quarters (tower basis of each half) <- C^-1 * quarter = v0
    temp6 = builder.alloc_qubits(6)
    qm = []
    for half in (value[:12], value[12:]):
        apply_inplace_linear(builder, half, i12['to_tower'])
        for q in (half[:6], half[6:]):
            xor_product(builder, q, child, temp6)
            builder.swap(q, temp6)
            m = builder.alloc_bits(6); builder.hmr(temp6, m); qm.append(m)
        apply_inplace_linear(builder, half, i12['from_tower'])
    builder.free(temp6)
    # 6. X-measure C^-1 (tower coordinates), pay with C recomputed; pay the quarter masks (C v0_q)
    apply_inplace_linear(builder, child, i6['to_tower'])
    child_mask = builder.alloc_bits(6); builder.hmr(child, child_mask); builder.free(child)
    c = init_norm(builder, norm[:6], norm[6:], i12['delta'])
    phase_inverse_six(builder, c, child_mask)
    builder.free(child_mask)
    k = 0
    for half in (value[:12], value[12:]):
        apply_inplace_linear(builder, half, i12['to_tower'])
        for q in (half[:6], half[6:]):
            phase_product(builder, q, c, qm[k], kernel(6)); builder.free(qm[k]); k += 1
        apply_inplace_linear(builder, half, i12['from_tower'])
    erase_norm(builder, norm[:6], norm[6:], c, i12['delta'])
    builder.free(c)
    # 7. norm to polynomial basis; pay the scaled masks (N v0 halves); erase N against the source
    apply_inplace_linear(builder, norm, i12['from_tower'])
    for half, m in zip((value[:12], value[12:]), scaled):
        phase_product(builder, half, norm, m, kernel(12)); builder.free(m)
    erase_norm(builder, source[:12], source[12:], norm, delta)
    builder.free(norm)
    # 8. prefix's old-target mask and the adjoint product's mask
    builder.cz(record.old_target_mask, value)
    builder.free(record.old_target_mask)
    A.phase_product(builder, source, value, old_product_mask, record.tensor)
    return old_product_mask


def emit_closing(A, builder, source, value, record):
    m = _body(A, builder, source, value, record)
    builder.free(m)
    record.closed = True


def closing_with_case1(A, builder, source, value, record, xpr, Tail):
    m = _body(A, builder, source, value, record)
    z = builder.alloc_qubits(1)[0]
    Tail.zero_xor(builder, source, z)
    for mi, q in zip(m, xpr):
        builder.ccz(mi, z, q)
    Tail.erase_zero_flag(builder, source, z)
    builder.free(km.array([z]))
    builder.free(m)
    record.closed = True


def install(A, CE, enable=True):
    """A = gf24_nested_norm (P.Arithmetic); CE = confluent_ext. Replaces A.emit_closing (unguarded records only) and
    CE.closing_with_case1; counts calls by (caller, guarded) in CENSUS."""
    import sys as _s
    orig = A.emit_closing

    def emit(builder, source, value, record):
        f = _s._getframe(1)
        key = f'{f.f_code.co_filename.rsplit("/", 1)[-1]}:{f.f_code.co_name}:{"guarded" if record.guarded else "unguarded"}'
        CENSUS[key] = CENSUS.get(key, 0) + 1
        if record.guarded or not enable:
            return orig(builder, source, value, record)
        return emit_closing(A, builder, source, value, record)
    A.emit_closing = emit
    orig_c1 = CE.closing_with_case1

    def c1(A_, builder, source, value, record, xpr, Tail):
        f = _s._getframe(1)
        key = f'{f.f_code.co_filename.rsplit("/", 1)[-1]}:{f.f_code.co_name}:case1'
        CENSUS[key] = CENSUS.get(key, 0) + 1
        if not enable:
            return orig_c1(A_, builder, source, value, record, xpr, Tail)
        return closing_with_case1(A_, builder, source, value, record, xpr, Tail)
    CE.closing_with_case1 = c1
