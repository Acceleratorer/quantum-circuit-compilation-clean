"""Price alternate pairs of omitted real nodes for the degree-17 physical Forney solver."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import random
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'20261118T033800Z-dqi-block-source'))
from quadratic import M, Place, add, divexact, mul, scale


class RealPair(Place):
    def __init__(self,x):
        self.x=x
        self.d=M.mul(x,x)^x
        self.poly=[self.d,1,1]


def frame(a,b,m):
    rb=[M.peval(b,x) for x in (m.x,m.x^1)]
    if not all(rb):
        return None,'b'+str(rb[0]==0)+str(rb[1]==0)
    ra=[M.peval(a,x) for x in (m.x,m.x^1)]
    rr=[M.div(t,z) for t,z in zip(ra,rb)]
    r=[rr[0]^M.mul(m.x,rr[0]^rr[1]),rr[0]^rr[1]]
    c=divexact(add(a,mul(r,b)),m.poly)
    rc=[M.peval(c,x) for x in (m.x,m.x^1)]
    if not all(rc):
        return None,'c'+str(rc[0]==0)+str(rc[1]==0)
    qq=[M.div(t,z) for t,z in zip(rb,rc)]
    q=[qq[0]^M.mul(m.x,qq[0]^qq[1]),qq[0]^qq[1]]
    e=divexact(add(b,mul(q,c)),m.poly)
    assert M.trim(b)==add(mul(m.poly,e),mul(q,c))
    return (c,e),''


def main():
    p=argparse.ArgumentParser()
    p.add_argument('law',choices=('weighted','forced','upper'))
    p.add_argument('shots',type=int)
    p.add_argument('seed',type=int)
    a=p.parse_args()
    rng=random.Random(a.seed)
    raw=HERE.parent/'20261117T214100Z-dqi-direct-bezout/physical_locators.dat'
    rows={int(v[0]):(float(v[1]),list(map(int,v[2:]))) for v in (line.split() for line in raw.read_text().splitlines())}
    events=Counter();st=time.monotonic()
    for case in range(a.shots):
        w=rng.choices(list(rows),weights=[v[0] for v in rows.values()])[0] if a.law=='weighted' else 19+case%17
        roots=rng.sample(range(70,4096),w) if a.law=='upper' else rng.sample(range(1,4096),w)
        if a.law=='forced' and not any(x<32 for x in roots):
            roots[0]=rng.randrange(1,32)
        d=list(rows[w][1])
        for x in roots:
            d=mul(d,[x,1])
        d=scale(d,rng.randrange(1,4096))
        aa=[M.sqrt(x) for x in d[1::2]];ae=[M.sqrt(x) for x in d[::2]]
        b=add(ae,scale(aa,M.div(ae[-1],aa[-1])))
        chosen=set();gaps=0
        for i in range(8):
            for branch in range(3):
                m=RealPair(2*i+16*branch)
                assert m.x not in chosen
                step,why=frame(aa,b,m)
                if why:
                    events[f'failure_depth{i}_{why}_branch{branch}']+=1
                    if branch==0:gaps+=1
                    continue
                aa,b=step;chosen.update((m.x,m.x+1));events[f'use_{branch}']+=1
                break
            else:
                events['three_failed']+=1;break
        events[f'first_choice_gaps_{gaps}']+=1
        if b and b[0] and len(chosen)==16:events['adapted_all_eight']+=1
    result=dict(args=vars(a),counts=dict(events),nodes='All first, backup and third scalar roots are within the omitted mask 0..47; physical input locator from original grade-specific padding.',seconds=time.monotonic()-st,pid=os.getpid(),cpus=sorted(os.sched_getaffinity(0)))
    (HERE/f'held_split_pivots_{a.seed}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
