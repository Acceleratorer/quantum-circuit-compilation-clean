#!/usr/bin/env python3
"""Exact incumbent paired-extractor carry audit; no native circuit claim.

Recurrence independently transcribed from src/dqi_v8/v8_model.py extractor_old.
Field dimension is parameterized only for complete small controls.
"""
import collections, hashlib, itertools, json, random, sys, time
from pathlib import Path

ROOT=Path(__file__).absolute().parents[2]

class Field:
    def __init__(self,n,poly,delta):
        self.n=n; self.q=1<<n; self.poly=poly; self.delta=delta
        self.ex=[0]*(2*(self.q-1)); self.log=[-1]*self.q
        x=1
        for i in range(self.q-1):
            self.ex[i]=x; self.log[x]=i
            x<<=1
            if x&self.q:x^=poly
        assert x==1 and len(set(self.ex[:self.q-1]))==self.q-1
        self.ex[self.q-1:]=self.ex[:self.q-1]
        assert self.trace(delta)==1
    def mul(self,a,b):return self.ex[self.log[a]+self.log[b]] if a and b else 0
    def inv(self,a):
        if not a:raise ZeroDivisionError
        return self.ex[((self.q-1)-self.log[a])%(self.q-1)]
    def sqrt(self,a):return self.ex[((self.q//2)*self.log[a])%(self.q-1)] if a else 0
    def trace(self,a):
        t=0
        for _ in range(self.n):t^=a;a=self.mul(a,a)
        return t
    def add(self,x,y):return x[0]^y[0],x[1]^y[1]
    def scale(self,x,a):return self.mul(x[0],a),self.mul(x[1],a)
    def kmul(self,x,y):
        aa=self.mul(x[0],y[0]);bb=self.mul(x[1],y[1])
        return aa^self.mul(self.delta,bb),self.mul(x[0]^x[1],y[0]^y[1])^aa
    def kinv(self,x):
        norm=self.mul(x[0],x[0])^self.mul(x[0],x[1])^self.mul(self.delta,self.mul(x[1],x[1]))
        z=self.inv(norm)
        return self.mul(x[0]^x[1],z),self.mul(x[1],z)
    def ksq(self,x):return self.kmul(x,x)
    def ksqrt(self,x):
        h=self.sqrt(x[1]);return self.sqrt(x[0]^self.mul(self.delta,self.mul(h,h))),h
    def kap(self,a,b):
        ta,tb=2*a,2*b
        return self.mul(ta,ta)^ta^self.mul(tb,tb)^tb
    def at(self,p,a):return p[0]^self.mul(2*a,p[1]),p[1]
    def coeff(self,x,a):return self.at(x,a)

def query(F,p,old,a,n,d):
    return F.scale(F.add(d,F.kmul(F.at(p,a),n)),F.inv(F.kap(old,a))),n

def reverse_query(F,p,old,a,n,d):
    return d,F.add(F.scale(n,F.kap(old,a)),F.kmul(F.at(p,a),d))

def extract(F,Yd,first_test=19):
    P=[F.coeff(F.kinv(Yd[0][0]),0)];c=(1,0);flags={};records=[]
    for a in range(1,len(Yd)):
        Y,Yp=Yd[a];k0=F.kap(0,a)
        eg=F.add(F.scale(F.ksqrt(Yp),F.sqrt(k0)),F.ksqrt(Y))
        n,d,e=F.kmul(c,Y),c,F.kmul(c,eg)
        gam=F.ksqrt(F.add((2*a,1),(k0,0)))
        x=F.add((F.sqrt(P[0][0]),0),F.scale(gam,F.sqrt(P[0][1])))
        e=F.add(e,F.kmul(x,n));n,d=query(F,P[0],0,a,n,d);e=F.scale(e,F.inv(k0))
        for b in range(1,a):
            PA,PB=P[2*b-1:2*b+1];kp=F.kap(b,a)
            e=F.add(e,F.scale(n,F.sqrt(PA[1])));n,d=query(F,PA,b,a,n,d)
            gam=F.ksqrt(F.add((2*a,1),(kp,0)))
            x=F.add((F.sqrt(PB[0]),0),F.scale(gam,F.sqrt(PB[1])))
            e=F.add(e,F.kmul(x,n));n,d=query(F,PB,b,a,n,d);e=F.scale(e,F.inv(kp))
        s=2*a-1;flag=False
        if s>=first_test:
            flag=n==(0,0);flags[s]=flag
            if flag:n,d=d,n
        if n==(0,0):raise ZeroDivisionError
        P.append(F.coeff(F.kmul(d,F.kinv(n)),a));oldc=c;c=n
        e=F.add(e,F.scale(c,F.sqrt(P[s][1])))
        x=F.kmul(e,F.kinv(c));P.append(F.coeff(F.ksq(F.kinv(x)) if x!=(0,0) else (0,0),a))
        records.append((oldc,c,flag))
    return P,flags,c,records

def recover(F,P,flags):
    """Recover exact carry from heads using normalized inverse query products.

    Each node starts at n=1,d=P_odd and reverses the old-slot 2x2 matrices.
    The resulting d0 equals oldcarry/newcarry; all operations are explicitly
    charged in the result ledger, and no HMR erasure is assumed.
    """
    c=(1,0);ratios=[]
    for a in range(1,(len(P)+1)//2):
        n,d=(1,0),F.at(P[2*a-1],a)
        if flags.get(2*a-1,False):n,d=d,n
        for b in reversed(range(1,a)):
            n,d=reverse_query(F,P[2*b],b,a,n,d)
            n,d=reverse_query(F,P[2*b-1],b,a,n,d)
        n,d=reverse_query(F,P[0],0,a,n,d)
        c=F.kmul(c,F.kinv(d));ratios.append(d)
    return c,ratios

def run():
    started=time.time();r={"evidence":"diagnostic","scope":"actual single-first paired extractor; 33 heads, before sequential end node"}
    F=Field(2,7,2);words=list(itertools.product(range(4),repeat=2));seen={};coll=[];valid=0;recover_bad=0
    for y0,y,yp in itertools.product(words,repeat=3):
        try:P,flags,c,_=extract(F,[(y0,(0,0)),(y,yp)])
        except ZeroDivisionError:continue
        valid+=1;key=tuple(P)
        if key in seen and seen[key][0]!=c:coll.append([key,seen[key],[c,y0,y,yp]])
        seen[key]=(c,y0,y,yp)
        cr,_=recover(F,P,flags);recover_bad+=cr!=c
    r['tiny_GF4_exhaustive']={"inputs":4096,"valid":valid,"distinct_heads":len(seen),"carry_collisions":len(coll),"recovery_mismatches":recover_bad,"examples":coll[:2]}
    assert not coll and not recover_bad
    sys.path.insert(0,str(ROOT/'src/dqi_v8'));import v8_model as V
    G=Field(12,0x1053,2048);rng=random.Random(1813);physical=[];scale_cases=0;eqbad=recbad=0;scale_invariant=0;different_heads=0
    for t in [19,25,31,35]:
        for shot in range(4):
            err={V.M.EXP[p]:rng.randrange(1,4096) for p in rng.sample(range(4095),t)}
            S=V.M.syndromes(err);_,Yd,_,_=V.data8(S)
            try:P,fl,c,rr=extract(G,[Yd[a] for a in range(17)]);pref,fr,cref=V.extractor_old(Yd)
            except ZeroDivisionError:continue
            eqbad+=(P!=pref or fl!=fr or c!=cref)
            cr,ratios=recover(G,P,fl);recbad+=cr!=c
            physical.append({"t":t,"carry":c,"heads_hash":hashlib.sha256(repr(P).encode()).hexdigest(),"ratio_product_recovery":cr==c})
            for scale in [2,3,7,19,127,255,1024,2048]:
                Ys=[(G.scale(y,scale),G.scale(yp,scale)) for y,yp in [Yd[a] for a in range(17)]]
                try:Ps,fs,cs,_=extract(G,Ys)
                except ZeroDivisionError:continue
                scale_cases+=1;scale_invariant+=cs==c;different_heads+=Ps!=P
                crr,_=recover(G,Ps,fs);recbad+=crr!=cs
    assert eqbad==0 and recbad==0
    r['GF4096']={"physical_samples":len(physical),"reference_mismatches":eqbad,"recovery_mismatches":recbad,"global_scalings":scale_cases,"carry_unchanged_by_scale":scale_invariant,"heads_changed_by_scale":different_heads,"samples":physical}
    # Accumulate sixteen ratios before ONE final inverse. First accumulator
    # product with1 is a copy, so fifteen real products, not sixteen.
    # The191T inverse figure is an optimistic component allowance, not a bound
    # on all possible inverse circuits and not a native cost for this topology.
    r['literal_reconstruction_price']={"K_query_products":256,"K_carry_products":15,"K_inversions":1,"optimistic_inverse_T":191,"optimistic_forward_T":(256+15)*99+191,"return_cleanup":"unpriced, additional; this is not a native whole cost","width":"two K query words plus a K accumulator unless recomputation/overlap changes schedule"}
    r['elapsed_seconds']=time.time()-started;r['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(r,indent=2))
    Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':run()
