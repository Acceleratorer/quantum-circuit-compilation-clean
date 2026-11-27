# SPDX-License-Identifier: Apache-2.0
"""Native two-RHS W^T and W^-T, paid in both directions on dirty input words."""
from pathlib import Path
base=Path(__file__).resolve().with_name("emit_payload.py")
exec(compile(base.read_text().split('\nstart=time.monotonic();n=args.degree;',1)[0],str(base),'exec'))
from tower_inverse import init_norm,erase_norm,kernel,phase_product
from source_maps import dot


def h_one(b,h,back=False):
    if back:b.swap(h[0],h[1])
    b.cx(h[0],h[1])
    if not back:b.swap(h[0],h[1])


def pay_division(b,s,words,rs):
    O=V.P.DirectArithmetic;A=O.A
    for w,r in zip(words,rs):
        phase_product(b,s,w,r.old_target_mask,A.tensor24(2048));b.free(r.old_target_mask)
    norm=init_norm(b,s[:12],s[12:],2048)
    for w,r in zip(words,rs):
        for half,mask in zip((w[:12],w[12:]),r.adjoint_masks):
            phase_product(b,norm,half,mask,kernel(12));b.free(mask)
        if r.inverse_norm_mask is not None:
            O.Phase12.phase_inverse_twelve_polynomial(b,norm,r.inverse_norm_mask);b.free(r.inverse_norm_mask)
        r.closed=True
    erase_norm(b,s[:12],s[12:],norm,2048);b.free(norm)


def tw_cross(b,c,ys,delta):
    for i in range(len(ys[0])-2):
        co=ext_evaluate(len(c),delta,i);j=next(j for j,v in enumerate(co) if v);x=c[j];pt=32+i
        for k,v in enumerate(co):
            if k!=j:axpy(b,c[k],x,M.div(v,co[j]))
        scaleview(b,x,co[j])
        for w in ys:
            axpy(b,w[0],w[1],pt);xor_product(b,x,w[i+2],w[0]);axpy(b,w[0],w[1],pt)
        scaleview(b,x,M.inv(co[j]))
        for k,v in enumerate(co):
            if k!=j:axpy(b,c[k],x,M.div(v,co[j]))


def tw_down(b,c,ys,delta):
    """Map primal coefficient vectors to W^T outputs in [high,low] order."""
    n=len(ys[0]);J=chart(n,delta);cc=chart(n-1,delta);E=ev(n-2)
    transform(b,c,cc)
    for row in ys:transform(b,row,transpose(J),True);h_one(b,row[:2])
    regs=[c[:2],*[y[:2] for y in ys]];native_place(b,regs,delta);cw=flat(c[:2]);heads=[flat(w[:2]) for w in ys]
    ar=V.P.DirectArithmetic.A;recs=[ar.emit_prefix(b,cw,w,2048) for w in heads]
    native_place(b,regs,delta)
    for w in ys:h_one(b,w[:2],True)
    tw_cross(b,c,ys,delta)
    for row in ys:
        for i,w in enumerate(row[2:]):
            pt=32+i;scaleview(b,w,M.mul(pt,pt)^pt^delta)
        transform(b,row[2:],transpose(E))
    transform(b,c,cc,True)
    def up():
        transform(b,c,cc)
        for row in ys:
            transform(b,row[2:],transpose(E),True)
            for i,w in enumerate(row[2:]):
                pt=32+i;scaleview(b,w,M.inv(M.mul(pt,pt)^pt^delta))
        tw_cross(b,c,ys,delta)
        for w in ys:h_one(b,w[:2])
        native_place(b,regs,delta);ds=multi_div(b,cw,heads);pay_division(b,cw,heads,ds)
        for w,r in zip(heads,recs):ar.repay_product_input(b,w,r)
        native_place(b,regs,delta)
        for row in ys:h_one(b,row[:2],True);transform(b,row,transpose(J))
        transform(b,c,cc,True)
    return up


def truth(cv,ys,m):
    out=[]
    for y in ys:
        h=[dot(cv,y),dot([0]+cv,y)]
        l=[M.mul(m.d,y[j])^y[j+1]^y[j+2] for j in range(len(y)-2)]
        out.append(h+l)
    return out


start=time.monotonic();n=args.degree;sh=args.shots
b=km.CircuitBuilder();b.set_max_qubits(889);C=[b.create_quantum_register(12,'c'+str(i)) for i in range(n-1)];Y=[[b.create_quantum_register(12,'y'+str(k)+'_'+str(i)) for i in range(n)] for k in range(2)]
sp=b.create_quantum_register(865-12*(3*n-1),'occupied');ms=[[b.create_classical_register(12,'m'+str(k)+'_'+str(i)) for i in range(n)] for k in range(2)];backs=[]
print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),degree=n,entry='W-transpose')),flush=True)
for k in range((n-1)//2):
    backs.append(tw_down(b,C[2*k:], [y[2*k:] for y in Y],places[k].d))
for k in range(2):
    for j in range(n):
        if not args.skip_return_mask or j or k:b.cz(Y[k][j],ms[k][j])
if not args.forward:
    for f in reversed(backs):f()
circ=b.finish_circuit();stats=circ.operation_statistics();print(json.dumps(dict(T=stats.num_toffoli_like,Q=circ.num_qubits)),flush=True)
rng=np.random.default_rng(args.seed);vals=rng.integers(4096,size=(3*n-1,sh),dtype=np.uint64);masks=rng.integers(4096,size=(2*n,sh),dtype=np.uint64);desired=np.zeros((2*n,sh),dtype=np.uint64);expect=np.zeros(sh,dtype=bool);replaced=0
for i in range(sh):
    while True:
        c=list(map(int,vals[:n-1,i]));ys=[list(map(int,z)) for z in (vals[n-1:2*n-1,i],vals[2*n-1:,i])]
        if all(places[k].reduce(c[2*k:])!=(0,0) for k in range((n-1)//2)):break
        vals[:n-1,i]=rng.integers(4096,size=n-1,dtype=np.uint64);replaced+=1
    for k in range((n-1)//2):
        sub=truth(c[2*k:],[row[2*k:] for row in ys],places[k])
        ys=[row[:2*k]+tail for row,tail in zip(ys,sub)]
    desired[:,i]=ys[0]+ys[1];z=0
    for v,m in zip(desired[:,i],masks[:,i]):z^=int(v)&int(m)
    expect[i]=bool(z.bit_count()&1)
sim=km.Simulator(batch_size=sh,seed=args.seed,counting_operations=True);sim.use_same_registers_as(circ);sv=rng.integers(0,2,(len(sp),sh),dtype=np.uint8).astype(bool);sim.write_across_shots(sp,sv)
for reg,row in zip(C+Y[0]+Y[1]+ms[0]+ms[1],[*vals,*masks]):sim.write_across_shots(reg,bits(row))
sim.do(circ);errs=np.any(sim.read_across_shots(sp)^sv,axis=0)
for reg,row in zip(C+Y[0]+Y[1],[*vals[:n-1],*(desired if args.forward else vals[n-1:])]):errs|=np.any(sim.read_across_shots(reg)^bits(row),axis=0)
anc=km.array([km.q(i) for i in range(865,circ.num_qubits)]);errs|=np.any(sim.read_across_shots(anc),axis=0)
pe=None if args.forward else int((sim.read_phase_flipped_across_shots()^expect).sum());assert not errs.any() and (args.forward or bool(pe)==args.skip_return_mask),(errs.sum(),pe)
out=dict(degree=n,total_stages=(n-1)//2,T=stats.num_toffoli_like,Q=circ.num_qubits,shots=sh,phase_errors=pe,value_scratch_errors=int(errs.sum()),negative=args.skip_return_mask,forward=args.forward,seed=args.seed,rejected=replaced,seconds=time.monotonic()-start,claim='Native transpose W^T at every degree and full W^-T return with independently marked two-RHS outputs. Source supplied as dirty nested coefficient subarrays; actual source generation and middle corrections separate.')
(args.out/'native_transpose.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
