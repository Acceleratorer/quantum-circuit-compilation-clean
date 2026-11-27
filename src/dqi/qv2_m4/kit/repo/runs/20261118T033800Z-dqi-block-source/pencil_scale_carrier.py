"""Carry one omitted amplitude scale through the actual 33-head extraction and synthesis."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path
import random
import time

from source_panel import HERE, M
from source_maps import Field, extract, v
from return_peel import norm, tails

F = Field(12, 0x1053, 2048)
ZERO = (0, 0)
with_seed = inspect.getsource(extract).replace(
    'def extract(F,Yd,first_test=19):', 'def extract_with_seed(F,Yd,seed,first_test=19):'
).replace('c=(1,0);flags={}', 'c=seed;flags={}')
assert with_seed != inspect.getsource(extract) and 'c=seed;' in with_seed
scope = vars(__import__(extract.__module__)).copy()
exec(compile(with_seed, '<independent seeded extract>', 'exec'), scope)
seeded_extract = scope['extract_with_seed']
PRIOR = HERE.parent / '20261117T214100Z-dqi-direct-bezout'
WEIGHTS = [float(row.split()[1]) for row in (PRIOR / 'physical_locators.dat').read_text().splitlines()]


def physical_errors(rng, w, law, j):
    points = rng.sample(range(1, 4096), w)
    err = {x: rng.randrange(1, 4096) for x in points}
    if law != 'axis' or w < 2:
        return err
    # Force Y[0].lo==Y[0].hi (first reciprocal coordinate zero), or Y[0].hi==0.
    def functional(x):
        pair = F.scale(F.kinv((x, 1)), M.mul(x, M.peval(v.U, x)))
        return (pair[0] ^ pair[1]) if j % 2 else pair[1]
    pivot = next((x for x in points if functional(x)), None)
    if pivot is None:
        return err
    s = 0
    for x in points:
        if x != pivot:
            s ^= M.mul(err[x], functional(x))
    if s:
        err[pivot] = M.div(s, functional(pivot))
    return err


def assess(err, rng, counts):
    S = M.syndromes(err)
    raw = v.data8(S)
    Y = [raw[1][a] for a in range(17)]
    if Y[0][0] == ZERO:
        counts['original_first_pivot_zero'] += 1
        return
    head0 = F.coeff(F.kinv(Y[0][0]), 0)
    i = int(head0[0] == 0)
    lam = M.inv(head0[i])
    li = M.inv(lam)
    scaled_s = [M.mul(x, li) for x in S]
    scaled = v.data8(scaled_s)
    ys = [scaled[1][a] for a in range(17)]
    assert all(y == F.scale(y0,li) and d == F.scale(d0,li) for (y,d),(y0,d0) in zip(ys,Y))
    try:
        head, flags, unit_carry, recs = extract(F, ys)
        raw_head, raw_flags, raw_carry, raw_recs = extract(F, Y)
        H, G, stored, timeline = seeded_extract(F, ys, (lam,0))
    except ZeroDivisionError:
        counts['original_or_scaled_unprotected_pivot_zero'] += 1
        return
    assert head == H and flags == G and head[0][i] == 1
    assert all(F.scale(c0,lam)==s0 and F.scale(c1,lam)==s1 and f==g
               for (c0,c1,f),(s0,s1,g) in zip(recs,timeline))
    assert F.scale(unit_carry,lam) == stored
    counts['primary_coordinate' if i==0 else 'alternate_coordinate'] += 1
    counts['scale_unit'] += lam==1
    counts['full_ext_carry_same_as_raw'] += stored==raw_carry
    counts['scale_covariant_flags'] += flags==raw_flags
    for h,hr in zip(head,raw_head):
        counts['nonzero_normalized_head'] += h!=ZERO
        if h!=ZERO and hr!=ZERO:
            z = F.kmul(h,F.kinv(hr))
            counts['normalized_head_has_nonreal_relative_scale'] += z[1]!=0
    g, ii = scaled[2:]
    A = v.pass_e(head,g[0],1,v.e_init(1,*g,True),True)
    B = v.pass_e(head,ii[0],1,v.e_init(1,*ii,False),False)
    n0,d0,fl,p33,_ = v.end_block(A,B)
    v._true_P33[0] = p33
    rt = v.native_return(head,n0,d0,fl)
    if not rt.startswith('ret_ok'):
        counts['native_baseline_return_failure'] += 1
        return
    # The return-synthesis gauge itself may depend on the stored carry, since it cancels at all ratios.
    rho = norm(F,stored)
    states = tails(head,M.pscale(n0,rho),M.pscale(d0,rho))
    N,D = states[0]
    deriv = v.C.deriv(D)
    assert all(M.peval(D,x)==0 for x in err)
    num=den=1
    for a in range(1,17):
        s=2*a-1
        at=M.alpha(a)
        w=M.pevalK(D,at)
        ns,ds=states[s]
        pivot_poly=ds if flags.get(s,False) else ns
        if w==ZERO:
            w=M.pevalK(deriv,at)
            pivot_poly=v.C.deriv(pivot_poly)
            counts['differentiated_source_sites']+=1
        if flags.get(s,False):
            counts['swapped_source_sites']+=1
        u=M.pevalK(pivot_poly,at)
        prior,nxt,_=recs[a-1]
        ok=(w!=ZERO and F.kmul(u,prior)==F.kmul(w,nxt))
        counts['wrong_forward_factors']+=not ok
        num=M.mul(num,norm(F,u))
        den=M.mul(den,norm(F,w))
    if not num or not den:
        counts['no_forward_unit']+=1
        return
    scale=M.div(M.mul(norm(F,stored),den),num)
    counts['scale_restored']+=lam==scale
    counts['wrong_scale']+=lam!=scale
    wrong=M.mul(norm(F,stored),den)
    counts['negative_uncharged_wrong_scale']+=wrong!=lam
    mask=rng.randrange(1,4096)
    counts['negative_wrong_mask']+=((wrong^lam)&mask).bit_count()%2
    assert all(M.mul(s,scale)==e for s,e in zip(scaled_s,S)) or scale!=lam
    for x,e in err.items():
        denx=M.mul(x,M.mul(M.peval(v.U,x),M.peval(deriv,x)))
        if not denx:
            counts['zero_physical_denominator']+=1
        else:
            out=M.mul(scale,M.div(M.peval(N,x),denx))
            counts['correct_original_amplitude' if out==e else 'wrong_original_amplitude']+=1
    counts['verified_original_returns']+=scale==lam


def main():
    p=argparse.ArgumentParser()
    p.add_argument('law',choices=['weighted','allweight','axis','full','gap'])
    p.add_argument('seed',type=int)
    p.add_argument('shots',type=int)
    a=p.parse_args()
    start=time.monotonic();rng=random.Random(a.seed);counts=Counter()
    print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),law=a.law,shots=a.shots)),flush=True)
    for j in range(a.shots):
        if a.law=='weighted':
            w=rng.choices(range(19,36),WEIGHTS)[0]
        elif a.law=='allweight':
            w=19+j%17
        elif a.law=='gap':
            w=19+j%11
        elif a.law=='axis':
            w=19+(j//2)%17
        else:
            w=35
        assess(physical_errors(rng,w,a.law,j),rng,counts)
    output=dict(law=a.law,seed=a.seed,shots=a.shots,counts=counts,seconds=time.monotonic()-start,
                cpu=sorted(os.sched_getaffinity(0)),pid=os.getpid(),utc=datetime.now(timezone.utc).isoformat(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope='word-level original scaled extraction, seeded carry, arbitrary physical synthesis scale, end return, all root amplitudes; source/scanner qubit and gate fees separate')
    (HERE/f'pencil_scale_carrier_{a.seed}.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output),flush=True)


if __name__=='__main__':
    main()
