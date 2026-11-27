"""Encode exact zero-row interpolation constraints for arbitrary pairs of binary feature alternatives."""
import argparse,json,random
from paired_field_tensor import P
from field_basis_exchange import outer
from free_potential_rank import basis,reduce
from asymmetric_completion import complete

def main(o):
    body=json.loads((P/o.start).read_text())['terms'];fs=[tuple(t[:2])for t in body]
    if o.minors:
        rr=random.Random(o.seed);add=[]
        for _ in range(o.minors):
            (a,b),(c,d)=rr.sample(fs,2);add.append((a^c,b));add.append((c,d^b))
        fs.extend(t for t in add if t not in fs)
    all_r1=complete(fs);allf=list(dict.fromkeys([*fs,*[tuple(t)for t in all_r1['new_directions']]]))
    selected=[];features=[];ds={}
    for i,(a,b)in enumerate(allf):
        z=outer(a,b);rg=0
        while z:
            k=z.bit_length()-1
            if k not in ds:
                j=len(selected);ds[k]=(z,rg^(1<<j));selected.append(i);rg=1<<j;break
            y,g=ds[k];z^=y;rg^=g
        features.append(rg)
    assert selected[:len(body)]==list(range(len(body)))
    depend=[i for i in range(len(allf))if i not in selected];ac=[0]*len(allf)
    for j,i in enumerate(depend):
        ac[i]=1<<j
        for k,h in enumerate(selected):ac[h]|=((features[i]>>k)&1)<<j
    rhs=[*[w for a,b,w in body],*[0]*(len(allf)-len(body))]
    data=dict(args=vars(o),sample_features=allf,augmented_rank=len(selected),existing_terms=len(body),nullity=len(depend),constraint_rows=ac,rhs=rhs,full_exact_rank_one_count=len(allf))
    (P/f'minor_constraints_{o.seed}.json').write_text(json.dumps(data,indent=1)+'\n');print(len(allf),len(selected),len(depend))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('start');p.add_argument('minors',type=int);p.add_argument('seed',type=int);main(p.parse_args())
