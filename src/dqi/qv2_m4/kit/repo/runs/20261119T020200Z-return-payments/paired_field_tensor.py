"""Construct a GF4096 product and one input-Frobenius product from nine rational GF8 sites and a jet."""
import argparse
from pathlib import Path
import json
import sys
from paired_jets import M
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sys.path.insert(0,str(ROOT/'src'))
from dqi_q18_retire import joint_pair12_lift as lift
from dqi_q18_retire.published_joint_gate import PAIRS
import kickmix as km
S=km.GF2Field(3);F=km.GF2Field(12)
TOWER_STEP=1
def coords():
    generator=F.pow(F.primitive_element,4095//7)
    g=next(F.pow(generator,i) for i in range(1,8)if F.pow(F.pow(generator,i),3)^F.pow(generator,i)^1==0)
    k=[F.mul(F.pow(g,i),F.pow(F.primitive_element,j*TOWER_STEP))for j in range(4)for i in range(3)]
    def embed(x):return lift.xor(k[i]for i in range(12)if x>>i&1)
    binary={embed(i):i for i in range(4096)};assert len(binary)==4096
    return [binary[1<<i]for i in range(12)]
def small_tensor():
    # A six-product formula for GF8 from the six symmetric binary forms, verified on all bases.
    for skip in (7,1,2,3,4,5,6):
        masks=[x for x in range(1,8)if x!=skip]
        rows=[sum(((a>>i&1)&(a>>j&1))<<k for k,a in enumerate(masks))for i in range(3)for j in range(3)]
        rhs=[S.mul(1<<i,1<<j)for i in range(3)for j in range(3)]
        if lift.solve(rows,rhs,6)['spans']:return masks
    raise AssertionError()
def forms(single_points,jet,common,swaps):
    co=coords();singles=small_tensor()
    published=json.loads((ROOT/'runs/20261031T215700Z-published-joint-source-loader/construct.json').read_text())
    assert tuple(tuple(t)for t in published['exponent_pairs'])==PAIRS
    pp=[(a,b)for a,b,_ in published['terms']]
    def ev(co,p,op):
        cs=[(co>>(3*j))&7 for j in range(4)]
        if op=='deriv':cs=[cs[1],0,cs[3]]
        c=cs[-1]if p==8 else 0
        if p!=8:
            for u in cs[::-1]:c=S.mul(c,p)^u
        return S.square(c)if op=='sq'else c
    def pull(m,p,o):return sum(((m&ev(v,p,o)).bit_count()&1)<<i for i,v in enumerate(co))
    ret=[]
    for p in common:
        A,B=swaps.get(p,(1,1))
        aa=lambda a:sum(((a&S.mul(A,1<<i)).bit_count()&1)<<i for i in range(3))
        bb=lambda a:sum(((a&S.mul(B,1<<i)).bit_count()&1)<<i for i in range(3))
        ret += [(pull(aa(a),p,''),pull(bb(b),p,''))for a,b in pp]
    for point in single_points:ret += [(pull(a,point,''),pull(a,point,'sq'))for a in singles]
    ret +=[(pull(a,jet,'deriv'),pull(a,jet,'sq'))for a in singles]
    return ret
def target(fs):
    rows=[sum(((a>>i&1)&(b>>j&1))<<k for k,(a,b)in enumerate(fs))for i in range(12)for j in range(12)]
    rhs=[F.mul(1<<i,1<<j)|(F.mul(1<<i,F.square(1<<j))<<12)for i in range(12)for j in range(12)]
    sol=lift.solve(rows,rhs,len(fs));assert sol['spans'],sol
    return [(a,b,x)for (a,b),x in zip(fs,sol['output_vectors'])if x]
def main():
    common=(0,1,2,3,4,5,8);singles=(6,7);jet=0
    fs=forms(singles,jet,common,{})
    term=target(fs)
    q=P/'aligned_paired_field_terms.json';q.write_text(json.dumps(dict(terms=term,rank=len(term),all_144_basis_verified=True,common=common,singles=singles,jet=jet,attribution='Seven GF8 product terms use Bartoli, Zini and Zullo, arXiv:2201.08242v1 Table 1, CC BY 4.0. GF4096 interpolation with jet and coordinate lifting implemented here.'),indent=1)+'\n');print(len(term))
if __name__=='__main__':main()
