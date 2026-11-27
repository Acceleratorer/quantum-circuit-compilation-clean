"""Check full-alphabet DQI source maps in two coordinate systems."""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / 'runs/20261117T184500Z-dqi-source-gauss'
sys.path.insert(0, str(PREVIOUS))
from return_peel import Field, M, extract, v


def xor(xs):
    y = 0
    for x in xs:
        y ^= x
    return y


def dot(x, y):
    return xor(M.mul(a, b) for a, b in zip(x, y))


def transpose(rows):
    return list(zip(*rows))


def mv(matrix, x):
    return [dot(row, x) for row in matrix]


def inverse(rows):
    n = len(rows)
    a = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next(k for k in range(j, n) if a[k][j])
        a[pivot], a[j] = a[j], a[pivot]
        a[j] = M.pscale(a[j], M.inv(a[j][j]))
        for k in range(n):
            if k != j and a[k][j]:
                a[k] = M.padd(a[k], M.pscale(a[j], a[k][j]))
    return [row[n:] for row in a]


@lru_cache(None)
def matrices(n):
    ev = []
    for i in range(n):
        powers = [1]
        for _ in range(n - 1):
            powers.append(M.mul(powers[-1], i))
        ev.append(powers)
    iv = inverse(ev)
    cauchy = [[M.inv(i ^ j) if i != j else 0 for j in range(n)] for i in range(n)]
    return ev, iv, transpose(iv), cauchy


def direct(D, z, bad_diagonal=False):
    n = len(z)
    _, iv, it, cauchy = matrices(n)
    t = mv(it, z)
    a = [M.peval(D, i) for i in range(n)]
    b = [M.peval(v.C.deriv(D), i) for i in range(n)]
    u = [M.mul(d, x) for d, x in zip(b, t)]
    w = [M.mul(d, x) for d, x in zip(a, t)]
    h, k = mv(cauchy, u), mv(cauchy, w)
    result = [M.mul(d, c) ^ M.mul(e, f if bad_diagonal else f ^ q)
              for d, e, c, f, q in zip(a, b, h, k, u)]
    return mv(iv, result)


def physical(rng, weight):
    field = Field(12, 0x1053, 2048)
    err = {M.EXP[p]: rng.randrange(1, 4096) for p in rng.sample(range(4095), weight)}
    _, geom, g, ii = v.data8(M.syndromes(err))
    try:
        heads, _, _, _ = extract(field, [geom[a] for a in range(17)])
    except ZeroDivisionError:
        return None
    A = v.pass_e(heads, g[0], 1, v.e_init(1, *g, True), True)
    B = v.pass_e(heads, ii[0], 1, v.e_init(1, *ii, False), False)
    n, d, fl, p33, _ = v.end_block(A, B)
    v._true_P33[0] = p33
    if not v.native_return(heads, n, d, fl).startswith('ret_ok'):
        return None
    N, D = v.synth(heads, n, d)
    scale = rng.randrange(1, 4096)
    D = (M.pscale(D, scale) + [0] * 36)[:36]
    N = (M.pscale(N, scale) + [0] * 35)[:35]
    try:
        z = M.conversion(D, N, M.Euclid())
    except (M.DomainFailure, ZeroDivisionError):
        return None
    return D, N, z


def horner(p, z):
    return [dot(p[i + 1:], z) for i in range(len(z))]


def standard_direct(D, z):
    d = v.C.deriv(D)
    N = M.trim(M.padd(M.pmul(D, horner(d, z)), M.pmul(d, horner(D, z))))
    assert len(N) <= len(z)
    return (N + [0] * len(z))[:len(z)]


def triangular(D, z, solve, count):
    a = D[:0:-1]
    data = list(z)
    if solve:
        data.reverse()

    def recurse(lo, hi):
        if hi - lo == 1:
            data[lo] = M.mul(M.inv(a[0]) if solve else a[0], data[lo])
            count['unit_products'] += 1
            return
        mid = (lo + hi) // 2
        left, right = mid - lo, hi - mid
        if solve:
            recurse(lo, mid)
        else:
            recurse(mid, hi)
        width = right + left - 1
        ev, _, it, _ = matrices(width)
        forms = mv(it, a[1:1 + width])
        old_left = list(data[lo:mid][::-1])
        for point in range(width):
            coeff = M.mul(forms[point], M.peval(old_left, point))
            for j in range(right):
                data[mid + j] ^= M.mul(coeff, ev[point][j])
        count['field_products_cross'] += width
        count['disjoint_blocks'] += 1
        if solve:
            recurse(mid, hi)
        else:
            recurse(lo, mid)

    recurse(0, len(z))
    return data if solve else data[::-1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['cauchy', 'triangular'])
    p.add_argument('--shots', type=int, required=True)
    p.add_argument('--seed', type=int, required=True)
    args = p.parse_args()
    rng, counts = random.Random(args.seed), Counter()
    start = time.monotonic()
    print(f'{args.mode} pid={os.getpid()} cpu={sorted(os.sched_getaffinity(0))}', flush=True)
    for j in range(args.shots):
        n = 35
        if args.mode == 'cauchy' and j % 3 == 0:
            wt = [35, 34, 33, 32, 31, 29, 27, 25, 21, 19][(j // 3) % 10]
            physical_case = physical(rng, wt)
            if physical_case is None:
                counts['existing_source_rejections'] += 1
                continue
            D, N, z = physical_case
            counts['physical_weight_' + str(wt)] += 1
        else:
            D = [rng.randrange(4096) for _ in range(n)] + [rng.randrange(1, 4096)]
            z = [rng.randrange(4096) for _ in range(n)]
            if args.mode == 'cauchy' and j % 7 == 1:
                # Make an actual double root at the public evaluation point 0.
                D[0] = D[1] = 0
                counts['dirty_forced_double_root'] += 1
            N = standard_direct(D, z)
            counts['dirty'] += 1
        if args.mode == 'cauchy':
            assert standard_direct(D, z) == direct(D, z) == N
            counts['wrong_diagonal_detected'] += direct(D, z, True) != N
        else:
            fwd, rev = Counter(), Counter()
            h = triangular(D, z, False, fwd)
            assert h == M.horner_R(D, z)
            assert triangular(D, h, True, rev) == z and fwd == rev
            counts.update(fwd)
        counts['exact'] += 1
    data = dict(mode=args.mode, seed=args.seed, shots=args.shots, counts=dict(counts),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                pid=os.getpid(), affinity=sorted(os.sched_getaffinity(0)), seconds=time.monotonic()-start,
                evidence='diagnostic source-level map, variable width and mask return separately required')
    (HERE / f'{args.mode}_{args.seed}.json').write_text(json.dumps(data, indent=1) + '\n')
    print(data, flush=True)


if __name__ == '__main__':
    main()
