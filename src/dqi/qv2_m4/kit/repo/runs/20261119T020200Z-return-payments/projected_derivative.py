"""Keep selected original derivative directions and retire their exact native signed accumulator on return."""
from collections import Counter
from functools import cache
from pathlib import Path
import json,runpy
from paired_jets import M

HERE=Path(__file__).resolve().parent
MASK=(1<<24)-1
@cache
def tensors():
    p=HERE/'whole889_scalar_audit/code'
    return runpy.run_path(str(p/'ja_terms.py'))['TERMS'],runpy.run_path(str(p/'jb_terms.py'))['TERMS']
def scale(v,c):return M.mul(v&4095,c)|(M.mul(v>>12,c)<<12)
def kap(a):return 2048^M.mul(2*a,2*a)^(2*a)
@cache
def steps(a):
    ja,jb=tensors();r=[];invscale=1
    for j in range(a):
        t=2*(a^j);k=kap(a)^kap(j)
        if j:r.append(('A',j,invscale,jb))
        r.append(('B',j,invscale,ja[str(t)]));invscale=M.mul(invscale,k)
    return r,invscale
@cache
def geometry(a,k):
    seq,_=steps(a);counts=Counter()
    for _,_,inv,terms in seq:
        for _,_,w in terms:
            if not w&MASK:counts[scale(w>>24,inv)]+=1
    span=[0];basis=[];gains=[]
    for _ in range(k):
        # Count every coset meeting the support. Every extension picks one entire coset.
        sums=Counter();seen=set(span)
        def reduce(x):
            for v in lead:x=min(x,x^v)
            return x
        lead=[]
        for v in basis:
            x=reduce(v)
            if x:lead.append(x);lead.sort(reverse=True)
        for x,w in counts.items():
            y=reduce(x)
            if y:sums[y]+=w
        z=max(sums,key=lambda c:(sums[c],-c));basis.append(z);span.extend([s^z for s in span]);gains.append(sums[z])
    chosen=set(span);total=sum(counts[x]for x in chosen);assert sum(gains)==total
    full=basis[:]
    b={}
    def add(x):
        while x:
            i=x.bit_length()-1
            if i not in b:b[i]=x;return True
            x^=b[i]
        return False
    for x in full:assert add(x)
    for x in (1<<j for j in range(24)):
        if add(x):full.append(x)
    return full,dict(gradient=gains,retired_toffolis=total,upper_bound=sum(w for _,w in counts.most_common((1<<k)-1)),source_dimensions=k,unique_terms=len(counts))

def read(b,word,a,k):
    from field_tensor import invert_binary_columns
    basis,stats=geometry(a,k);r=b.alloc_qubits(k)
    for j,row in enumerate(invert_binary_columns(basis)[:k]):
        for i,w in enumerate(word):
            if row>>i&1:b.cx(w,r[j])
    return r

def restore(ex,words,a,n,e,d,source,omit=False):
    from tower_inverse import rows_from_columns,apply_inplace_linear,phase_product
    from field_tensor import invert_binary_columns,apply_linear,accumulate_product
    import kickmix as km
    b=ex.b;k=len(source);basis,stats=geometry(a,k);inv=invert_binary_columns(basis)
    seq,last=steps(a);endbasis=[scale(v,M.inv(last))for v in basis]
    apply_inplace_linear(b,e,invert_binary_columns(endbasis))
    mask=b.alloc_bits(k);b.hmr(e[:k],mask)
    for kind,j,sc,terms in reversed(seq):
        kp=kap(j)^kap(a);w=words[2*j-1] if kind=='A' else words[2*j]
        b.swap(n,d);ex.RQ.public_scale(b,d,kp);ex.RQ.node_view(b,w,a)
        quantum=[];phase_terms=[]
        for left,right,out in terms:
            z=apply_linear(inv,scale(out>>24,sc));qo=(out&MASK)|((z>>k)<<24);phase=z&((1<<k)-1)
            if qo:quantum.append((left,right,qo))
            if phase:phase_terms.append((left,right,phase))
        accumulate_product(b,w,n,km.array([*d,*e[k:]]),quantum)
        if not(omit and not j):phase_product(b,w,n,mask,phase_terms)
        ex.RQ.node_view(b,w,a)
    b.cz(mask,source);b.free(mask);b.cx(source,e[:k]);b.cx(e[:k],source);b.free(source)
    apply_inplace_linear(b,e,rows_from_columns(basis))

def inventory(p):
    rec={}
    for a in range(1,17):
        rec[a]={k:geometry(a,k)[1] for k in range(1,10)}
    # Enumerating all allocations of nine stored dimensions, use the exact
    # term-count ceiling for any possible basis as well as the constructive result.
    def best(key):
        choices={0:(0,[])}
        for a in range(1,17):
            tmp={}
            for spent,(s,alloc) in choices.items():
                for k in range(10-spent):
                    item=(s+(rec[a][k][key]if k else 0),alloc+([(a,k)] if k else []))
                    if spent+k not in tmp or item[0]>tmp[spent+k][0]:tmp[spent+k]=item
            choices=tmp
        return choices
    result=dict(cells=rec,constructive=best('retired_toffolis'),upper_bound=best('upper_bound'))
    p.write_text(json.dumps(result,indent=1)+'\n');return result
if __name__=='__main__':
    result=inventory(HERE/'projected_derivative_inventory.json')
    print(result['constructive'][9],result['upper_bound'][9])
