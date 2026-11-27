"""Pay old GF(2^24) zero tests on the GF(8) norm inside the in-place reciprocal."""
from contextlib import contextmanager


@contextmanager
def at_inverse(masks, omit=False, fused=False):
    import nested_norm_inverse as tower
    masks = [m for m in masks if m is not None]
    if not masks:
        yield
        return
    native = tower.inverse_three
    calls = 0

    def inverse_with_payment(builder, norm):
        nonlocal calls
        calls += 1
        assert calls == 1 and len(norm) == 3
        if fused and not omit:
            from lowspace_field import transpositions_three,apply_inplace_linear
            import kickmix as km
            import itertools
            for j,(value,to_basis,from_basis) in enumerate(transpositions_three()):
                offset=[norm[i] for i in range(3) if value>>i&1]
                builder.x(offset);apply_inplace_linear(builder,norm,to_basis);builder.x(norm[1:])
                if j==0:
                    # Coordinate of zero in this affine Toffoli chart. The
                    # equality's cubic monomial uses the very same AND as the inverse.
                    at=sum(((value&r).bit_count()%2)<<i for i,r in enumerate(to_basis))^6
                    terms=[subset for size in (1,2) for subset in itertools.combinations(range(3),size)
                           if all(at>>k&1==0 for k in range(3) if k not in subset)]
                    tmp=builder.alloc_qubits(1)[0];builder.init_and(norm[1],norm[2],tmp)
                    for mask in masks:
                        builder.push_condition(mask[0])
                        builder.cz(tmp,norm[0])
                        for subset in terms:
                            if len(subset)==1:builder.z(norm[subset[0]])
                            else:builder.cz(norm[subset[0]],norm[subset[1]])
                        if at==0:builder.neg()
                        builder.pop_condition()
                    builder.cx(tmp,norm[0]);builder.del_and(norm[1],norm[2],tmp);builder.free(km.array([tmp]))
                else:builder.ccx(norm[1],norm[2],norm[0])
                builder.x(norm[1:]);apply_inplace_linear(builder,norm,from_basis);builder.x(offset)
            for debt in masks:builder.free(debt)
            return
        if not omit:
            builder.x(norm)
            for debt in masks:
                builder.push_condition(debt[0])
                builder.ccz(norm[0], norm[1], norm[2])
                builder.pop_condition()
            builder.x(norm)
        for debt in masks:
            builder.free(debt)
        return native(builder, norm)

    tower.inverse_three = inverse_with_payment
    try:
        yield
    finally:
        tower.inverse_three = native
    assert calls == 1


def patch(source, omit=False, fused=False):
    before = """            for m in (mz, rec.get('rz', {}).pop(s + 1, None)):
                if m is not None: self.Tail.zero_phase(b, W2, m[0]); b.free(m)
            mz = None
"""
    assert source.count(before) == 1
    source = source.replace(before, """            debts = (mz, rec.get('rz', {}).pop(s + 1, None))
            mz = None
""")
    site = "            A.inverse_closed(b, W2); A.repay_source_masks(b, W2, rec['inv2'][a])"
    assert source.count(site) == 1
    return source.replace(site, "            from norm_zero_payment import at_inverse\n            with at_inverse(debts, "+str(omit)+" and a==10,"+str(fused)+"):A.inverse_closed(b,W2)\n            A.repay_source_masks(b, W2, rec['inv2'][a])")
