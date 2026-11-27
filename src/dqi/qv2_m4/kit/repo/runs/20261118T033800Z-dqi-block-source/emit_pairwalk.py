# SPDX-License-Identifier: Apache-2.0
"""Both orientations of the native source/payload basis transport with shared reciprocal debts."""
from pathlib import Path
base=Path(__file__).resolve().with_name("emit_transpose.py")
exec(compile(base.read_text().split('\nstart=time.monotonic();n=args.degree;',1)[0],str(base),'exec'))
from triangular_gauge import dual_join
O=V.P.DirectArithmetic
MIDDLE=None


def restore_divide(b,s,rets,targets):
    """Consume completed quotients and start new divisions against the same unchanged source."""
    ar=O.A;heads=[ar.emit_prefix(b,s,w,2048) for w,r in rets];olds=[O._adjoint_consume(b,s,w,2048) for w in targets]
    ni=O._inverse_norm(b,s,2048);adjs=[O._consume_halves(b,ni,w) for w in targets]
    for (t,r),head in zip(rets,heads):
        assert not r.closed and tuple(t)==r.target and tuple(s)==r.source
        b.cz(r.old_target_mask,t);b.free(r.old_target_mask);b.cx(s[12:],s[:12])
        phase_product(b,s,t,km.array([*r.adjoint_masks[0],*r.adjoint_masks[1]]),ar.tensor24(2048));b.cx(s[12:],s[:12])
        for mask in r.adjoint_masks:b.free(mask)
        if r.inverse_norm_mask is not None:b.cz(r.inverse_norm_mask,ni);b.free(r.inverse_norm_mask)
        r.closed=True
    CE.quotient_phase_multi(O,b,s,ni,[(w,head.old_target_mask) for (w,r),head in zip(rets,heads)],2048)
    for h in heads:ar.free_product_mask(b,h)
    m=b.alloc_bits(12);b.hmr(ni,m);b.free(ni)
    return [O.DivisionRecord(id(b),tuple(s),tuple(w),old,adj,m if j==0 else None,2048) for j,(w,old,adj) in enumerate(zip(targets,olds,adjs))]


def tw_half(b,c,Y,delta,up,first):
    n=len(Y[0]);J=chart(n,delta);E=ev(n-2)
    if up and first:
        for row in Y:
            transform(b,row[2:],transpose(E),True)
            for i,w in enumerate(row[2:]):
                pt=32+i;scaleview(b,w,M.inv(M.mul(pt,pt)^pt^delta))
        tw_cross(b,c,Y,delta)
        for row in Y:h_one(b,row[:2])
    elif up:
        for row in Y:h_one(b,row[:2],True);transform(b,row,transpose(J))
    elif first:
        for row in Y:transform(b,row,transpose(J),True);h_one(b,row[:2])
    else:
        for row in Y:h_one(b,row[:2],True)
        tw_cross(b,c,Y,delta)
        for row in Y:
            for i,w in enumerate(row[2:]):
                pt=32+i;scaleview(b,w,M.mul(pt,pt)^pt^delta)
            transform(b,row[2:],transpose(E))


def walk(b,A,B,Y,n0,reverse,prior,frames=()):
    n=len(A)-1
    if n==1:
        if MIDDLE is None:return {}
        return {'center':MIDDLE(b,A,B,Y,frames,reverse,prior['center'] if reverse else None)}
    stage=(n0-n)//2;delta=places[stage].d
    ca=chart(n+1,delta);cb=chart(n,delta);cc=chart(n-1,delta)
    transform(b,A,ca);transform(b,B,cb);r,c=A[:2],A[2:];q,e=B[:2],B[2:]
    h=[w[:2] for w in Y];low=[w[2:] for w in Y];rw=flat(r);qw=flat(q);hw=[flat(z) for z in h]
    native_place(b,[q,r],delta);R=O.divide_deferred(b,qw,rw);native_place(b,[q,r],delta)
    xform(b,c,r,B,delta,False);transform(b,c,ev(n-1),True);transform(b,c,cc)
    if reverse:tw_half(b,c,Y,delta,False,True)
    else:
        for row in Y:transform(b,row,cb)
    cw=flat(c[:2]);regs=[c[:2],q,*h];native_place(b,regs,delta)
    if reverse:Q,=restore_divide(b,cw,list(zip(hw,prior['up'])),[qw])
    else:Q,*lower=multi_div(b,cw,[qw,*hw])
    native_place(b,regs,delta);xform(b,e,q,c,delta,False);transform(b,e,ev(n-2),True)
    if reverse:tw_half(b,c,Y,delta,False,False)
    else:
        for tail,head in zip(low,h):xform(b,tail,head,c,delta,False);transform(b,tail,ev(n-2),True)
    transform(b,c,cc,True)
    child=walk(b,c,e,low,n0,reverse,prior['child'] if reverse else None,(*frames,(r,q,h,delta)))
    transform(b,c,cc);transform(b,e,ev(n-2));xform(b,e,q,c,delta,True)
    if reverse:
        for tail,head in zip(low,h):transform(b,tail,ev(n-2));xform(b,tail,head,c,delta,True)
    else:tw_half(b,c,Y,delta,True,True)
    native_place(b,regs,delta)
    if reverse:CE.restore_multi(O,b,cw,[(qw,Q),*list(zip(hw,prior['lower']))],[],[])
    else:up=restore_divide(b,cw,[(qw,Q)],hw)
    native_place(b,regs,delta)
    if reverse:
        for row in Y:transform(b,row,cb,True)
    else:tw_half(b,c,Y,delta,True,False)
    transform(b,c,cc,True);transform(b,c,ev(n-1));xform(b,c,r,B,delta,True)
    native_place(b,[q,r],delta);O.restore_with_shared_norm(b,qw,rw,R);native_place(b,[q,r],delta)
    transform(b,B,cb,True);transform(b,A,ca,True)
    return {} if reverse else dict(lower=lower,child=child,up=up)


def truth(a,b,ys,n0,n):
    if n==1:return ys
    m=places[(n0-n)//2];d,why=deflate(a,b,m)
    if why:raise ZeroDivisionError
    r,q,c,e=d;hh=[];ll=[]
    for y in ys:
        h=m.quotient(m.reduce(y),m.reduce(c));l=divexact(add(y,mul(c,h)),m.poly);hh.append(h);ll.append(l+[0]*(n-2-len(l)))
    child=truth(c,e,ll,n0,n-2);return [dual_join(c,m,l,h) for l,h in zip(child,hh)]


start=time.monotonic();n=args.degree;sh=args.shots;print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),degree=n)),flush=True)
b=km.CircuitBuilder();b.set_max_qubits(889);A=[b.create_quantum_register(12,'a'+str(i)) for i in range(n+1)];B=[b.create_quantum_register(12,'b'+str(i)) for i in range(n)];Y=[[b.create_quantum_register(12,'y'+str(k)+'_'+str(i)) for i in range(n)] for k in range(2)];sp=b.create_quantum_register(865-12*(4*n+1),'occupied');masks=[b.create_classical_register(12,'p'+str(i)) for i in range(2*n)]
prior=walk(b,A,B,Y,n,False,None)
for j,(w,m) in enumerate(zip(Y[0]+Y[1],masks)):
    if j or not args.skip_return_mask:b.cz(w,m)
if not args.forward:walk(b,A,B,Y,n,True,prior)
circ=b.finish_circuit();stats=circ.operation_statistics();print(json.dumps(dict(T=stats.num_toffoli_like,Q=circ.num_qubits,ops=len(circ))),flush=True)
rng=np.random.default_rng(args.seed);vals=np.zeros((4*n+1,sh),dtype=np.uint64);ms=rng.integers(4096,size=(2*n,sh),dtype=np.uint64);des=np.zeros((2*n,sh),dtype=np.uint64);ph=np.zeros(sh,dtype=bool);reject=0
for j in range(sh):
    while True:
        aa=list(map(int,rng.integers(4096,size=n+1)));bb=list(map(int,rng.integers(4096,size=n)));ys=[list(map(int,rng.integers(4096,size=n))) for _ in range(2)]
        try:z=truth(aa,bb,ys,n,n);break
        except ZeroDivisionError:reject+=1
    vals[:,j]=aa+bb+ys[0]+ys[1];des[:,j]=z[0]+z[1];x=0
    for word,mask in zip(des[:,j],ms[:,j]):x^=int(word)&int(mask)
    ph[j]=bool(x.bit_count()&1)
sim=km.Simulator(batch_size=sh,seed=args.seed,counting_operations=True);sim.use_same_registers_as(circ);sv=rng.integers(0,2,(len(sp),sh),dtype=np.uint8).astype(bool);sim.write_across_shots(sp,sv)
for reg,row in zip(A+B+Y[0]+Y[1]+masks,[*vals,*ms]):sim.write_across_shots(reg,bits(row))
sim.do(circ);ve=np.any(sim.read_across_shots(sp)^sv,axis=0)
for reg,row in zip(A+B+Y[0]+Y[1],[*vals[:2*n+1],*(des if args.forward else vals[2*n+1:])]):ve|=np.any(sim.read_across_shots(reg)^bits(row),axis=0)
anc=km.array([km.q(i) for i in range(865,circ.num_qubits)]);ve|=np.any(sim.read_across_shots(anc),axis=0);pe=None if args.forward else int((sim.read_phase_flipped_across_shots()^ph).sum());assert not ve.any() and (args.forward or bool(pe)==args.skip_return_mask),(ve.sum(),pe)
out=dict(degree=n,shots=sh,seed=args.seed,body_T=stats.num_toffoli_like,Q=circ.num_qubits,operations=len(circ),forward=args.forward,negative=args.skip_return_mask,value_and_scratch_errors=int(ve.sum()),phase_errors=pe,seconds=time.monotonic()-start,rejected_residues=reject,claim='Full physical source A/B and two dirty payloads, both true W triangular orientations and all source reconstruction, native forward and reverse. Central matrix replaced by identity for this cost separating experiment. Border and gap body excluded.')
(args.out/'pairwalk.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
