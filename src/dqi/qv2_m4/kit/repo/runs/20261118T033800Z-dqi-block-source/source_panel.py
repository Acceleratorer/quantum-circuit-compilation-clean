"""Block the two-polynomial source change used by the physical half-Bezout converter."""
import argparse
from collections import Counter
from functools import lru_cache
import json
import os
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '20261117T214100Z-dqi-direct-bezout'))
from source_maps import M, physical


def add(a, b): return M.trim(M.padd(a, b))
def mul(a, b): return M.trim(M.pmul(a, b))
def scale(a, s): return M.trim(M.pscale(a, s))


def divexact(p, m):
    q, r = M.pdivmod(p, m) if p else ([], [])
    assert not M.trim(r)
    return M.trim(q)


def pair_step(a, b, node):
    a0, b0 = M.peval(a, node), M.peval(b, node)
    if not b0: raise ZeroDivisionError
    r = M.div(a0, b0); c = divexact(add(a, scale(b, r)), [node, 1])
    c0 = M.peval(c, node)
    if not c0: raise ZeroDivisionError
    q = M.div(b0, c0); d = divexact(add(b, scale(c, q)), [node, 1])
    return c, d, r, q


def rebuild(a, b, parameters):
    for node, r, q in reversed(parameters):
        b = add(mul(b, [node, 1]), scale(a, q))
        a = add(mul(a, [node, 1]), scale(b, r))
    return a, b


def run_panel(a, b, nodes):
    h = [1]
    for node in nodes: h = mul(h, [M.mul(node,node),0,1])
    ah, al = M.pdivmod(a, h); bh, bl = M.pdivmod(b, h)
    al, bl = M.trim(al), M.trim(bl)
    local = []; counts = Counter()
    for node in nodes:
        counts['local_scale_coefficients'] += max(0,len(bl)-1) + max(0,len(al)-2)
        al, bl, r, q = pair_step(al, bl, node); local.append((node,r,q))
    p00, p10 = rebuild([1], [], local); p01, p11 = rebuild([], [1], local)
    assert add(mul(p00,p11),mul(p01,p10)) == h
    c = add(al,add(mul(p11, ah),mul(p01,bh)))
    d = add(bl,add(mul(p10, ah),mul(p00,bh)))
    assert rebuild(c, d, local) == (M.trim(a),M.trim(b))
    plain, other = a,b
    for i,(node,r,q) in enumerate(local):
        plain,other,r0,q0 = pair_step(plain,other,node)
        assert r0==r and q==q0
    assert (c,d) == (plain,other)
    n = len(a)-1;k=len(nodes)
    # At fixed outside evaluation points the two-by-two source entries are
    # all dynamic. These are explicit scalar products per surviving node.
    counts['bulk_matrix_at_full_output_length'] = 4*max(0,n-k+1) if ah or bh else 0
    counts['bulk_only_occupied_high_pairs'] = 4*max(len(ah),len(bh))
    counts['affine_divisions'] = 2*k
    counts['source_pairs'] = k
    counts['old_single_step_products'] = sum(2*(n-j)-1 for j in range(k))
    return c,d,local,counts


def main():
    p=argparse.ArgumentParser();p.add_argument('--widths',required=True);p.add_argument('--shots',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--physical',action='store_true');arg=p.parse_args()
    rng=random.Random(arg.seed); widths=[int(v) for v in arg.widths.split(',')]; start=time.monotonic(); races=Counter(); bills={}
    print(json.dumps(dict(pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),shots=arg.shots,widths=widths)),flush=True)
    for j in range(arg.shots):
        if arg.physical:
            actual=physical(rng,[35,34,33,32,29,25,21,19][j%8]);
            if actual is None:races['source_rejected']+=1;continue
            D = actual[0];a=[M.sqrt(x) for x in D[1::2]];b=[M.sqrt(x) for x in D[::2]];b=add(b,scale(a,M.div(b[-1],a[-1])))
        else:
            a=[rng.randrange(4096) for _ in range(17)]+[rng.randrange(1,4096)];b=[rng.randrange(4096) for _ in range(17)]
        for width in widths:
            aa,bb=a,b; params=[]; bill=Counter()
            try:
                for lo in range(0,17,width):
                    aa,bb,pars,counts=run_panel(aa,bb,range(lo,min(17,lo+width)));params+=pars;bill+=counts
            except ZeroDivisionError:races['zero_'+str(width)]+=1;continue
            assert rebuild(aa,bb,params)==(M.trim(a),M.trim(b))
            races['exact_'+str(width)]+=1;bills[width]=dict(bill)
    out=dict(source='physical D split into odd and even coefficient square roots' if arg.physical else 'unconstrained uniform GF4096 polynomials',status='diagnostic',counts=dict(races),prices=bills,seed=arg.seed,shots=arg.shots,seconds=time.monotonic()-start,pid=os.getpid(),affinity=sorted(os.sched_getaffinity(0)),unpriced='scalar inverse, HMR, public-basis in-place staging, constructing four transfer entries from the 2k chart, exceptional transitions and external converter')
    (HERE/f'source_panel_{arg.seed}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)


if __name__=='__main__':main()
