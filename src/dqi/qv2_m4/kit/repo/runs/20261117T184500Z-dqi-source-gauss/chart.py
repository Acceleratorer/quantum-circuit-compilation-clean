"""Two source heads act by one involution and a linear translation on a jet."""
import argparse
import collections
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import sys
import time

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "20261117T181300Z-dqi-projective-carry"))
from probe import Field
from block_identity import direct

ZERO = (0, 0)
ONE = (1, 0)


def to_chart(f, n, d, e):
    if d == ZERO:
        return True, ZERO, f.kmul(e, f.kinv(n))
    inverse = f.kinv(d)
    return False, f.kmul(n, inverse), f.kmul(e, inverse)


def representative(chart):
    infinity, r, t = chart
    return (ONE, ZERO, t) if infinity else (r, ONE, t)


def shear(f, chart, h, u):
    infinity, r, t = chart
    if infinity:
        numerator = f.add(t, (u, 0))
        if h == ZERO:
            return True, ZERO, numerator
        ih = f.kinv(h)
        return False, ih, f.kmul(numerator, ih)
    den = f.add(ONE, f.kmul(h, r))
    numer = f.add(t, f.scale(r, u))
    if den == ZERO:
        return True, ZERO, f.kmul(numer, h)
    inv_den = f.kinv(den)
    return False, f.kmul(r, inv_den), f.kmul(numer, inv_den)


def translate(f, chart, h, deriv):
    infinity, r, t = chart
    return chart if infinity else (False, f.add(r, h), f.add(t, deriv))


def coefficients(f, a, b, pa, pb):
    k = f.kap(b, a)
    ki = f.inv(k)
    gamma = f.ksqrt(f.add((2 * a, 1), (k, 0)))
    v = f.add((f.sqrt(pb[0]), 0), f.scale(gamma, f.sqrt(pb[1])))
    return f.at(pa, a), f.sqrt(pa[1]), f.scale(f.at(pb, a), ki), f.scale(v, ki)


def pair(f, chart, coeffs, reverse=False):
    h, u, j, v = coeffs
    if reverse:
        return shear(f, translate(f, chart, j, v), h, u)
    return translate(f, shear(f, chart, h, u), j, v)


def invert_pivot(f, chart):
    infinity, r, t = chart
    if infinity:
        return False, ZERO, t
    if r == ZERO:
        return True, ZERO, t
    i = f.kinv(r)
    return False, i, f.kmul(t, i)


def single(f, chart, a, p, reverse=False):
    k = f.kap(0, a)
    ki = f.inv(k)
    _, _, j, v = coefficients(f, a, 0, ZERO, p)
    # The public scaling (n,e) /= k leaves e/n invariant at infinity.
    def scale_chart(c, scalar):
        inf, r, t = c
        return c if inf else (False, f.scale(r, scalar), f.scale(t, scalar))
    if reverse:
        return invert_pivot(f, scale_chart(translate(f, chart, j, v), k))
    return translate(f, scale_chart(invert_pivot(f, chart), ki), j, v)


def inv0(f, x):
    return f.kinv(x) if x != ZERO else ZERO


def restore(f, heads, flags, count):
    geometries = [None] * count
    geometries[0] = (f.kinv(f.at(heads[0], 0)), None)
    for a in range(count - 1, 0, -1):
        s = 2 * a - 1
        p = f.at(heads[s], a)
        x = inv0(f, f.ksqrt(f.at(heads[s + 1], a)))
        tn = f.add(x, (f.sqrt(heads[s][1]), 0))
        chart = to_chart(f, ONE, p, tn)
        if flags.get(s):
            chart = invert_pivot(f, chart)
        for b in reversed(range(1, a)):
            chart = pair(f, chart, coefficients(f, a, b, heads[2*b-1], heads[2*b]), True)
        inf, r, t = single(f, chart, a, heads[0], True)
        assert not inf
        yp = f.ksq(f.scale(f.add(t, f.ksqrt(r)), f.inv(f.sqrt(f.kap(0, a)))))
        geometries[a] = (r, yp)
    return geometries


def extract_normalized(f, geometry):
    heads = [f.coeff(f.kinv(geometry[0][0]), 0)]
    flags = {}
    infinity_steps = 0
    for a in range(1, len(geometry)):
        y, yp = geometry[a]
        e = f.add(f.scale(f.ksqrt(yp), f.sqrt(f.kap(0, a))), f.ksqrt(y))
        chart = single(f, (False, y, e), a, heads[0])
        infinity_steps += chart[0]
        for b in range(1, a):
            chart = pair(f, chart, coefficients(f, a, b, heads[2*b-1], heads[2*b]))
            infinity_steps += chart[0]
        infinity, r, t = chart
        s = 2*a-1
        if s >= 19:
            flags[s] = not infinity and r == ZERO
            if flags[s]:
                chart = invert_pivot(f, chart)
        infinity, r, t = chart
        if not infinity and r == ZERO:
            raise ZeroDivisionError
        reciprocal = ZERO if infinity else f.kinv(r)
        tn = t if infinity else f.kmul(t, reciprocal)
        pa = f.coeff(reciprocal, a)
        x = f.add(tn, (f.sqrt(pa[1]), 0))
        heads += [pa, f.coeff(f.ksq(inv0(f, x)), a)]
    return heads, flags, infinity_steps


def pack(f, chart):
    inf, r, t = chart
    return int(inf) | r[0] << 1 | r[1] << (1+f.n) | t[0] << (1+2*f.n) | t[1] << (1+3*f.n)


def exact():
    f = Field(2, 7, 2)
    words = list(itertools.product(range(f.q), repeat=2))
    charts = [(False, x, t) for x in words for t in words] + [(True, ZERO, t) for t in words]
    rng = random.Random(1845)
    count = negative = poles = 0
    for pa, pb in itertools.product(words, repeat=2):
        coeffs = coefficients(f, 1, 0, pa, pb)
        for x in charts:
            expect = to_chart(f, *direct(f, [(0, pa, pb)], *representative(x), 1))
            out = pair(f, x, coeffs)
            assert out == expect and pair(f, out, coeffs, True) == x
            poles += out[0]
            h, u, j, v = coeffs
            bad = pair(f, out, (h, u ^ 1, j, v), True)
            mask = rng.randrange(1 << (4*f.n+1))
            negative += ((pack(f, x) ^ pack(f, bad)) & mask).bit_count() % 2
            count += 1
    assert negative
    return dict(field_bits=2, cases=count, all_forward_and_inverse_pass=True,
                output_at_infinity=poles, corrupted_derivative_phase_failures=negative)


def physical(seed, samples):
    sys.path.insert(0, str(ROOT / "src/dqi_v8"))
    import v8_model as v
    f = Field(12, 0x1053, 2048)
    rng = random.Random(seed)
    rows = collections.Counter()
    for i in range(samples):
        weight = [16,17,18,19,23,26,29,32,33,34,35][i % 11]
        err = {v.M.EXP[p]:rng.randrange(1,4096) for p in rng.sample(range(4095),weight)}
        syr = v.M.syndromes(err)
        _, geom, _, _ = v.data8(syr)
        data = [geom[a] for a in range(17)]
        ref = None
        try:
            ref = v.extractor_old(geom)
        except v.M.DomainFailure:
            pass
        try:
            heads, flags, infinity = extract_normalized(f, data)
        except ZeroDivisionError:
            assert ref is None
            rows["matching_rejections"] += 1
            continue
        assert ref is not None and heads == ref[0] and flags == ref[1]
        back = restore(f, heads, flags, len(data))
        assert back[0][0] == data[0][0] and back[1:] == data[1:]
        rows["all33_heads_and_full_source_return_pass"] += 1
        rows["gap_flags_encountered"] += sum(flags.values())
        rows["intermediate_infinity_points"] += infinity
        rows[f"admitted_weight_{weight}"] += 1
    return dict(seed=seed, samples=samples, counters=dict(rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["exact", "physical"])
    parser.add_argument("--seed", type=int, default=1845)
    parser.add_argument("--samples", type=int, default=88)
    args = parser.parse_args()
    start = time.time()
    name = args.mode if args.mode == 'exact' else f'physical_{args.seed}'
    receipt = dict(evidence="diagnostic", utc_start_epoch=start, pid=os.getpid(),
                   affinity=sorted(os.sched_getaffinity(0)), source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    output = HERE / f'{name}.json'
    output.write_text(json.dumps(dict(receipt,status="running"),indent=2)+'\n')
    values = exact() if args.mode == 'exact' else physical(args.seed, args.samples)
    receipt.update(values, elapsed_seconds=time.time()-start,status="complete")
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)


if __name__ == "__main__":
    main()
