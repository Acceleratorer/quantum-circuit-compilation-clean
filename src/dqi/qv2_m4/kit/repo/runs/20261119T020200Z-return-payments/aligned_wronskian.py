"""Factor both physical outputs after a norm-one Frobenius endpoint correction."""
from functools import cache
from pathlib import Path
import argparse
import json
import random
import time
import numpy as np
from wronskian_potential import F,M,plus,cj,sc,tr,physical,kap,tensors
P=Path(__file__).resolve().parent
O=(1,0)
Z=(0,0)
def norm(x):return F.kmul(x,cj(x))[0]
def divide(x,y):return F.kmul(x,F.kinv(y))
def residual(t,z,n):
    return plus(F.kmul(plus(F.kmul(t,z),cj(z)),n),cj(F.kmul(z,n)))
def roots(t):
    roots=[]
    for z in [(1,0),*((u,1)for u in range(4096))]:
        arg=plus(F.kmul(t,z),cj(z))
        if norm(arg)==norm(z):
            ratio=divide(cj(z),arg)
            n=plus(O,ratio) if ratio!=O else O
            assert residual(t,z,n)==Z and n!=Z
            roots.append((z,n))
    return roots
def coords(v,x,y):
    det=M.mul(x[0],y[1])^M.mul(x[1],y[0]);assert det
    return M.div(M.mul(v[0],y[1])^M.mul(v[1],y[0]),det),M.div(M.mul(v[1],x[0])^M.mul(v[0],x[1]),det)
def charts(nodes,rng):
    trace=np.array([tr(a)for a in range(4096)]);log=np.array(M.LOG);exp=np.array([M.EXP[i%4095]for i in range(8191)])
    def mul(a,b):return np.where((a!=0)&(b!=0),exp[log[a]+log[b]],0)
    def inv(a):return np.where(a!=0,exp[4095-log[a]],0)
    rec={}
    for a in nodes:
        betas=[0,*[M.inv(F.sqrt(kap(j)^kap(a)))for j in range(a)]]
        found=False
        for perm in np.array_split(rng.permutation(4096),128):
            u,w=np.meshgrid(np.arange(4096),perm);good=np.ones(u.shape,dtype=bool)
            for bj in betas:
                t=u^bj;n=mul(t,t)^mul(t,w)^mul(2048,mul(w,w))
                xx=n^w;yy=mul(2048,n)^t^mul(2049,w)
                mask=(n!=0)&(trace[mul(mul(xx,yy),mul(inv(n),inv(n)))]==0)
                good &= mask
            ix=np.flatnonzero(good)
            if len(ix):
                p=int(ix[0]);t0=(int(u.flat[p]),int(w.flat[p]));found=True;break
        if not found:raise ValueError(f'No norm-one chart for node {a}')
        rec[a]=dict(u=t0[0],w=t0[1],c=plus(t0,O),d=O,s=1,t=[(t0[0]^b,t0[1])for b in betas])
    return rec
@cache
def geometry(t):
    rr=roots(t);assert len(rr)==2,(t,rr)
    (z0,n1),(z1,n0)=rr
    sq0,sq1=F.kmul(z0,z0),F.kmul(z1,z1)
    A,B,C,D=[F.kmul(x,n)for x in [sq0,sq1]for n in [n0,n1]]
    k=divide(C,B);assert k[1]==0 and k[0]
    U,V=residual(t,z0,n0),residual(t,z1,n1)
    return z0,z1,n0,n1,A,B,C,D,k[0],U,V
def evaluate(t,z,n):
    z0,z1,n0,n1,A,B,C,D,k,U,V=geometry(t)
    x,y=coords(z,z0,z1);u,v=coords(n,n0,n1)
    xx=M.mul(x,x);yy=M.mul(y,y)
    p,s=M.mul(xx,u),M.mul(x,u)
    q,h=M.mul(yy,v),M.mul(y,v)
    # B*[(xx+yy)*(k*u+v)] contributes both correctly aligned cross terms.
    r=M.mul(xx^yy,M.mul(k,u)^v)
    return (plus(plus(sc(plus(A,C),p),sc(plus(D,B),q)),sc(B,r)),plus(sc(U,s),sc(V,h)))
def main(o):
    start=time.monotonic();nodes=list(map(int,o.nodes.split(',')));rr=random.Random(o.seed)
    r=charts(nodes,np.random.default_rng(o.seed));nt=0
    for rec in r.values():
        for t in rec['t']:
            for i in range(o.basis+o.random):
                if i<o.basis:
                    zz,nn=1<<(i//24),1<<(i%24);z=(zz&4095,zz>>12);n=(nn&4095,nn>>12)
                else:z=(rr.randrange(4096),rr.randrange(4096));n=(rr.randrange(4096),rr.randrange(4096))
                actual=evaluate(t,z,n);target=(F.kmul(F.kmul(z,z),n),residual(t,z,n))
                assert actual==target,(t,z,n,actual,target)
                nt+=1
    counts=physical(rr,o.law,o.shots,r)
    result=dict(args=vars(o),records=r,geometry_checked=nt,originals=counts,seconds=time.monotonic()-start)
    f=P/f'aligned_wronskian_{o.seed}.json';f.write_text(json.dumps(result,indent=1)+'\n')
    print('simultaneous',nt,'originals',counts,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('nodes');p.add_argument('law');p.add_argument('shots',type=int);p.add_argument('seed',type=int);p.add_argument('--basis',type=int,default=576);p.add_argument('--random',type=int,default=64);main(p.parse_args())
