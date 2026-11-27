"""Recover a measured norm via native polynomial-return states and local selections."""
import argparse
import collections
import hashlib
import json
import random
import time
from pathlib import Path
from peel import HERE, M, Field, extract, v, zero


def norm(f, w):
    x, y = w
    return x ^ f.sqrt(f.mul(x, y)) ^ f.mul(f.sqrt(f.delta), y)


def orientation(f, w):
    x, y = w
    assert x or y
    if x and y:
        return f.mul(x, f.inv(y)), False
    return (1 if x else 2), True


def restore(f, ray, s):
    h, special = ray
    if special:
        return (s, 0) if h == 1 else (0, f.mul(s, f.inv(f.sqrt(f.delta))))
    y = f.mul(s, f.inv(norm(f, (h, 1))))
    return f.mul(h, y), y


def tails(P, n, d):
    result = {}
    for i in range(32, -1, -1):
        n, d = d, M.padd(M.pmul(v.C.q(v.SLOT_NODE[i]), n), M.pmul(list(P[i]), d))
        result[i] = n, d
    return result


def selfcheck():
    for f in [Field(2, 7, 2), Field(4, 0x13, 8)]:
        seen = set()
        for x in range(f.q):
            for y in range(f.q):
                if x or y:
                    w = x, y
                    h, s = orientation(f, w), norm(f, w)
                    assert restore(f, h, s) == w
                    assert f.ksq((s, 0)) == f.kmul(w, (x ^ y, y))
                    seen.add((h, s))
        assert len(seen) == f.q * f.q - 1


def choose(n, d, at):
    v1, v2 = M.pevalK(n, at), M.pevalK(d, at)
    if v1 != zero or v2 != zero:
        return (v1 if v1 != zero else v2), (v2 if v1 != zero else v1), (
            'regular' if v1 != zero else 'swap'
        )
    v1, v2 = M.pevalK(v.C.deriv(n), at), M.pevalK(v.C.deriv(d), at)
    assert v1 != zero or v2 != zero
    return (v1 if v1 != zero else v2), (v2 if v1 != zero else v1), (
        'derivative' if v1 != zero else 'derivative_swap'
    )


def run(shots, seed, weights):
    selfcheck()
    f, rng = Field(12, 0x1053, 2048), random.Random(seed)
    count = collections.Counter()
    by = collections.defaultdict(collections.Counter)
    witnesses = []
    for i in range(shots):
        t = weights[i % len(weights)]
        err = {M.EXP[p]: rng.randrange(1, 4096) for p in rng.sample(range(4095), t)}
        _, geom, g, ii = v.data8(M.syndromes(err))
        try:
            P, flags, c, recs = extract(f, [geom[a] for a in range(17)])
            assert (P, flags, c) == v.extractor_old(geom)
        except (ZeroDivisionError, M.DomainFailure):
            count['extractor_domain_failure'] += 1
            by[t]['extractor_domain_failure'] += 1
            continue
        ray = orientation(f, c)
        A = v.pass_e(P, f.mul(ray[0], g[0]), ray[0], v.e_init(ray[0], *g, True), True)
        B = v.pass_e(P, f.mul(ray[0], ii[0]), ray[0], v.e_init(ray[0], *ii, False), False)
        n, d, flags3, p33, _ = v.end_block(A, B)
        v._true_P33[0] = p33
        native = v.native_return(P, n, d, flags3)
        by[t][native] += 1
        if not native.startswith('ret_ok'):
            count['reference_native_return_failed'] += 1
            continue
        scale = rng.randrange(1, 4096)
        trail = tails(P, M.pscale(n, scale), M.pscale(d, scale))
        n, d = trail[0]
        divisor, bad_product = 1, 1
        den = {}
        for a in range(1, 17):
            at = M.alpha(a)
            w = M.pevalK(d, at)
            if w == zero:
                w = M.pevalK(v.C.deriv(d), at)
                count['den_derivative'] += 1
            assert w != zero
            den[a] = w
            divisor = f.mul(divisor, norm(f, w))
        product = f.inv(divisor)
        bad_product = product
        moved = []
        wrong = []
        for s in range(33):
            a = v.SLOT_NODE[s]
            at = M.alpha(a)
            if s % 2:
                if (n, d) != trail[s]:
                    count['different_reverse_polynomial_pairs'] += 1
                w, bad, kind = choose(n, d, at)
                count[kind] += 1
                ref = f.kmul(recs[a - 1][1], f.kinv(recs[a - 1][0]))
                if f.kmul(ref, den[a]) != w:
                    wrong.append((a, kind))
                product = f.mul(product, norm(f, w))
                bad_product = f.mul(bad_product, norm(f, bad))
            v1 = M.pevalK(n, at)
            pv = f.kmul(M.pevalK(d, at), f.kinv(v1)) if v1 != zero else zero
            h = M.head_coeffs(pv, a)
            if tuple(h) != tuple(P[s]):
                moved.append(s)
            residual = M.padd(d, M.pmul(list(h), n))
            qq, rr = M.pdivmod(residual, v.C.q(a)) if residual else ([], [])
            assert not M.trim(rr)
            n, d = M.trim(qq), M.trim(n)
        prior = norm(f,c)
        mask = rng.randrange(1, 4096)
        phase_paid = ((product ^ prior) & mask).bit_count() % 2 == 0
        wrong_phase = ((bad_product ^ prior) & mask).bit_count() % 2 != 0
        result = restore(f, ray, product) == c
        count['admitted'] += 1
        count['wrong_factors'] += len(wrong)
        count['exact_factors'] += 16-len(wrong)
        count['moved_head_cases'] += bool(moved)
        count['carry_restored' if result else 'carry_failure'] += 1
        count['original_mask_repaid' if phase_paid else 'original_mask_failure'] += 1
        count['negative_wrong_phase'] += wrong_phase
        count['negative_wrong_carry'] += bad_product != prior
        by[t]['exact' if result else 'wrong'] += 1
        if (not result or wrong) and len(witnesses)<8:
            witnesses.append(dict(weight=t, wrong=wrong, moved=moved,scale=scale,actual=prior,got=product))
    return dict(seed=seed,shots=shots,weights=weights,counts=dict(count),by_weight=by,witnesses=witnesses)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--shots',type=int,required=True)
    p.add_argument('--weights',required=True)
    a = p.parse_args()
    start = time.monotonic()
    out = run(a.shots,a.seed,[int(s) for s in a.weights.split(',')])
    out.update(evidence='diagnostic native polynomial return, selected scale-mask recovery, no gate emitter',
               source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               seconds=time.monotonic()-start)
    (HERE/f'return_peel_{a.seed}.json').write_text(json.dumps(out,indent=1)+'\n')
    print(out['counts'],out['witnesses'][:1],flush=True)


if __name__ == '__main__':
    main()
