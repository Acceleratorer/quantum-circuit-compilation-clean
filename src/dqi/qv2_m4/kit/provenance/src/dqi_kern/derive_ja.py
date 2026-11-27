# SPDX-License-Identifier: Apache-2.0
# Lane kernel_flip, own code; the source kernels are the public J_A of Syed Asad Ali's compiled DQI decoder
# (Apache-2.0), original builder Syed Asad Ali.
"""Derive J_A[s] for s without an export from an exported J_A[s'] whose kappa lies in the Frobenius orbit of
kappa(s): if kappa(s)^(2^j) = kappa(s'), then J_A[s](X, n) = phi^-j(J_A[s'](phi^j X, phi^j n)) half-wise, phi = squaring
in K (a GF(2)-linear change of basis, so the rank is unchanged). Every derived kernel is verified (576 basis pairs +
10,000 random) before it is written into kernels.json['JA'][s] with its provenance.
  python3 derive_ja.py S [S ...]"""
import json, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import kernels as K


def kfrob(x, j):
    for _ in range(j % 24): x = K.kmul(x, x)
    return x


def derive(terms, j):
    return [(K.compose_left(u, lambda X: kfrob(X, j)), K.compose_left(v, lambda X: kfrob(X, j)),
             kfrob(w & 0xFFFFFF, 24 - j) | (kfrob(w >> 24, 24 - j) << 24)) for u, v, w in terms]


if __name__ == '__main__':
    d = K.load(); public = {int(s): e for s, e in d['JA'].items() if 'derived_from' not in e}
    for s in map(int, sys.argv[1:]):
        if str(s) in d['JA']: print(s, 'present'); continue
        x, found = K.kappa(s), None
        for j in range(12):
            for s2, e in public.items():
                if K.kappa(s2) == x: found = (j, s2); break
            if found: break
            x = K.fmul(x, x)
        if not found: print(s, 'no exported kernel in the kappa orbit'); continue
        j, s2 = found
        t = derive([tuple(z) for z in public[s2]['terms']], j)
        res = K.verify(t, K.map_ja(s))
        print(s, 'from', s2, 'j', j, res)
        if res['ok']:
            d['JA'][str(s)] = {'map': f'J_A[s={s}]', 'derived_from': s2, 'frobenius_j': j,
                               'source': f"Frobenius conjugate of JA[{s2}] ({public[s2]['source']})",
                               'terms': [list(z) for z in t], 'verification': res}
    tmp = K.HERE / 'kernels.json.tmp'; tmp.write_text(json.dumps(d)); tmp.replace(K.HERE / 'kernels.json')
