"""Native split quadratic Forney cells at two omitted ground-field points each."""
from contextlib import contextmanager
from functools import cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
OUTER = HERE.parent / '20261118T032100Z-dqi-outer-splice'
BLOCK = HERE.parent / '20261118T033800Z-dqi-block-source'
sys.path[:0] = [str(OUTER), str(BLOCK)]
from held_split_pivots import RealPair


def set_geometry(offset=0):
    from quadratic import places
    places[:8] = [RealPair(offset+2*i) for i in range(8)]
    return places


def make_scope(v, ce, out):
    import fusion_hook
    import joint_finish_scope
    from held_phase_splice import change

    saved_install, saved_scope = fusion_hook.install, fusion_hook.arithmetic_scope
    captured = []
    def capture(v, ce, out):
        f = fusion_hook.arithmetic_scope(v)
        change(f, 'timed-mask')
        captured.append(f)
    try:
        fusion_hook.install = capture
        joint_finish_scope.install(v, ce, out)
    finally:
        fusion_hook.install, fusion_hook.arithmetic_scope = saved_install, saved_scope
    return captured[0]


def build(v, ce, out, offset=0, slots=0, cell_hooks=None):
    from compact_inverse22 import compact_inverse_twelve
    from endnode import deferred_scale, hmr_word
    from phase_inverse12 import phase_inverse_twelve_polynomial
    from tower_inverse import phase_product, kernel
    from source_maps import transpose

    places = set_geometry(offset)
    f = make_scope(v, ce, out)
    M = f['M']
    f['Place'] = lambda d: next(m for m in places if m.d == d)
    transform, chart, ev = f['transform'], f['chart'], f['ev']
    prod, xform = f['xor_product'], f['xform']
    ker = kernel(12)
    normalized = bool(getattr(cell_hooks, 'normalized', False))
    if normalized:
        cell_hooks.install_centre(f)

    def pay(b, word, mask):
        b.cz(word, mask)
        b.free(mask)

    def product_debt(b, a, c, mask):
        phase_product(b, a, c, mask, ker)
        b.free(mask)

    @cache
    def matrix(x):
        return ((1,x),(1,x^1))

    @contextmanager
    def evaluate(b, x, words):
        for word in words:
            transform(b,word,matrix(x))
        try:
            yield
        finally:
            for word in reversed(words):
                transform(b,word,matrix(x),True)

    def opens(b, s, debt):
        z = compact_inverse_twelve(b,s)
        if debt is not None:
            pay(b,z,debt)
        return z

    def handoff(b, s, r, heads, node, event, mode, states, physical=None):
        """Two independent scalar inverse lifetimes retain classical phase debt only."""
        with evaluate(b,node.x,[s,r,*heads]):
            for side in range(2):
                state = states[side]
                source, target = s[side], r[side]
                payload = [h[side] for h in heads]
                if cell_hooks is not None and hasattr(cell_hooks,'filter_payload'):
                    payload=cell_hooks.filter_payload(node,side,mode,payload)
                release = None
                if cell_hooks is not None and physical is not None:
                    release = cell_hooks.denominator(b, f, node, side, physical)
                if event == 'open':
                    z = opens(b,source,None)
                    state['r'] = deferred_scale(b,target,z)
                    if mode == 'c':
                        state['h'] = [deferred_scale(b,h,z) for h in payload]
                    state['z'] = hmr_word(b,z)
                elif event == 'mid':
                    z = opens(b,source,state['z']) if mode == 'q' else None
                    state['post'] = deferred_scale(b,target,source)
                    pay(b,target,state['r'])
                    if z is not None:
                        state['h'] = [deferred_scale(b,h,z) for h in payload]
                        state['z'] = hmr_word(b,z)
                elif event == 'back':
                    z = opens(b,source,state['z'])
                    state['r'] = deferred_scale(b,target,z)
                    pay(b,target,state['post'])
                    if mode == 'q':
                        for h,debt in zip(payload,state['h']):
                            old = deferred_scale(b,h,source)
                            pay(b,h,debt)
                            product_debt(b,h,z,old)
                    state['z'] = hmr_word(b,z)
                elif event == 'close':
                    z = opens(b,source,state['z'])
                    old = deferred_scale(b,target,source)
                    pay(b,target,state['r'])
                    product_debt(b,target,z,old)
                    if mode == 'c':
                        for h,debt in zip(payload,state['h']):
                            old = deferred_scale(b,h,source)
                            pay(b,h,debt)
                            product_debt(b,h,z,old)
                    mask = hmr_word(b,z)
                    phase_inverse_twelve_polynomial(b,source,mask)
                    b.free(mask)
                else:
                    raise ValueError(event)
                if release is not None:
                    release()

    @cache
    def transport(i, size, j):
        """Map products at both j roots to their interpolant evaluated modulo place i."""
        from compact_finish import point_l
        from source_maps import inverse, mv
        to_coeff = inverse(matrix(places[j].x))
        linear = point_l(i,size,j)
        return tuple(map(tuple,transpose([mv(transpose(linear),col) for col in transpose(to_coeff)])))

    @cache
    def incidence(linear):
        result = []
        for src in range(24):
            for k in range(2):
                x = M.mul(linear[k][src//12],1<<(src%12))
                result.extend((12*k+bit,src) for bit in range(12) if x>>bit&1)
        return tuple(result)

    def cross(b, c, q, Y, i, size, back):
        if i+1 == size:
            return
        cc = chart(len(c),places[i].d)
        if not back:
            for y in Y:
                transform(b,y[:2],f['tail_scalar'](i,size))
        transform(b,c,cc,True)
        for y in Y:
            temp = b.alloc_qubits(24)
            pair = [temp[:12],temp[12:]]
            def contribution(j, mask=None):
                m = places[j]
                cj = chart(len(c),m.d)
                view = y[2*(j-i):2*(j-i)+2]
                transform(b,c,cj)
                linear = transport(i,size,j)
                with evaluate(b,m.x,[c[:2],view]):
                    if mask is None:
                        transform(b,pair,linear,True)
                        for a,h,t in zip(c[:2],view,pair):
                            prod(b,a,h,t)
                        transform(b,pair,linear)
                    else:
                        adj = b.alloc_bits(24)
                        b.bit_store(adj,False)
                        entries = incidence(linear)
                        for dst,src in entries:
                            b.cx(mask[dst],adj[src])
                        for k in range(2):
                            phase_product(b,c[k],view[k],adj[12*k:12*k+12],ker)
                        for dst,src in entries:
                            b.cx(mask[dst],adj[src])
                        b.free(adj)
                transform(b,c,cj,True)
            for j in range(i+1,size):
                contribution(j)
            with evaluate(b,places[i].x,[q,pair,y[:2]]):
                for a,h,t in zip(q,pair,y[:2]):
                    prod(b,a,h,t)
            mask = b.alloc_bits(24)
            b.hmr(temp,mask)
            b.free(temp)
            for j in range(i+1,size):
                contribution(j,mask)
            b.free(mask)
        transform(b,c,cc)
        if back:
            for y in Y:
                transform(b,y[:2],f['tail_scalar'](i,size),True)

    def walk(b,A,B,Y,n0,back,prior,frames=()):
        n = len(A)-1
        if n == 1:
            return {'leaf':f['centre_fused'](b,B,Y,frames,back,prior['leaf'] if back else None)}
        i,size = (n0-n)//2,(n0-1)//2
        m = places[i]
        ca,cb,cc = (chart(k,m.d) for k in (n+1,n,n-1))
        transform(b,A,ca)
        transform(b,B,cb)
        if not back:
            for y in Y:
                transform(b,y,cb)
        r,c = A[:2],A[2:]
        q,e = B[:2],B[2:]
        heads = [y[:2] for y in Y]
        tails = [y[2:] for y in Y]
        qs,cs = (prior['q'],prior['c']) if back else ([{},{}],[{},{}])
        handoff(b,q,r,heads,m,'back' if back else 'open','c' if normalized else 'q',qs)
        xform(b,c,r,B,m.d,False)
        transform(b,c,ev(n-1),True)
        transform(b,c,cc)
        rational = bool(getattr(cell_hooks,'rational',False))
        if rational:
            extras=cell_hooks.enter(b,f,m,c,B,Y,back,prior['extra'] if back else None,evaluate)
        handoff(b,c[:2],q,heads,m,'back' if back else 'open','q' if normalized else 'c',cs,c)
        def upper(reverse):
            if rational:
                cell_hooks.upper(b,f,c,Y,i,size,extras,reverse,evaluate)
            elif normalized:
                cell_hooks.cross(b,f,c,Y,i,size,reverse,transport,evaluate)
            else:
                cross(b,c,q,Y,i,size,reverse)
        def lower(tail,head,reverse,k):
            if rational:
                cell_hooks.row(b,f,tail,head,q,c,m,extras,reverse,k,evaluate)
            elif normalized:
                cell_hooks.lower(b,f,tail,head,q,c,m,reverse,evaluate)
            else:
                xform(b,tail,head,c,m.d,reverse)
        if back:
            upper(True)
        else:
            for k,(tail,head) in enumerate(zip(tails,heads)):
                lower(tail,head,False,k)
                transform(b,tail,ev(n-2),True)
        if rational:cell_hooks.source(b,f,e,q,c,m,extras,False,evaluate)
        else:xform(b,e,q,c,m.d,False)
        transform(b,e,ev(n-2),True)
        if rational and not back:cell_hooks.erase_k(b,extras)
        transform(b,c,cc,True)
        base_frame=(r,q,heads,m.d)
        child = walk(b,c,e,tails,n0,back,prior['child'] if back else None,(*frames,base_frame+(extras['flags'],) if rational else base_frame))
        transform(b,c,cc)
        if rational and back:cell_hooks.recover_k(b,f,e,tails,m,extras)
        transform(b,e,ev(n-2))
        if rational:cell_hooks.source(b,f,e,q,c,m,extras,True,evaluate)
        else:xform(b,e,q,c,m.d,True)
        if back:
            for k,(tail,head) in enumerate(zip(tails,heads)):
                transform(b,tail,ev(n-2))
                lower(tail,head,True,k)
        else:
            upper(False)
        handoff(b,c[:2],q,heads,m,'close' if back else 'mid','q' if normalized else 'c',cs,c)
        if rational:cell_hooks.leave(b,f,m,c,B,Y,back,extras,evaluate)
        transform(b,c,cc,True)
        transform(b,c,ev(n-1))
        xform(b,c,r,B,m.d,True)
        handoff(b,q,r,heads,m,'close' if back else 'mid','c' if normalized else 'q',qs)
        if back:
            for y in Y:
                transform(b,y,cb,True)
        transform(b,B,cb,True)
        transform(b,A,ca,True)
        return dict(q=qs,c=cs,child=child,**({'extra':extras} if rational else {}))

    def final_cells(b,A,Be,U,W,H,back,recs=None):
        size = (len(U)-1)//2
        saved = {}
        banks = recs["banks"] if back else [b.alloc_qubits(12) for _ in range(slots)]
        saved["banks"] = banks
        for i in (reversed(range(size)) if back else range(size)):
            m = places[i]
            J = chart(len(A),m.d)
            transform(b,A,J)
            transform(b,Be,J)
            a,s = A[:2], Be[:2]
            u,w = U[2*i:2*i+2], W[2*i:2*i+2]
            theta = f['hroot'](i)
            if not back:
                f['top_trace'](b,a,w,H,i,size)
            f['add_pair'](b,a,s,theta)
            f['add_pair'](b,w,u,theta)
            with evaluate(b,m.x,[a,s,u,w]):
                saved[i] = []
                for k in (reversed(range(2)) if back else range(2)):
                    ak,sk,uk,wk = a[k],s[k],u[k],w[k]
                    if banks:
                        from sys import path
                        directory=str(HERE.parent/"20261117T214100Z-dqi-parent-batch")
                        if directory not in path:path.insert(0,directory)
                        from gauge_unit import zero_flag
                        flag=b.alloc_qubits(1)[0]
                        zero_flag(b,sk,flag)
                        def secure(after):
                            if after:
                                for left,right in reversed(list(zip(banks,banks[1:]))):
                                    b.cswap(flag,left,right)
                                b.cswap(flag,uk,wk)
                                b.cswap(flag,wk,banks[0])
                            else:
                                b.cswap(flag,wk,banks[0])
                                b.cswap(flag,uk,wk)
                                for left,right in zip(banks,banks[1:]):
                                    b.cswap(flag,left,right)
                        if not back:secure(False)
                        for inp,target in zip(ak,sk):b.ccx(flag,inp,target)
                    if not back:
                        debt_w = deferred_scale(b,wk,sk)
                        prod(b,ak,uk,wk)
                        debt_u = deferred_scale(b,uk,sk)
                        saved[i].append((debt_w,debt_u))
                    else:
                        debt_w,debt_u = recs[i][k]
                        z = opens(b,sk,None)
                        new_u = deferred_scale(b,uk,z)
                        pay(b,uk,debt_u)
                        product_debt(b,uk,sk,new_u)
                        prod(b,ak,uk,wk)
                        new_w = deferred_scale(b,wk,z)
                        pay(b,wk,debt_w)
                        product_debt(b,wk,sk,new_w)
                        mask = hmr_word(b,z)
                        phase_inverse_twelve_polynomial(b,sk,mask)
                        b.free(mask)
                    if banks:
                        for inp,target in zip(ak,sk):b.ccx(flag,inp,target)
                        if back:secure(True)
                        zero_flag(b,sk,flag)
                        b.free(flag)
            f['add_pair'](b,w,u,theta)
            f['add_pair'](b,a,s,theta)
            if back:
                f['top_trace'](b,a,w,H,i,size)
            transform(b,Be,J,True)
            transform(b,A,J,True)
        if back:
            for bank in banks:b.free(bank)
        return saved
    f.update(fwalk=walk,final_cells=final_cells)
    if cell_hooks is not None and getattr(cell_hooks,'expose',False):
        return f, handoff
    if slots==-2:
        from twisted import install
        return install(f,v,ce,out)
    if slots==-1:
        from quotient_native import install
        install(f,BLOCK)
        return f['finish_map'],[1]
    return f['finish_map'],f['square'](f['factors'](0,8))


def install_member(v,ce,out,offset=16,slots=2):
    """Install the split terminal retaining the stated number of escrow words across the scan."""
    import fusion_hook
    import inspect
    finish=fusion_hook.make_finish_map
    installer=fusion_hook.install
    raw=inspect.getsource(installer)
    before='data=run(builder,D,N);assert builder.num_allocated_qubits==entry'
    assert raw.count(before)==1
    scope=dict(vars(fusion_hook))
    scope['make_finish_map']=lambda module: build(module,ce,out,offset,slots)
    exec(compile(raw.replace(before,before+'+'+str(12*max(0,slots))),'<split terminal lifetime>','exec'),scope)
    scope['install'](v,ce,out)
