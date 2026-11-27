# SPDX-License-Identifier: Apache-2.0
"""Native two-payload lower Bezout map sharing the source's reciprocal at each node."""
from pathlib import Path
source_adapter=Path(__file__).resolve().with_name('emit_source.py')
exec(compile(source_adapter.read_text().split('\nstart=time.monotonic();n=args.degree;',1)[0], str(source_adapter), 'exec'))
from source_panel import add,divexact,mul
sys.path.insert(0,str(args.out/'code'));import confluent_ext as CE


def multi_div(b,source,words):
    O=V.P.DirectArithmetic;olds=[O._adjoint_consume(b,source,w,2048) for w in words]
    norm=O._inverse_norm(b,source,2048);adjs=[O._consume_halves(b,norm,w) for w in words]
    m=b.alloc_bits(12);b.hmr(norm,m);b.free(norm)
    return [O.DivisionRecord(id(b),tuple(source),tuple(w),old,adj,m if j==0 else None,2048) for j,(w,old,adj) in enumerate(zip(words,olds,adjs))]


def lower_walk(b,A,B,Y,degree,slots):
    n=len(A)-1
    if n==1:
        for row in Y:slots.extend(row)
        return lambda:None
    delta=places[(degree-n)//2].d
    ca=chart(n+1,delta);cb=chart(n,delta);cc=chart(n-1,delta)
    transform(b,A,ca);transform(b,B,cb)
    for row in Y:transform(b,row,cb)
    r,c=A[:2],A[2:];q,e=B[:2],B[2:];h=[row[:2] for row in Y];low=[row[2:] for row in Y]
    rw=flat(r);qw=flat(q);targets=[qw,*[flat(hw) for hw in h]]
    native_place(b,[q,r],delta);R=V.P.DirectArithmetic.divide_deferred(b,qw,rw);native_place(b,[q,r],delta)
    xform(b,c,r,B,delta,False);transform(b,c,ev(n-1),True);transform(b,c,cc)
    cw=flat(c[:2]);regs=[c[:2],q,*h];native_place(b,regs,delta);records=multi_div(b,cw,targets);native_place(b,regs,delta)
    for dest,head in [(e,q),*zip(low,h)]:
        xform(b,dest,head,c,delta,False);transform(b,dest,ev(n-2),True)
    transform(b,c,cc,True);slots.extend([*r,*q,*h[0],*h[1]])
    back=lower_walk(b,c,e,low,degree,slots)
    def restore():
        back();transform(b,c,cc)
        for dest,head in [(e,q),*zip(low,h)]:
            transform(b,dest,ev(n-2));xform(b,dest,head,c,delta,True)
        native_place(b,regs,delta);CE.restore_multi(V.P.DirectArithmetic,b,cw,list(zip(targets,records)),[],[]);native_place(b,regs,delta)
        transform(b,c,cc,True);transform(b,c,ev(n-1));xform(b,c,r,B,delta,True)
        native_place(b,[q,r],delta);V.P.DirectArithmetic.restore_with_shared_norm(b,qw,rw,R);native_place(b,[q,r],delta)
        for row in Y:transform(b,row,cb,True)
        transform(b,B,cb,True);transform(b,A,ca,True)
    return restore


start=time.monotonic();n=args.degree;sh=args.shots;assert n%2 and n<=17
print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),degree=n)),flush=True)
b=km.CircuitBuilder();b.set_max_qubits(889);A=[b.create_quantum_register(12,'a'+str(i)) for i in range(n+1)];B=[b.create_quantum_register(12,'b'+str(i)) for i in range(n)];Y=[[b.create_quantum_register(12,'y'+str(k)+'_'+str(i)) for i in range(n)] for k in range(2)];sp=b.create_quantum_register(865-12*(4*n+1),'occupied');masks=[b.create_classical_register(12,'p'+str(i)) for i in range(4*n-2)];slots=[]
restore=lower_walk(b,A,B,Y,n,slots);assert len(masks)==len(slots)
for i,(w,m) in enumerate(zip(slots,masks)):
    if not args.skip_return_mask or i:b.cz(w,m)
if not args.forward:restore()
circ=b.finish_circuit();stats=circ.operation_statistics();print(json.dumps(dict(T=stats.num_toffoli_like,Q=circ.num_qubits,ops=len(circ))),flush=True)
rng=np.random.default_rng(args.seed);inputs=np.zeros((4*n+1,sh),dtype=np.uint64);desired=np.zeros((4*n-2,sh),dtype=np.uint64);ms=rng.integers(0,4096,(4*n-2,sh),dtype=np.uint64);ph=np.zeros(sh,dtype=bool);kept=0;reject=0
while kept<sh:
    aa=list(map(int,rng.integers(4096,size=n+1)));bb=list(map(int,rng.integers(4096,size=n)));ys=[list(map(int,rng.integers(4096,size=n))) for _ in range(2)];initial=aa+bb+ys[0]+ys[1];pars=[]
    for k in range((n-1)//2):
        m=places[k];row,reason=deflate(aa,bb,m)
        if reason:break
        rr,qq,aa,bb=row;pars+=rr+qq;yy=[]
        for y in ys:
            h=m.quotient(m.reduce(y),m.reduce(aa));rem=divexact(add(y,mul(aa,h)),m.poly);yy.append(rem);pars+=h
        ys=yy
    if len(pars)!=4*n-4:reject+=1;continue
    pars+= [(y+[0])[0] for y in ys];inputs[:,kept]=initial;desired[:,kept]=pars;z=0
    for x,y in zip(pars,ms[:,kept]):z^=x&int(y)
    ph[kept]=bool(z.bit_count()&1);kept+=1
sim=km.Simulator(batch_size=sh,seed=args.seed,counting_operations=True);sim.use_same_registers_as(circ);sv=rng.integers(0,2,(len(sp),sh),dtype=np.uint8).astype(bool);sim.write_across_shots(sp,sv)
data_regs=A+B+Y[0]+Y[1]
for w,v in zip(data_regs+masks,[*inputs,*ms]):sim.write_across_shots(w,bits(v))
sim.do(circ);ve=np.any(sim.read_across_shots(sp)^sv,axis=0)
for reg,row in zip(slots if args.forward else data_regs,desired if args.forward else inputs):ve|=np.any(sim.read_across_shots(reg)^bits(row),axis=0)
anc=km.array([km.q(i) for i in range(865,circ.num_qubits)]);ve|=np.any(sim.read_across_shots(anc),axis=0)
pe=None if args.forward else int((sim.read_phase_flipped_across_shots()^ph).sum());assert not ve.any() and (args.forward or bool(pe)==args.skip_return_mask),(ve.sum(),pe)
out=dict(degree=n,shots=sh,seed=args.seed,source_and_payload_words=4*n+1,static_T=stats.num_toffoli_like,Q=circ.num_qubits,operations=len(circ),value_and_scratch_errors=int(ve.sum()),phase_errors=pe,negative=args.skip_return_mask,rejected_residues=reject,seconds=time.monotonic()-start,forward_only=args.forward,evidence='complete native source plus W^-1 of both independent payloads in occupied words; reciprocal shared across source Q and both payloads; transpose and rank-one middle excluded')
(args.out/'payload_native.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
