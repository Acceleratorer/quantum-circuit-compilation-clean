"""Solve the physical Bezout system without retaining an old payload at regular cuts."""
from argparse import ArgumentParser
from collections import Counter
import json
import os
import random
import time
from quadratic import HERE,M,add,deflate,divexact,mul,pad,places,scale
from source_maps import dot,inverse,mv


def dual_join(c,m,lo,hi):
    """Solve m^T z=lo and [C,xC]^T z=hi in the monomial basis."""
    n=len(lo)+2
    ex=[1,0];ey=[0,1];v=[0,0]
    for j,z in enumerate(lo):
        ex.append(M.mul(m.d,ex[j])^ex[j+1])
        ey.append(M.mul(m.d,ey[j])^ey[j+1])
        v.append(z^M.mul(m.d,v[j])^v[j+1])
    cx=[0]+c
    cross=[[dot(p,ex),dot(p,ey)] for p in (c,cx)]
    x,y=mv(inverse(cross),[hi[0]^dot(c,v),hi[1]^dot(cx,v)])
    return [u^M.mul(x,a)^M.mul(y,b) for u,a,b in zip(v,ex,ey)]


def solve(a,b,t,rhss,n,counts,negative):
    a=pad(a,n+1);b=pad(b,n)
    lead=a[n]^M.mul(t,b[n-1])
    if not lead:raise ZeroDivisionError
    if n==1:
        if not b[0]:
            counts['singular_source_gcd']+=1;raise ZeroDivisionError
        return [[M.div(y[0],M.mul(lead,b[0]))] for y in rhss]
    stage=(17-n)//2;m=places[stage]
    result,why=deflate(a,b,m)
    if why:counts[why]+=1;raise ZeroDivisionError
    raw_r,q,c,e=result;g=pad(c,n-1)[-1];el=pad(e,n-2)[-1]
    r=raw_r[1]^t;gs=g^M.mul(r,el);q1=q[1]
    assert lead==gs^M.mul(M.mul(r,g),q1)
    low=[];high=[]
    for y in rhss:
        h=m.quotient(m.reduce(y),m.reduce(c));high.append(h)
        low.append(pad(divexact(add(y,mul(c,h)),m.poly),n-2))
    hinv=inverse(M.bezout(m.poly,q))
    if gs:
        counts['regular']+=1;alpha=M.div(r,gs);beta=M.div(M.mul(r,g),lead)
        diag=[]
        for h,y in zip(high,low):
            v=M.mul(alpha,y[-1]);h=[u^M.mul(w,v) for u,w in zip(h,q)]
            z=mv(hinv,h);z[1]^=M.mul(beta,h[1]);diag.append(z)
        x=solve(c,e,r,low,n-2,counts,negative)
        for zl,zh in zip(x,diag):
            if not (negative and n==17):zl[-1]^=M.mul(alpha,dot(q,zh))
    else:
        counts['exception_'+str(stage)]+=1
        assert r and g and el and q1
        x=solve(c,e,0,low,n-2,counts,negative);diag=[]
        for y,h,z in zip(low,high,x):
            qh=mv(hinv,h);lam=M.div(y[-1]^M.mul(g,h[1]),lead)
            v=M.mul(r,lam);z[-1]^=M.div(v,g);qh[-1]^=v;diag.append(qh)
    return [dual_join(c,m,l,h) for l,h in zip(x,diag)]


def sample(rng,mode,rows):
    if mode=='directed':
        # Force the top Schur pivot to vanish while the full leading unit stays valid.
        m=places[0];r=[rng.randrange(4096),rng.randrange(1,4096)]
        q=[rng.randrange(4096),rng.randrange(1,4096)]
        e=[rng.randrange(4096) for _ in range(14)]+[rng.randrange(1,4096)]
        c=[rng.randrange(4096) for _ in range(15)]+[M.mul(r[1],e[-1])]
        b=add(mul(m.poly,e),mul(q,c));a=add(mul(m.poly,c),mul(r,b))
        return a,b
    if mode=='weighted':
        wt=rng.choices(list(rows),weights=[x[0] for x in rows.values()])[0]
        d=[1]
        for p in rng.sample(range(1,4096),wt):d=mul(d,[p,1])
        d=scale(mul(d,rows[wt][1]),rng.randrange(1,4096))
        a=[M.sqrt(z) for z in d[1::2]];b=[M.sqrt(z) for z in d[::2]]
        return a,add(b,scale(a,M.div(b[-1],a[-1])))
    return [rng.randrange(4096) for _ in range(17)]+[rng.randrange(1,4096)],[rng.randrange(4096) for _ in range(17)]


if __name__=='__main__':
    ap=ArgumentParser();ap.add_argument('mode',choices=['directed','weighted','generic']);ap.add_argument('shots',type=int);ap.add_argument('seed',type=int);args=ap.parse_args()
    path=HERE.parent/'20261117T214100Z-dqi-direct-bezout'/'physical_locators.dat'
    rows={int(r[0]):(float(r[1]),list(map(int,r[2:]))) for r in (l.split() for l in path.read_text().splitlines())}
    start=time.monotonic();rng=random.Random(args.seed);stats=Counter();passed=0;nb=0;neg=0
    print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),mode=args.mode)),flush=True)
    for i in range(args.shots):
        a,b=sample(rng,args.mode,rows);u=[[rng.randrange(4096) for _ in range(17)] for _ in range(2)];mat=M.bezout(a,b);ys=[mv(mat,x) for x in u]
        try:
            z=solve(a,b,0,ys,17,stats,False)
        except ZeroDivisionError:stats['singular_or_residue']+=1;continue
        assert z==u,(i,z,u);passed+=1
        if i%29==0 and args.mode!='directed':
            nb+=1;neg+=solve(a,b,0,ys,17,Counter(),True)!=u
    out=dict(mode=args.mode,shots=args.shots,seed=args.seed,two_rhs_correct=passed,negative_cases=nb,negative_detections=neg,stages=dict(stats),seconds=time.monotonic()-start,pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),claim='No saved payload field on regular cuts; rare singular Schur chart uses one extra saved-coordinate combination in this algebraic reference. No gate count.')
    (HERE/f'gauge_solve_{args.seed}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
