"""Emit a Wronskian coordinate change having one base-field output word."""
from functools import cache
import json
from aligned_native import P,F,M,pack,un,pull,plus,cj,sc,kap

@cache
def data():
    return {int(a):v for a,v in json.loads((P/'low_endpoint_charts.json').read_text()).items()}

def chart(a):
    record=data()[a];u,w=record['t']
    return dict(c=tuple(record['c']),d=(1,0),t=[(u,w),*((u^M.inv(F.sqrt(kap(j)^kap(a))),w)for j in range(a))])

@cache
def endpoint_terms(a,initial):
    from tower_inverse import kernel
    c=chart(a)['c'];sk=F.sqrt(kap(a)^kap(0))if initial else 1
    def g(x):return sc(plus(F.kmul(c,x),cj(x)),sk)
    image=g((1,0))
    if not any(image):image=g((0,1))
    bit=0 if image[0] else 1
    def project(x):
        y=g(x);v=M.div(y[bit],image[bit]);assert sc(image,v)==y;return v
    cols=[F.ksqrt(un(1<<i)) for i in range(24)]
    body=[]
    for part,v in enumerate(((1,0),(0,1))):
        xx=[x[part]for x in cols]; yy=[project(F.kmul(v,x))for x in cols]
        for u,t,w in kernel(12):body.append((pull(u,xx),pull(t,yy),pack(sc(image,w))))
    assert len(body)==84
    for i in range(24):
        for j in range(24):
            y=0
            for u,t,w in body:
                if u>>i&1 and t>>j&1:y^=w
            assert y==pack(g(F.kmul(cols[i],cols[j])))
    return body

def install():
    import aligned_native as aligned
    original_make,original_update=aligned.make,aligned.update
    def make(a):return chart(a) if data()[a]['fully_split'] else original_make(a)
    def update(ex,n,e,d,a,initial):
        from field_tensor import accumulate_product
        if not data()[a]['fully_split']:return original_update(ex,n,e,d,a,initial)
        return accumulate_product(ex.b,n,d,e,endpoint_terms(a,initial))
    aligned.make=make;aligned.update=update
