# SPDX-License-Identifier: Apache-2.0
"""Lane dqi_pair: the public joint kernel J_B (173 ANDs; decoded by lane dqi890 from Syed Asad Ali's compiled v13 DQI
decoder, Apache-2.0, original builder Syed Asad Ali) rewritten in the standard basis:
  inputs hv = head in VALUE view at the node (lo a = c0 + t c1, hi b = c1), m = n (standard K basis);
  outputs y1 ^= (a + b theta) m,  y2 ^= sqrt(b) m.
Writes terms [(u_mask24, v_mask24, w_mask48)] + free linear part, and verifies on random inputs.
  jb_std.py KERNEL.json OUT.json"""
import sys, json, random
sys.path.insert(0, '<REPO>/src/dqi_math')
import model as M
K = json.load(open(sys.argv[1]))
U, V, W, Fl, T0, T, Z = (K[k] for k in ('U', 'V', 'W', 'F_free_linear', 'T0_wire_to_m', 'T_e_basis', 'Z_free_e'))
t = K['node_t']
bits = lambda x, n: [(x >> i) & 1 for i in range(n)]
unbits = lambda v: sum(b << i for i, b in enumerate(v))
def matvec(Mx, v):   # rows of Mx dot v
    return [sum(r[j] & v[j] for j in range(len(v))) & 1 for r in Mx]
def ginv(Mx):
    n = len(Mx); A = [r[:] + [int(i == j) for j in range(n)] for i, r in enumerate(Mx)]
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c]); A[c], A[p] = A[p], A[c]
        for i in range(n):
            if i != c and A[i][c]: A[i] = [x ^ y for x, y in zip(A[i], A[c])]
    return [r[n:] for r in A]
T0i, Ti = ginv(T0), ginv(T)
WT = list(zip(*W))     # W is 48 x 173 or 173 x 48?
if len(W) == 48: Wc = W            # rows = outputs
else: Wc = [list(r) for r in zip(*W)]
def wired(hw, nw):
    p = [(sum(U[k][j] & hw[j] for j in range(24)) & 1) & (sum(V[k][j] & nw[j] for j in range(24)) & 1) for k in range(len(U))]
    o = [(sum(Wc[i][k] & p[k] for k in range(len(p))) + sum(Fl[i][j] & nw[j] for j in range(24))) & 1 for i in range(48)]
    return o
def std(hv, m):          # hv, m ints
    a, b = hv & 4095, hv >> 12
    hw = bits((a ^ M.mul(t, b)) | (b << 12), 24)
    nw = matvec(T0i, bits(m, 24))
    o = wired(hw, nw)
    y1 = unbits(o[:24])
    e = [x ^ y for x, y in zip(o[24:], matvec(Z, nw))]
    y2 = unbits(matvec(Ti, e))
    return y1, y2
rng = random.Random(1); bad = 0
for _ in range(300):
    hv, m = rng.randrange(1 << 24), rng.randrange(1 << 24)
    a, b = hv & 4095, hv >> 12
    want1 = M.kmul((a, b), (m & 4095, m >> 12)); want1 = want1[0] | (want1[1] << 12)
    want2 = M.kscale((m & 4095, m >> 12), M.sqrt(b)); want2 = want2[0] | (want2[1] << 12)
    bad += std(hv, m) != (want1, want2)
print('mismatches', bad)
# standard-basis terms by probing (bilinear: u_k, v_k linear forms; outputs linear in products)
def ulin(k, hv):
    a, b = hv & 4095, hv >> 12
    hw = bits((a ^ M.mul(t, b)) | (b << 12), 24); return sum(U[k][j] & hw[j] for j in range(24)) & 1
def vlin(k, m):
    nw = matvec(T0i, bits(m, 24)); return sum(V[k][j] & nw[j] for j in range(24)) & 1
terms = []
for k in range(len(U)):
    u = sum(ulin(k, 1 << j) << j for j in range(24)); v = sum(vlin(k, 1 << j) << j for j in range(24))
    w1 = sum(Wc[i][k] << i for i in range(24))
    w2col = [Wc[24 + i][k] for i in range(24)]
    w2 = unbits(matvec(Ti, w2col))
    terms.append((u, v, w1 | (w2 << 24)))
# free linear part in standard basis (y = sum terms + L m)
def by_terms(hv, m):
    y = 0
    for u, v, w in terms:
        if bin(u & hv).count('1') & 1 and bin(v & m).count('1') & 1: y ^= w
    return y
lin = []
for j in range(24):
    y1, y2 = std(0, 1 << j); lin.append((y1 | (y2 << 24)) ^ by_terms(0, 1 << j))
bad2 = 0
for _ in range(300):
    hv, m = rng.randrange(1 << 24), rng.randrange(1 << 24)
    y1, y2 = std(hv, m)
    y = by_terms(hv, m)
    for j in range(24):
        if m >> j & 1: y ^= lin[j]
    bad2 += y != (y1 | (y2 << 24))
print('terms', len(terms), 'free-linear nonzero', sum(1 for x in lin if x), 'term-form mismatches', bad2)
json.dump(dict(credit=K['credit'], terms=terms, free_linear=lin, doc=__doc__), open(sys.argv[2], 'w'))
