# SPDX-License-Identifier: Apache-2.0
"""Emit the complete degree-two source traversal in its 35 occupied field words."""
import argparse
from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import sys
import time
import zipfile

p=argparse.ArgumentParser();p.add_argument('--src',type=Path);p.add_argument('--official',type=Path);p.add_argument('--out',type=Path);p.add_argument('--degree',type=int,required=True);p.add_argument('--shots',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--skip-return-mask',action='store_true');p.add_argument('--forward',action='store_true');args=p.parse_args()
tmp=Path('/tmp/panel_native');tmp.mkdir()
with zipfile.ZipFile(args.src/'dqi_source_zip') as z:z.extractall(tmp)
source=tmp/'dqi_source/src';bundle=source/'pro1_controller_bundle/1_task'
for d,f in [('official','kickmix/kickmix.so'),('verifiers/dqi','verifiers/dqi/verify_submission_dqi.py')]:
    target=bundle/d;target.mkdir(parents=True,exist_ok=True);shutil.copy(args.official/f,target/Path(f).name)
os.chdir(source);sys.path.insert(0,str(source/'controller_work/after_v3/integration_v7'));import v7_pipeline as V;V.configure()
sys.path.insert(0,str(Path(__file__).resolve().parent));from quadratic import M,Place,deflate,places
from source_maps import inverse,mv,transpose
from tower_inverse import apply_inplace_linear, rows_from_columns, xor_product
from quantum_reciprocal import xor_linear
import kickmix as km
import numpy as np


@lru_cache(None)
def cols(s):return tuple(M.mul(s,1<<j) for j in range(12))


def axpy(b,r,t,s):
    if not s:return
    if s==1:b.cx(r,t)
    else:xor_linear(b,r,t,cols(s))


def scaleview(b,r,s):
    if s!=1:apply_inplace_linear(b,r,rows_from_columns(cols(s)))


@lru_cache(None)
def operations(matrix):
    w=[list(v) for v in matrix];n=len(matrix);ans=[]
    for j in range(n):
        pivot=next(i for i in range(j,n) if w[i][j]);
        if pivot!=j:w[j],w[pivot]=w[pivot],w[j];ans.append(('swap',j,pivot,1))
        s=w[j][j]
        if s!=1:
            w[j]=[M.div(x,s) for x in w[j]];ans.append(('scale',j,j,M.inv(s)))
        for i in range(n):
            if i!=j and w[i][j]:
                s=w[i][j];w[i]=[v^M.mul(s,x) for x,v in zip(w[j],w[i])];ans.append(('add',j,i,s))
    return ans


def transform(b,w,m,back=False):
    ops=operations(tuple(tuple(row) for row in m))
    for tag,j,i,s in (ops if back else reversed(ops)):
        if tag=='swap':b.swap(w[j],w[i])
        elif tag=='scale':scaleview(b,w[j],s if back else M.inv(s))
        else:axpy(b,w[j],w[i],s)


@lru_cache(None)
def ev(n):
    return tuple(tuple(M.EXP[(M.LOG[32+i]*j)%4095] for j in range(n)) for i in range(n))


@lru_cache(None)
def chart(n,delta):
    m=Place(delta);res=[m.reduce([0]*j+[1]) for j in range(n)]
    return tuple([tuple(x[0] for x in res),tuple(x[1] for x in res),*ev(n)[:n-2]])


@lru_cache(None)
def ext_evaluate(n,delta,i):
    return tuple(mv(transpose(inverse(chart(n,delta))),ev(n)[i]))


def xform(b,dest,unit,other,delta,reverse):
    for i,t in enumerate(dest):
        point=32+i;den=M.mul(point,point)^point^delta
        scaleview(b,t,den if reverse else M.inv(den))
        co=ext_evaluate(len(other),delta,i);j=next(j for j,v in enumerate(co) if v);x=other[j]
        for k,c in enumerate(co):
            if k!=j:axpy(b,other[k],x,M.div(c,co[j]))
        axpy(b,unit[1],unit[0],point)
        fac=co[j] if reverse else M.div(co[j],den)
        scaleview(b,x,fac);xor_product(b,unit[0],x,t);scaleview(b,x,M.inv(fac))
        axpy(b,unit[1],unit[0],point)
        for k,c in enumerate(co):
            if k!=j:axpy(b,other[k],x,M.div(c,co[j]))


def flat(w):return km.array([q for reg in w for q in reg])


@lru_cache(None)
def shift_to_native(delta):
    return next(x for x in range(4096) if M.mul(x,x)^x==delta^2048)


def native_place(b,words,delta):
    for pair in words:axpy(b,pair[1],pair[0],shift_to_native(delta))


def source_walk(b,A,B,degree,slots):
    n=len(A)-1
    if n==1:return lambda:None
    delta=places[(degree-n)//2].d
    ca=chart(n+1,delta);cb=chart(n,delta);cc=chart(n-1,delta)
    transform(b,A,ca);transform(b,B,cb)
    r,c=A[:2],A[2:];q,e=B[:2],B[2:];r_w=flat(r);q_w=flat(q)
    native_place(b,[q,r],delta);R=V.P.DirectArithmetic.divide_deferred(b,q_w,r_w);native_place(b,[q,r],delta)
    xform(b,c,r,B,delta,False);transform(b,c,ev(n-1),True);transform(b,c,cc)
    c_w=flat(c[:2]);native_place(b,[c[:2],q],delta);Q=V.P.DirectArithmetic.divide_deferred(b,c_w,q_w);native_place(b,[c[:2],q],delta)
    xform(b,e,q,c,delta,False);transform(b,e,ev(n-2),True);transform(b,c,cc,True)
    slots.extend(r+q);back=source_walk(b,c,e,degree,slots)
    def restore():
        back();transform(b,c,cc);transform(b,e,ev(n-2));xform(b,e,q,c,delta,True)
        native_place(b,[c[:2],q],delta);V.P.DirectArithmetic.restore_with_shared_norm(b,c_w,q_w,Q);native_place(b,[c[:2],q],delta)
        transform(b,c,cc,True);transform(b,c,ev(n-1));xform(b,c,r,B,delta,True)
        native_place(b,[q,r],delta);V.P.DirectArithmetic.restore_with_shared_norm(b,q_w,r_w,R);native_place(b,[q,r],delta)
        transform(b,B,cb,True);transform(b,A,ca,True)
    return restore


def bits(w):return np.array([(w>>j)&1 for j in range(12)],dtype=bool)


start=time.monotonic();n=args.degree;assert n%2 and 3<=n<=17
print(json.dumps(dict(pid=os.getpid(),cpu=sorted(os.sched_getaffinity(0)),degree=n)),flush=True)
b=km.CircuitBuilder();b.set_max_qubits(889);A=[b.create_quantum_register(12,'a'+str(i)) for i in range(n+1)];B=[b.create_quantum_register(12,'b'+str(i)) for i in range(n)];sp=b.create_quantum_register(865-12*(2*n+1),'occupied');pm=[b.create_classical_register(12,'mask'+str(i)) for i in range(2*n-2)];slots=[]
back=source_walk(b,A,B,n,slots);assert len(slots)==len(pm)
for i,(x,m) in enumerate(zip(slots,pm)):
    if not args.skip_return_mask or i:b.cz(x,m)
if not args.forward:back()
circ=b.finish_circuit();stats=circ.operation_statistics();print(json.dumps(dict(T=stats.num_toffoli_like,Q=circ.num_qubits,ops=len(circ))),flush=True)
rng=np.random.default_rng(args.seed);sh=args.shots;inputs=np.zeros((2*n+1,sh),dtype=np.uint64);desired=np.zeros((2*n-2,sh),dtype=np.uint64);ms=rng.integers(0,4096,(2*n-2,sh),dtype=np.uint64);exp=np.zeros(sh,dtype=bool);kept=0;denfail=0
while kept<sh:
    aa=list(map(int,rng.integers(0,4096,n+1)));bb=list(map(int,rng.integers(0,4096,n)));a0=aa[:];b0=bb[:];pars=[]
    for k in range((n-1)//2):
        row,reason=deflate(aa,bb,places[k]);
        if reason:break
        rr,qq,aa,bb=row;pars+=rr+qq
    if len(pars)!=2*n-2:denfail+=1;continue
    inputs[:,kept]=a0+b0;desired[:,kept]=pars;ex=0
    for mask,v in zip(ms[:,kept],pars):ex^=int(mask)&v
    exp[kept]=bool(ex.bit_count()&1);kept+=1
sim=km.Simulator(batch_size=sh,seed=args.seed,counting_operations=True);sim.use_same_registers_as(circ);sv=rng.integers(0,2,(len(sp),sh),dtype=np.uint8).astype(bool);sim.write_across_shots(sp,sv)
for reg,row in zip(A+B+pm,[*inputs,*ms]):sim.write_across_shots(reg,bits(row))
sim.do(circ)
if args.forward:
    errs=[int(np.any(sim.read_across_shots(w)^bits(values),axis=0).sum()) for w,values in zip(slots,desired)]
    (args.out/'forward_slots.json').write_text(json.dumps(dict(errors=errs,T=stats.num_toffoli_like,Q=circ.num_qubits,degree=n,shots=sh))+'\n');print(errs);sys.exit(0)
ve=np.any(sim.read_across_shots(sp)^sv,axis=0)
for reg,row in zip(A+B,inputs):ve|=np.any(sim.read_across_shots(reg)^bits(row),axis=0)
anc=km.array([km.q(i) for i in range(865,circ.num_qubits)]);ve|=np.any(sim.read_across_shots(anc),axis=0);pe=int((sim.read_phase_flipped_across_shots()^exp).sum());assert not ve.any() and bool(pe)==args.skip_return_mask,(ve.sum(),pe)
out=dict(physical_words=2*n+1,degree=n,T=stats.num_toffoli_like,Q=circ.num_qubits,operations=len(circ),shots=sh,seed=args.seed,value_and_scratch_errors=int(ve.sum()),phase_errors=pe,negative=args.skip_return_mask,unadmitted_residue=denfail,seconds=time.monotonic()-start,evidence='complete native source traversal and inverse on arbitrary data; nonlinear parameters are independently marked and all original data, spectators and scratch checked')
(args.out/'source_native.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
