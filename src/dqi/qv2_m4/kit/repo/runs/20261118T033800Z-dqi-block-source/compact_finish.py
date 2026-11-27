"""Fixed-width CRT coordinates of the direct scan numerator, including the top border."""
from functools import lru_cache
from finish_fusion import *


def kmul(m,u,v):return m.reduce(mul(u,v))


@lru_cache(None)
def factors(start,count):
    p=[1]
    for m in places[start:count]:p=mul(p,m.poly)
    return tuple(p)


@lru_cache(None)
def basis(start,end,j,axis):
    P=list(factors(start,end));m=places[j];k=divexact(P,m.poly)
    h=m.quotient(([1,0],[0,1])[axis],m.reduce(k))
    return tuple(mul(k,h))


def interp(start,end,values):
    out=[]
    for j,v in zip(range(start,end),values):
        for axis,c in enumerate(v):
            out=add(out,scale(basis(start,end,j,axis),c))
    return out


@lru_cache(None)
def point_l(i,end,j):
    m=places[i]
    return tuple(m.reduce(basis(i+1,end,j,k)) for k in range(2))


def at_l(mat,x):
    a,b=mat
    return [M.mul(a[k],x[0])^M.mul(b[k],x[1]) for k in range(2)]


def packed(frames,leaf,H,qt,wrong=False,return_slots=False):
    nn=len(frames);tau=leaf[:];sig=[0,0];hi=[]
    for a,b,r,q,c,e,m,h in frames:hi.append([m.quotient(x,q) for x in h])
    for i in reversed(range(nn)):
        a,b,r,q,c,e,m,h=frames[i]
        for k,p in enumerate(hi[i]):
            p[0]^=tau[k];sig[k]^=kmul(m,q,p)[1];tau[k]^=M.mul(r[1],sig[k])
    for k in range(2):
        test=0
        for i,frame in enumerate(frames):test^=kmul(frame[6],frame[3],hi[i][k])[1]
        assert sig[k]==test
    for i in reversed(range(nn)):
        a,b,r,q,c,e,m,h=frames[i];pt=m.reduce(factors(i+1,nn));unit=m.reduce(c)
        for k,w in enumerate(hi[i]):
            h0,h1=kmul(m,w,pt)
            for j in range(i+1,nn):
                z=places[j].reduce(c);f=kmul(places[j],z,hi[j][k]);u,v=at_l(point_l(i,nn,j),f)
                if not wrong or j!=i+1:h0^=u;h1^=v
            hi[i][k]=m.quotient((h0,h1),unit)
    if return_slots:return hi,tau
    a0,b0=frames[0][:2];even=add(b0,scale(a0,qt));ep=[];op=[];tv=[]
    for j,(xi,eta) in enumerate(hi):
        m=places[j];a=m.reduce(a0);b=m.reduce(even);vb=kmul(m,a,eta);tv.append(vb)
        ep.append(m.reduce(add(mul(b,xi),[0]+list(vb))))
        op.append(m.reduce(add(mul(a,xi),mul(b,eta))))
    P=list(factors(0,nn));E=interp(0,nn,ep);O=interp(0,nn,op);Tv=pad(interp(0,nn,tv),len(P)-1)
    E=add(E,mul(P,[H^M.mul(qt,tau[0])^Tv[-1],tau[1]]))
    O=add(O,scale(P,tau[0]^M.mul(qt,tau[1])))
    z=[0]*(4*nn+3)
    for i,x in enumerate(E):z[2*i]=M.mul(x,x)
    for i,x in enumerate(O):z[2*i+1]=M.mul(x,x)
    return M.trim(z)


if __name__=='__main__':
    mode,ns,sd=sys.argv[1:];shots=int(ns);seed=int(sd);rng=random.Random(seed);start=time.monotonic();counts=Counter()
    rows={int(r[0]):(float(r[1]),list(map(int,r[2:]))) for r in (z.split() for z in (HERE.parent/'20261117T214100Z-dqi-direct-bezout'/'physical_locators.dat').read_text().splitlines())}
    print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),mode=mode)),flush=True)
    for case in range(shots):
        a,b=sample(rng,mode,rows);qt=rng.randrange(4096);h=rng.randrange(4096);y=[[rng.randrange(4096) for j in range(17)] for k in range(2)];even=add(b,scale(a,qt));D=add(square(even),[0]+square(a));U=add(y[0],scale(a,h));N=add(square(U),[0]+square(y[1]));Dprime=square(a)
        try:fr,leaf=project(a,b,y)
        except ZeroDivisionError as ex:counts[str(ex)]+=1;continue
        K=packed(fr,leaf,h,qt);P2=square(factors(0,8))
        assert rem(add(mul(Dprime,K),mul(P2,N)),D)==[];counts['packed_scan_exact']+=1
        if case%97==0:
            wrong=packed(fr,leaf,h,qt,True);counts['negative_cases']+=1;counts['negative_detected']+=rem(add(mul(Dprime,wrong),mul(P2,N)),D)!=[]
    out=dict(mode=mode,seed=seed,shots=shots,counts=dict(counts),seconds=time.monotonic()-start,pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),architecture='32 field words for eight two-RHS CRT pairs, two leading fields, and original odd border. Bottom uses precisely two temporary fields. Every higher stage only uses unchanged deeper CRT words and its source c; no saved scalar flags or secondary polynomial bank.')
    (HERE/f'compact_finish_{seed}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
