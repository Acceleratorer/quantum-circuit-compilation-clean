"""A 17-evaluation derivative plus its degree-six value in the native GF(2^24)."""
from functools import cache, reduce
from operator import xor
import json
from pathlib import Path

def add(items):
    return reduce(xor, items, 0)

def apply(rows, value):
    return sum(((value & row).bit_count() & 1) << i for i,row in enumerate(rows))

def rows(columns, width):
    return tuple(sum(((column >> i) & 1) << j for j,column in enumerate(columns)) for i in range(width))

def invrows(columns):
    n=len(columns)
    mat=[r | (1 << (n+i)) for i,r in enumerate(rows(columns,n))]
    for i in range(n):
        k=next((k for k in range(i,n) if mat[k]>>i & 1),None)
        if k is None:raise ValueError('singular')
        mat[k],mat[i]=mat[i],mat[k]
        for j in range(n):
            if j!=i and mat[j]>>i & 1:mat[j]^=mat[i]
    return tuple(r >> n for r in mat)

def small_mul(a,b):
    out=0
    for _ in range(4):
        if b&1:out^=a
        b>>=1;a=(a<<1)^(19 if a&8 else 0)
    return out

def power(x,n,product):
    z=1
    while n:
        if n&1:z=product(z,x)
        x=product(x,x);n>>=1
    return z

@cache
def geometry():
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'/'dqi_scale'))
    import gf as ground
    def kprod(a,b):
        A,B=a&4095,a>>12;C,D=b&4095,b>>12
        r=ground.mul(B,D)
        return ground.mul(A,C)^ground.mul(2048,r)^((ground.mul(A,D)^ground.mul(B,C)^r)<<12)
    beta=next(z for z in range(2,4096) if power(z,4,kprod)^z^1==0)
    small=[power(beta,i,kprod) for i in range(4)]
    def emb(k):return add(v for j,v in enumerate(small) if k>>j&1)
    for t in range(4096,16384):
        powers=[power(t,i,kprod) for i in range(23)]
        try:invrows([kprod(v,powers[j]) for j in range(6) for v in small])
        except ValueError:continue
        break
    else:raise AssertionError
    def sample(j,v):
        ordinary=kprod(emb(v),powers[j]);deriv=kprod(emb(v),powers[j-1]) if j%2 else 0
        return ordinary,deriv
    encode=invrows([a | (b<<24) for j in range(12) for v in (1,2,4,8) for a,b in [sample(j,v)]])
    points=tuple(range(16))+(None,)
    def ev(j,v,x,hi):
        if x is None:return v if j==hi else 0
        return small_mul(v,power(x,j,small_mul))
    def get_input(z,x):
        poly=apply(encode,z)
        return add(ev(j,(poly>>(4*j))&15,x,11) for j in range(12))
    inputs=[rows([get_input(1<<i,x) for i in range(48)],4) for x in points]
    obs=[];deriv=[]
    for j in range(23):
        for w in (1,2,4,8):
            val,d=sample(j,w)
            obs.append(val | sum(ev(j,w,x,22)<<(24+4*i) for i,x in enumerate(points)))
            deriv.append(d)
    inverse=invrows(obs)
    def read(z):
        c=apply(inverse,z)
        return add(v for j,v in enumerate(deriv) if c>>j&1)
    # Construct the nine-product tower algorithm for GF16.
    w=next(z for z in range(2,16) if small_mul(z,z)^z^1==0)
    h=next(z for z in range(2,16) if small_mul(z,z)^z^w==0)
    base=[1,w,h,small_mul(w,h)];chg=invrows(base)
    small_terms=[]
    selectors=((1,2),(4,8),(5,10))
    tuples=[(i,j) for i,j in selectors for i,j in ((i,i),(j,j),(i^j,i^j))]
    for gi,(lm,rm) in enumerate(tuples):
        # Derive the Karatsuba interpolation image by symbolic expansion in the two quadratic towers.
        def inner(z):
            aa,bb,cc=(int(gi==n+z) for n in range(3))
            return aa^bb^((aa^cc)<<1)
        e0,e1,es=inner(0),inner(3),inner(6)
        wt=small_mul(e0&1,1)^small_mul((e0>>1)&1,w)
        hi=small_mul(e1&1,1)^small_mul((e1>>1)&1,w)
        mix=small_mul(es&1,1)^small_mul((es>>1)&1,w)
        wt^=small_mul(w,hi)^small_mul(h,mix^((e0&1)^small_mul((e0>>1)&1,w)))
        small_terms.append((add(chg[i] for i in range(4) if lm>>i&1),add(chg[i] for i in range(4) if rm>>i&1),wt))
    def calc(terms,a,b):
        return add(w for l,r,w in terms if (l&a).bit_count()%2 and (r&b).bit_count()%2)
    assert all(calc(small_terms,a,b)==small_mul(a,b) for a in range(16)for b in range(16))
    terms=[]
    for idx,mat in enumerate(inputs):
        for l,r,w in small_terms:
            terms.append((add(mat[k] for k in range(4) if l>>k&1),add(mat[k] for k in range(4) if r>>k&1),read(w<<(24+4*idx))))
    terms=tuple(term for term in terms if term[-1]);valuecols=tuple(read(1<<i) for i in range(24))
    return terms,valuecols,kprod,t

def check():
    import random
    terms,cols,mul,t=geometry();r=random.Random(15407)
    trial=[(1<<j,1<<k) for j in range(48)for k in range(48)]
    trial.extend((r.getrandbits(48),r.getrandbits(48))for _ in range(4096))
    for z,y in trial:
        s,a=z&0xffffff,z>>24;u,w=y&0xffffff,y>>24
        uv=mul(s,u)
        deriv=add(v for l,h,v in terms if (z&l).bit_count()%2 and (y&h).bit_count()%2)
        deriv^=add(c for j,c in enumerate(cols) if uv>>j&1)
        assert deriv==mul(s,w)^mul(a,u)
    report=dict(ordinary_products=99,derivative_terms=len(terms),fused=99+len(terms),tower_generator=t,checked=len(trial))
    print(report);Path(__file__).with_name('terminal_jet_tensor.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':check()
