"""Build charts directly against the real source's head view and dirty joint target."""
from functools import cache
from pathlib import Path
import json
import numpy as np
from aligned_wronskian import F,M,plus,sc,divide,cj,geometry,coords,charts,kap
P=Path(__file__).resolve().parent
MASK=(1<<24)-1
PAIR_FILE=P/'aligned_paired_field_terms.json'
def un(v):return v&4095,v>>12
def pack(x):return x[0]|(x[1]<<12)
def pull(m,cols):return sum(((m&x).bit_count()%2)<<i for i,x in enumerate(cols))
@cache
def make(a):
    return charts([a],np.random.default_rng(49101+a))[a]
def half_terms(a,j,typ,real):
    from tower_inverse import kernel
    kt=F.sqrt(kap(a)^kap(j));c=make(a);t=c['t'][0 if typ=='A' else j+1];z0,z1,n0,n1,A,B,C,D,k,U,V=geometry(t)
    if typ=='B':U,V=sc(U,kt),sc(V,kt)
    h=[coords(F.ksqrt(un(1<<i)),z0,z1)for i in range(24)]
    n=[coords(un(1<<i),n0,n1)for i in range(24)]
    body=[];pair=json.loads(PAIR_FILE.read_text())['terms']
    for idx,M0,W in ((0,plus(A,C),U),(1,plus(D,B),V)):
        hcols=[x[idx]for x in h];ncols=[x[idx]for x in n]
        for nm,hm,out in pair:
            ordinary=out&4095;mixed=out>>12
            body.append((pull(hm,hcols),pull(nm,ncols),pack(sc(M0,mixed))|(pack(sc(W,ordinary))<<24)))
    sq=lambda x:M.mul(x,x)
    hcols=[sq(x^y)for x,y in h];ncols=[M.mul(k,u)^v for u,v in n]
    body.extend((pull(x,hcols),pull(y,ncols),pack(sc(B,v)))for x,y,v in kernel(12))
    assert len(body)==2*len(pair)+42 and all(a and b and c for a,b,c in body)
    return body
@cache
def native_terms(a,j,kind):return half_terms(a,j,kind,True)
def update(ex,n,e,d,a,initial):
    from field_tensor import accumulate_product
    c=make(a);sk=F.sqrt(kap(a)^kap(0))if initial else 1
    def res(v):
        t=F.ksqrt(un(v));return pack(sc(plus(F.kmul(c['c'],t),F.kmul(c['d'],cj(t))),sk))
    terms=[(u,v,res(w))for u,v,w in ex.A.tensor24(2048)]
    accumulate_product(ex.b,n,d,e,[(u,v,w)for u,v,w in terms if w])
def altered(ex,head,n,d,e,j,a,kind,reverse):
    from field_tensor import accumulate_product
    import kickmix as km
    b=ex.b;k=kap(j)^kap(a)
    if reverse:b.swap(n,d);ex.RQ.public_scale(b,d,k)
    ex.RQ.node_view(b,head,a)
    accumulate_product(b,head,n,km.array([*d,*e]),native_terms(a,j,kind))
    ex.RQ.node_view(b,head,a)
    if not reverse:ex.RQ.public_scale(b,d,M.inv(k));b.swap(n,d)
def patch(src,nodes,pair_file=None):
    def add(anchor,addition,after=False):
        nonlocal src
        assert src.count(anchor)==1,anchor
        src=src.replace(anchor,anchor+addition if after else addition+anchor)
    a=src.index('    def joint_half(');end=src.index('\n',a)
    # The public source calls the old source node b and the target a.
    src=src[:end]+f'\n        if a in {nodes!r}:return aligned.altered(self,head,n,d,e,b,a,kind,reverse)'+src[end:]
    pre='            self.single(words, a, W1, W2, carry)\n'
    add(pre,f'            if a in {nodes!r}:aligned.update(self,W1,W2,carry,a,True)\n')
    end='                self.old_double(words, bb, a, W1, W2, carry)\n'
    add(end,f'            if a in {nodes!r}:aligned.update(self,W1,W2,carry,a,False)\n',True)
    ret='            for bb in reversed(range(1, a)):\n'
    add(ret,f'            if a in {nodes!r}:aligned.update(self,W1,W2,carry,a,False)\n')
    end='            self.single(words, a, W1, W2, carry, reverse=True)\n'
    add(end,f'            if a in {nodes!r}:aligned.update(self,W1,W2,carry,a,True)\n',True)
    prefix='import sys\nsys.path.insert(0,'+repr(str(P))+')\nimport aligned_native as aligned\n'
    if pair_file:prefix+='from pathlib import Path as _P\naligned.PAIR_FILE=_P('+repr(str(pair_file))+')\n'
    return prefix+src
