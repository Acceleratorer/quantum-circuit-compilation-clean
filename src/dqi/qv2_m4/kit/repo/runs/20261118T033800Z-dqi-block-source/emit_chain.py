# SPDX-License-Identifier: Apache-2.0
"""A complete bounded-width two-RHS inverse Bezout map with a semiseparable centre."""
from pathlib import Path
pair_path=Path(__file__).resolve().with_name("emit_pairwalk.py")
body,main_code=pair_path.read_text().split('\nstart=time.monotonic();n=args.degree;',1)
exec(compile(body,str(pair_path),'exec'))
from tower_inverse import invert_inplace
from chain_middle import solve_chain


def mul_keep(b,s,t):
    v=b.alloc_qubits(12);xor_product(b,s,t,v);b.swap(v,t);m=b.alloc_bits(12);b.hmr(v,m);b.free(v)
    return m


def scalar_div(b,s,v,reverse=False,debt=None):
    if not reverse:invert_inplace(b,s)
    m=[mul_keep(b,s,w) for w in v]
    if reverse:
        for x,w in zip(debt,v):b.cz(x,w);b.free(x)
        invert_inplace(b,s)
        for x,w in zip(m,v):phase_product(b,s,w,x,kernel(12));b.free(x)
    invert_inplace(b,s);return None if reverse else m


def phase_or_value_carry(b,frames,ds,outs,phase):
    """Accumulate final t = sum_i r_i * (d_leaf + sum_{j>=i} high'_j1)."""
    prefix=[r[1] for r,q,h,delta in frames]
    for i,(r,q,h,delta) in enumerate(frames):
        if i:b.cx(prefix[i-1],prefix[i])
        for k,(head,t) in enumerate(zip(h,outs)):
            if phase:phase_product(b,prefix[i],head[1],t,kernel(12))
            else:xor_product(b,prefix[i],head[1],t)
        if i==len(frames)-1:
            for d,t in zip(ds,outs):
                if phase:phase_product(b,prefix[i],d,t,kernel(12))
                else:xor_product(b,prefix[i],d,t)
    for i in reversed(range(1,len(prefix))):b.cx(prefix[i-1],prefix[i])


def diagonal(b,frames,reverse,recs):
    out=[]
    for i,(r,q,h,delta) in enumerate(frames):
        if reverse:
            for pair in h:h_one(b,pair)
        native_place(b,[q,*h],delta);qw=flat(q);targets=[flat(z) for z in h]
        if reverse:CE.restore_multi(O,b,qw,list(zip(targets,recs[i])),[],[])
        else:out.append(multi_div(b,qw,targets))
        native_place(b,[q,*h],delta)
        if not reverse:
            for pair in h:h_one(b,pair,True)
    return out


def centre(b,A,B,Y,frames,reverse,prior):
    a=A[1];p=B[0];ds=[v[0] for v in Y]
    if reverse:
        diagonal(b,frames,True,prior['high'])
        scalar_div(b,p,ds,True,prior['leaf'])
        ts=[b.alloc_qubits(12) for _ in ds];phase_or_value_carry(b,frames,ds,ts,False)
        for r,q,h,d in reversed(frames):
            for v,t,head in zip(ds,ts,h):
                b.cx(head[1],v);xor_product(b,q[1],t,head[1]);xor_product(b,q[0],t,head[0]);xor_product(b,r[1],v,t)
            xor_product(b,q[1],a,p);xor_product(b,r[1],p,a)
        for t in ts:b.free(t)
        scalar_div(b,a,ds,True,prior['root'])
        for r,q,h,d in frames:
            xor_product(b,r[1],p,a);xor_product(b,q[1],a,p)
            for v,head in zip(ds,h):xor_product(b,a,head[1],v)
        return None
    for r,q,h,d in reversed(frames):
        for v,head in zip(ds,h):xor_product(b,a,head[1],v)
        xor_product(b,q[1],a,p);xor_product(b,r[1],p,a)
    top=scalar_div(b,a,ds);ts=[b.alloc_qubits(12) for _ in ds]
    for r,q,h,d in frames:
        for v,t,head in zip(ds,ts,h):
            xor_product(b,r[1],v,t);xor_product(b,q[0],t,head[0]);xor_product(b,q[1],t,head[1]);b.cx(head[1],v)
        xor_product(b,r[1],p,a);xor_product(b,q[1],a,p)
    tm=[b.alloc_bits(12) for _ in ts]
    for t,m in zip(ts,tm):b.hmr(t,m);b.free(t)
    phase_or_value_carry(b,frames,ds,tm,True)
    for m in tm:b.free(m)
    leaf=scalar_div(b,p,ds);high=diagonal(b,frames,False,None)
    return dict(root=top,leaf=leaf,high=high)


def whole_truth(a,b,ys,n0,n):
    if not a[-1]:raise ZeroDivisionError('original leading')
    z=solve_chain(a,b,ys)
    mat=M.bezout(a,b)
    assert all(mv(mat,x)==y for x,y in zip(z,ys))
    return z


MIDDLE=centre
truth=whole_truth
main_code=main_code.replace("'pairwalk.json'","'native_chain.json'").replace('Full physical source A/B and two dirty payloads, both true W triangular orientations and all source reconstruction, native forward and reverse. Central matrix replaced by identity for this cost separating experiment. Border and gap body excluded.','Full physical 17x17 (or reduced) inverse Bezout map, two independent dirty RHS, central scalar recurrence, source reconstruction, all reverse HMR and marked phase. Outer D,N border excluded.')
exec(compile('\nstart=time.monotonic();n=args.degree;'+main_code,str(pair_path),'exec'))
