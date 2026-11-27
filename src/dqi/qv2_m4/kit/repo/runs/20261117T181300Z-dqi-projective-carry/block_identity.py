#!/usr/bin/env python3
"""Exact block jet matrix, projective inverse and HMR witness controls.

This proves identities only. It does NOT claim inverse witnesses are free.
Source chart storage, arbitrary head changes and zero-pivot charts remain paid
dependencies, explicitly listed in the accompanying ledger.
"""
import hashlib,json,random,time
from pathlib import Path
from probe import Field

Z=(0,0);ONE=(1,0)
def direct(F,heads,n,d,e,a):
    for b,PA,PB in heads:
        kp=F.kap(b,a);ki=F.inv(kp)
        e=F.add(e,F.scale(n,F.sqrt(PA[1])))
        n,d=F.scale(F.add(d,F.kmul(F.at(PA,a),n)),ki),n
        gam=F.ksqrt(F.add((2*a,1),(kp,0)))
        xb=F.add((F.sqrt(PB[0]),0),F.scale(gam,F.sqrt(PB[1])))
        e=F.scale(F.add(e,F.kmul(xb,n)),ki)
        n,d=F.scale(F.add(d,F.kmul(F.at(PB,a),n)),ki),n
    return n,d,e

def coefficients(F,heads,a):
    c0=direct(F,heads,ONE,Z,Z,a);c1=direct(F,heads,Z,ONE,Z,a)
    ce=direct(F,heads,Z,Z,ONE,a)
    assert ce[:2]==(Z,Z)
    return c0[0],c1[0],c0[1],c1[1],c0[2],c1[2],ce[2]

def apply(F,C,y,e):
    A,B,Cc,D,U,V,S=C
    den=F.add(F.kmul(Cc,y),D)
    if den==Z:raise ZeroDivisionError
    ni=F.kinv(den)
    out=F.kmul(F.add(F.kmul(A,y),B),ni)
    ep=F.kmul(F.add(F.add(F.kmul(U,y),V),F.kmul(S,e)),ni)
    return out,ep

def invert(F,C,yp,ep):
    A,B,Cc,D,U,V,S=C
    dn=F.add(F.kmul(Cc,yp),A)
    if dn==Z:raise ZeroDivisionError
    y=F.kmul(F.add(F.kmul(D,yp),B),F.kinv(dn))
    den=F.add(F.kmul(Cc,y),D)
    e=F.kmul(F.add(F.add(F.kmul(ep,den),F.kmul(U,y)),V),F.kinv(S))
    return y,e

def packed(F,x):return x[0]|(x[1]<<F.n)
def run():
    rng=random.Random(1835);rows=[]
    for n,poly,delta in [(2,7,2),(4,19,8),(12,0x1053,2048)]:
        F=Field(n,poly,delta);tests=neg=regular=singular=0
        sizes=[1] if n==2 else ([1,2] if n==4 else [1,2,4])
        for pairs in sizes:
            a=pairs
            for case in range(8):
                heads=[(b,(rng.randrange(F.q),rng.randrange(F.q)),(rng.randrange(F.q),rng.randrange(F.q)))for b in range(pairs)]
                C=coefficients(F,heads,a)
                A,B,Cc,D,U,V,S=C
                det=F.add(F.kmul(A,D),F.kmul(B,Cc));assert det==F.ksq(S)
                inputs=[((i&3,i>>2),(j&3,j>>2)) for i in range(16) for j in range(16)] if n==2 else [((rng.randrange(F.q),rng.randrange(F.q)),(rng.randrange(F.q),rng.randrange(F.q))) for _ in range(64)]
                for y,e in inputs:
                    nn,dd,ee=direct(F,heads,y,ONE,e,a);tests+=1
                    if dd==Z:singular+=1;continue
                    regular+=1;yp,ep=apply(F,C,y,e)
                    assert (yp,ep)==(F.kmul(nn,F.kinv(dd)),F.kmul(ee,F.kinv(dd)))
                    yr,er=invert(F,C,yp,ep);assert (yr,er)==(y,e)
                    mask=rng.randrange(1<<(4*n));before=packed(F,y)|(packed(F,e)<<(2*n));rebuilt=packed(F,yr)|(packed(F,er)<<(2*n))
                    assert ((before&mask).bit_count()^(rebuilt&mask).bit_count())%2==0
                    # Corrupt the derivative affine term V: value and phase
                    # recovery must fail in a nonzero set, not self-compare.
                    bad=(*C[:5],F.add(V,ONE),S)
                    yb,eb=invert(F,bad,yp,ep)
                    badpacked=packed(F,yb)|(packed(F,eb)<<(2*n))
                    neg+=((before&mask).bit_count()^(badpacked&mask).bit_count())%2
        assert neg>0
        rows.append({'field_bits':n,'old_head_block_sizes':[2*p for p in sizes],'tests':tests,'regular':regular,'singular_denominator':singular,'roundtrip_and_HMR_witness_failures':0,'omitted_V_phase_negative_failures':neg})
    r={'evidence':'diagnostic','identity':'projective two-jet transfer, det(M)=S^2; exact normalized inverse on regular chart','controls':rows,
       'cost_warning':'HMR witness requires the shown nonlinear inverse; it is NOT Clifford-free. An actual source chart and exceptional denominator branch are unbuilt.',
       'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path(__file__).with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':run()
