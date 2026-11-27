"""Build a native candidate by completing a consistent zero-row dependency to an information set."""
import argparse, json,random,subprocess,time
from pathlib import Path
from paired_field_tensor import P,F,lift
def solve(rows,weights,circuit,rng):
    b={};selection=[*[i for i in range(len(rows))if circuit>>i&1],*rng.sample(range(len(rows)),len(rows))]
    for i in selection:
        v=rows[i];w=weights[i]
        while v:
            j=v.bit_length()-1
            if j not in b:b[j]=(v,w);break
            t,h=b[j];v^=t;w^=h
    f={}
    for j,(v,w)in sorted(b.items()):
        for k,c in f.items():
            if v>>k&1:w^=c
        f[j]=w
    return [w^lift.xor(c for j,c in f.items()if v>>j&1)for v,w in zip(rows,weights)]
def verify(ts):
    for i in range(12):
        for j in range(12):assert lift.xor(w for a,b,w in ts if a>>i&1 and b>>j&1)==F.mul(1<<i,1<<j)|(F.mul(1<<i,F.square(1<<j))<<12)
def main(o):
    tm=time.monotonic();d=json.loads((P/o.input).read_text());rows=d['constraint_rows'];w=d['rhs'];m=len(rows);n=d['nullity'];rng=random.Random(o.seed)
    assert n+24<=64
    path=P/(o.out_stem or f'minorcircuit_{o.seed}');path.mkdir(exist_ok=True);f=path/'input';out=path/'circuits'
    f.write_text(str(m+1)+'\n'+''.join(f'{a} {a|(c<<n)}\n'for a,c in zip(rows,w))+'0 0\n')
    cmd=[str(P/'partition_circuits'),str(f),str(out),str(o.degree),str(o.right),str(o.limit),str(o.rounds),str(o.seed)] if o.right else [str(P/'minor_circuits'),str(f),str(out),str(o.degree),str(o.limit)]
    r=subprocess.run(cmd,capture_output=True,text=True,check=True)
    cs=[x|(y<<64)for x,y in [map(int,l.split())for l in out.read_text().splitlines()]]
    best=list(w);bestc=0
    for c in cs:
        for _ in range(o.trials):
            ww=solve(rows,w,c,rng)
            if sum(bool(x)for x in ww)<sum(bool(x)for x in best):best,bestc=ww,c
    ts=[(*p,b)for p,b in zip(d['sample_features'],best)if b];verify(ts)
    res=dict(args=vars(o),census=r.stdout.strip(),minimal_good_circuits=len(cs),witness_circuit=bestc,rank=len(ts),terms=ts,exact_144_equations=True,seconds=time.monotonic()-tm)
    path.with_suffix('.json').write_text(json.dumps(res,indent=1)+'\n');print(res['census'],len(ts))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('degree',type=int);p.add_argument('limit',type=int);p.add_argument('trials',type=int);p.add_argument('seed',type=int);p.add_argument('--right',type=int,default=0);p.add_argument('--rounds',type=int,default=1);p.add_argument('--out-stem');main(p.parse_args())
