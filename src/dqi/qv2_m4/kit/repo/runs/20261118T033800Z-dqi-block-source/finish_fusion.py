"""Check the quotient-chain numerator directly in the scan's public square multiplier."""
from collections import Counter
import json
import os
import random
import sys
import time
from quadratic import HERE,M,add,deflate,divexact,mul,pad,places,scale
from triangular_gauge import sample


def square(p):
    v=[0]*(2*len(p)-1)
    for j,x in enumerate(p):v[2*j]=M.mul(x,x)
    return M.trim(v)


def rem(p,d):return M.trim(M.pmod(p,d))


def project(a,b,y):
    frames=[];n=17
    for m in places[:8]:
        raw,why=deflate(a,b,m)
        if why:raise ZeroDivisionError(why)
        r,q,c,e=raw;hs=[m.quotient(m.reduce(t),m.reduce(c)) for t in y]
        y=[pad(divexact(add(t,mul(c,h)),m.poly),n-2) for t,h in zip(y,hs)]
        frames.append((a,b,r,q,c,e,m,hs));a,b=c,e;n-=2
    if not b or not b[0]:raise ZeroDivisionError('terminal gcd')
    return frames,[M.div(t[0],b[0]) for t in y]


def direct(frames,leaf,border,q_top,negative=False):
    S=[[],[]];T=[[x] for x in leaf];P=[1];coords=[{},{}];lead_s=[0,0];lead_t=leaf[:];checks=0
    for i in reversed(range(8)):
        a,b,r,q,c,e,m,hh=frames[i];out_s=[];out_t=[]
        for k in range(2):
            s=add(mul(m.poly,S[k]),add(mul(q,T[k]),mul(P,hh[k])))
            t=add(mul(m.poly,T[k]),mul(r,s) if not (negative and i==0) else [])
            if not negative:
                unit=m.reduce(c)
                z=m.quotient(hh[k],q)
                raw=add(m.reduce(T[k]),m.reduce(mul(P,z)))
                xi=m.quotient(m.reduce(raw),unit);coords[k][i]=xi
                for j in range(i,8):
                    place=frames[j][6];v=coords[k][j]
                    assert place.reduce(s)==place.reduce(mul(b,v))
                    assert place.reduce(t)==place.reduce(mul(a,v))
                lead_s[k]^=M.mul(q[1],lead_t[k])^hh[k][1];lead_t[k]^=M.mul(r[1],lead_s[k])
                assert lead_s[k]==pad(s,2*(8-i))[-1]
                assert lead_t[k]==pad(t,2*(8-i)+1)[-1];checks+=8-i
            out_s.append(s);out_t.append(t)
        P=mul(P,m.poly);S=out_s;T=out_t
    even=add(add(S[0],scale(T[0],q_top)),add([0]+T[1],scale(P,border)))
    odd=add(add(S[1],scale(T[1],q_top)),T[0]);z=[0]*35
    for i,x in enumerate(even):z[2*i]=M.mul(x,x)
    for i,x in enumerate(odd):z[2*i+1]=M.mul(x,x)
    return M.trim(z),square(P),checks


if __name__=='__main__':
    mode,ns,sd=sys.argv[1:];shots=int(ns);seed=int(sd);rng=random.Random(seed);start=time.monotonic();counts=Counter()
    rows={int(r[0]):(float(r[1]),list(map(int,r[2:]))) for r in (z.split() for z in (HERE.parent/'20261117T214100Z-dqi-direct-bezout'/'physical_locators.dat').read_text().splitlines())}
    print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),mode=mode)),flush=True)
    for case in range(shots):
        a,b=sample(rng,mode,rows);qt=rng.randrange(4096);h=rng.randrange(4096);y=[[rng.randrange(4096) for j in range(17)] for k in range(2)]
        even=add(b,scale(a,qt));D=add(square(even),[0]+square(a));U=add(y[0],scale(a,h));N=add(square(U),[0]+square(y[1]));Dprime=square(a)
        try:frames,leaf=project(a,b,y)
        except ZeroDivisionError as err:counts[str(err)]+=1;continue
        K,Mpub,certs=direct(frames,leaf,h,qt)
        assert len(K)<=35 and rem(add(mul(Dprime,K),mul(Mpub,N)),D)==[]
        counts['complete_scan_polynomial']+=1;counts['fixed_CRT_coordinates']+=certs
        if case%47==0:
            bad,_,_=direct(frames,leaf,h,qt,True);counts['negative_trials']+=1;counts['negative_failed']+=bool(rem(add(mul(Dprime,bad),mul(Mpub,N)),D))
    out=dict(mode=mode,shots=shots,seed=seed,counts=dict(counts),seconds=time.monotonic()-start,pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),evidence='Whole numerator for the original 35-word scan, including odd top border. Dprime*K=Mpublic*N mod D on all inputs, every retained local CRT value checked. Structural logic only, native cost and fixed-width restoration pending.')
    (HERE/f'finish_fusion_{seed}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
