"""Two-degree source deflation for the physical, two-RHS Bezout solver."""
import argparse
from collections import Counter
import json
import os
import random
import time
from source_panel import HERE,M,add,divexact,mul,physical,scale
from source_maps import inverse, mv, transpose


class Place:
    def __init__(self, delta):
        assert M.trace(delta)==1
        self.d=delta;self.poly=[delta,1,1]
    def reduce(self,p):
        a=M.pmod(p,self.poly) if p else []
        return tuple((a+[0,0])[:2])
    def quotient(self,u,v):
        a,b=u;c,d=v; den=M.mul(c,c)^M.mul(c,d)^M.mul(self.d,M.mul(d,d))
        if not den:raise ZeroDivisionError
        return [M.div(M.mul(a,c^d)^M.mul(self.d,M.mul(b,d)),den),M.div(M.mul(a,d)^M.mul(b,c),den)]


places=[Place(i) for i in range(4096) if M.trace(i)==1][:32]


def deflate(a,b,m):
    ra=m.reduce(a);rb=m.reduce(b)
    if rb==(0,0):return None,'first_residue'
    r=m.quotient(ra,rb);c=divexact(add(a,mul(r,b)),m.poly);rc=m.reduce(c)
    if rc==(0,0):return None,'second_residue'
    q=m.quotient(rb,rc);e=divexact(add(b,mul(q,c)),m.poly)
    assert add(mul(m.poly,e),mul(q,c))==M.trim(b)
    assert add(mul(m.poly,c),mul(r,b))==M.trim(a)
    return (r,q,c,e),None


def pad(x,n):return list(x)+[0]*(n-len(x))


def solve_core(a,b,rhss,stats,wrong=False,swap=0,repair=False):
    n=len(a)-1
    if n==1:
        un=M.mul(a[-1],b[0]);return [[M.div(y[0],un)] for y in rhss]
    step=(17-n)//2
    options=places[2*step:2*step+(2 if swap else 1)]
    for selection,m in enumerate(options):
        row,reason=deflate(a,b,m)
        if row is None:stats[reason]+=1;continue
        r,q,c,e=row
        if len(c)!=n-1:
            stats['leading_zero']+=1;continue
        break
    else:
        if not repair or row is None:raise ZeroDivisionError
    g=pad(c,n-1)[-1];flag=int(repair and not g)
    child_a=add(c,[0]+e) if flag else c
    if flag:stats['flag_'+str(step)]+=1
    assert len(child_a)==n-1
    stats['alternate_'+str(selection)]+=1
    # W columns m*x^j, C, xC. Solve W^{-1} by reducing all input rows
    # modulo m and dividing by C(m); reconstruct low quotient by public m.
    high=[];low=[]
    for y in rhss:
        z=m.quotient(m.reduce(y),m.reduce(c));h=divexact(add(y,mul(c,z)),m.poly)
        high.append(z);low.append(pad(h,n-2))
    # B(A,B) in W coordinates = B0 + r1*[E;Q] [E;Q]^T.
    # B0 consists of B(C,E) and B(m,Q). Its inverse sends [E;Q] to
    # [last/lead(C);last] because the last column of both Bezout blocks
    # contains the corresponding second argument times the first's lead.
    low_x=solve_core(child_a,e,low,stats,wrong,swap,repair)
    h=M.bezout(m.poly,q);h_inv=inverse(h)
    invlc=M.inv(child_a[-1]); original_lead=M.mul(g,1^M.mul(r[1],q[1]))^M.mul(r[1],pad(e,n-2)[-1]);assert original_lead==a[-1]
    # W^{-T} as a descending linear recurrence with a public modulus.
    # For the mathematical check, use the two scalar dual coordinates to
    # choose x0,x1 of the public recurrence m0*xj + xj+1 + xj+2 = low_j.
    r0=[1,0];r1=[0,1]
    for j in range(n-2):
        r0.append(M.mul(m.d,r0[j])^r0[j+1]);r1.append(M.mul(m.d,r1[j])^r1[j+1])
    c0=pad(c,n);c1=[0]+pad(c,n-1)
    def dot(a,b):
        s=0
        for u,v in zip(a,b):s^=M.mul(u,v)
        return s
    du=inverse([[dot(c0,r0),dot(c0,r1)],[dot(c1,r0),dot(c1,r1)]])
    out=[]
    for ylow,yhigh,zlow in zip(low,high,low_x):
        zhigh=mv(h_inv,yhigh)
        # h = v.T B0^-1 y = (last/lc, last) dot y. No variable dot product.
        lam=M.div(ylow[-1]^M.mul(g,yhigh[-1]),original_lead)
        t=M.mul(r[1],lam) if not wrong else 0
        sig=yhigh[-1]^lam^M.mul(q[1],t)
        zlow[-1]^=M.mul(t^(sig if flag else 0),invlc);zhigh[-1]^=t
        v=[0,0]
        for j,z in enumerate(zlow):v.append(z^v[j+1]^M.mul(m.d,v[j]))
        u0,u1=mv(du,[zhigh[0]^dot(c0,v),zhigh[1]^dot(c1,v)])
        out.append([v0^M.mul(u0,x)^M.mul(u1,y) for v0,x,y in zip(v,r0,r1)])
    return out


def main():
    pp=argparse.ArgumentParser();pp.add_argument('--shots',type=int,required=True);pp.add_argument('--seed',type=int,required=True);pp.add_argument('--physical',action='store_true');pp.add_argument('--two-places',action='store_true');pp.add_argument('--repair',action='store_true');aa=pp.parse_args();t0=time.monotonic();rng=random.Random(aa.seed);stats=Counter();exact=0;negative=0
    print('quadratic source and two RHS',os.getpid(),sorted(os.sched_getaffinity(0)),flush=True)
    for j in range(aa.shots):
        if aa.physical:
            raw=physical(rng,[35,34,33,32,29,25,21,19][j%8]);
            if raw is None:stats['upstream_reference_failure']+=1;continue
            D=raw[0];a=[M.sqrt(z) for z in D[1::2]];b=[M.sqrt(z) for z in D[::2]];b=add(b,scale(a,M.div(b[-1],a[-1])))
        else:
            a=[rng.randrange(4096) for _ in range(17)]+[rng.randrange(1,4096)];b=[rng.randrange(4096) for _ in range(17)]
        u=[[rng.randrange(4096) for _ in range(17)] for i in range(2)];m=M.bezout(a,b);y=[mv(m,x) for x in u]
        try:
            x=solve_core(a,b,y,stats,swap=aa.two_places,repair=aa.repair)
            if j%16==0:negative+=solve_core(a,b,y,Counter(),True,aa.two_places,aa.repair)!=u
        except (ZeroDivisionError,IndexError):stats['failed_source']+=1;continue
        assert x==u,(x,u);exact+=1
    out=dict(evidence='diagnostic direct solve, generator matrices created only for truth inputs; actual gap selection/measurements not priced',seed=aa.seed,shots=aa.shots,exact_two_rhs=exact,negative_rejections=negative,counts=dict(stats),source_words=35,core_degrees=list(range(17,0,-2)),seconds=time.monotonic()-t0,pid=os.getpid(),cpus=sorted(os.sched_getaffinity(0)))
    (HERE/f'quadratic_{aa.seed}.json').write_text(json.dumps(out,indent=1)+'\n');print(out,flush=True)


if __name__=='__main__':main()
