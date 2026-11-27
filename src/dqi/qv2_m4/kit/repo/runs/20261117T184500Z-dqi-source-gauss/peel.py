"""Recover row carry factors from existing source-synthesis polynomial evaluations."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import sys
import time
from chart import HERE, ROOT
sys.path.insert(0,str(ROOT/'src/dqi_v8'))
import v8_model as v
from probe import Field,extract

M=v.M
zero=(0,0)
one=(1,0)


def run(seed, shots,weights):
    f=Field(12,0x1053,2048);rng=random.Random(seed);count=collections.Counter()
    by=collections.defaultdict(collections.Counter);sample=[]
    for i in range(shots):
        t=weights[i%len(weights)]
        err={M.EXP[p]: rng.randrange(1,4096) for p in rng.sample(range(4095),t)}
        _,geom,g,ii=v.data8(M.syndromes(err))
        try:
            P,flags,c,recs=extract(f,[geom[a] for a in range(17)])
            ref=v.extractor_old(geom)
            assert (P,flags,c)==ref
        except (ZeroDivisionError,M.DomainFailure):
            count['matching_oracle_extraction_failure']+=1;continue
        # This model uses unit scale 1 at both end nodes; the product below
        # is scale independent for any common nonzero end-seed gauge.
        A=v.pass_e(P,g[0],1,v.e_init(1,g[0],g[1],True),True)
        B=v.pass_e(P,ii[0],1,v.e_init(1,ii[0],ii[1],False),False)
        n,d,fl,_,_=v.end_block(A,B)
        tail={}
        for s in range(32,-1,-1):
            n,d=d,M.padd(M.pmul(v.C.q(v.SLOT_NODE[s]),n),M.pmul(list(P[s]),d))
            tail[s]=(n,d)
        fullD=d;fullN=n
        num=den=one;badnum=one;missing=0;ngap=0
        for a in range(1,17):
            s=2*a-1;al=M.alpha(a)
            dval=M.pevalK(fullD,al); nval=M.pevalK(fullN,al)
            pn,pd=tail[s]
            swap=flags.get(s,False)
            src=pd if swap else pn
            wrong=pn if swap else pd
            qv=M.pevalK(src,al); qwrong=M.pevalK(wrong,al)
            if dval==zero:
                count['linear_first_derivative_fallbacks']+=1
                assert nval==qv==qwrong==zero
                dval=M.pevalK(v.C.deriv(fullD),al)
                nval=M.pevalK(v.C.deriv(fullN),al)
                qv=M.pevalK(v.C.deriv(src),al)
                qwrong=M.pevalK(v.C.deriv(wrong),al)
                if dval==zero:
                    count['unresolved_higher_multiplicity']+=1;missing+=1;continue
            assert M.kmul(dval,geom[a][0])==nval
            prev,new,actualswap=recs[a-1]
            ratio=M.kmul(new,M.kinv(prev))
            if M.kmul(ratio,dval)!=qv:
                count['wrong_factor']+=1
                if len(sample)<12:sample.append(dict(t=t,a=a,q=qv,d=dval,ratio=ratio,swap=swap))
            else:count['exact_node_factor']+=1
            num=M.kmul(num,qv);den=M.kmul(den,dval)
            # Wrong choice at every row, deliberately tests the quotient sign.
            badnum=M.kmul(badnum,qwrong)
            ngap+=swap
        if missing:continue
        correct=M.kmul(c,den)==num
        count['carry_product_pass' if correct else 'carry_product_fail']+=1
        by[t]['exact' if correct else 'failed']+=1
        by[t]['gap_swaps']+=ngap
        count['wrong_tail_negative']+=badnum!=M.kmul(c,den)
    return dict(shots=shots,seed=seed,weights=weights,counts=dict(count),weight_groups={k:dict(s) for k,s in by.items()},mismatches=sample)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);ap.add_argument('--shots',type=int,required=True)
    ap.add_argument('--weights',required=True);a=ap.parse_args()
    w=[int(s) for s in a.weights.split(',')];t=time.monotonic()
    out=run(a.seed,a.shots,w)
    out.update(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),evidence='diagnostic V8 unchanged 33-head extractor reference and complete V8 end/synthesis word model',seconds=time.monotonic()-t)
    (HERE/f'peel_{a.seed}.json').write_text(json.dumps(out,indent=1)+'\n')
    print(out['counts'],flush=True)
    assert not out['counts'].get('wrong_factor') and not out['counts'].get('carry_product_fail') and not out['counts'].get('unresolved_higher_multiplicity')


if __name__=='__main__':main()
