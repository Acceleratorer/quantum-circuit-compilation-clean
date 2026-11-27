"""Own word-level arithmetic for the DQI decoder algebra (no kickmix, no generator imports).

GF(2^12) = GF(2)[x]/(x^12+x^6+x^4+x+1) (0x1053, the competition field).
GF(2^24) = GF(2^12)[w]/(w^2+w+K), K = 2048, packed as lo | hi<<12 (value lo + hi*w): the generator's convention.
Polynomials over GF(2^12): python lists, low coefficient first.
"""
MOD = 0x1053
K = 2048
M12 = 4095


def _build():
    exp = [0] * 8190
    log = [0] * 4096
    x = 1
    for i in range(4095):
        exp[i] = x
        log[x] = i
        x <<= 1
        if x & 4096:
            x ^= MOD
    assert x == 1  # x is primitive for 0x1053
    for i in range(4095, 8190):
        exp[i] = exp[i - 4095]
    return exp, log


EXP, LOG = _build()


def mul(a, b):
    if not a or not b:
        return 0
    return EXP[LOG[a] + LOG[b]]


def inv(a):
    assert a, 'inverse of zero in GF(2^12)'
    return EXP[4095 - LOG[a]]


def div(a, b):
    return mul(a, inv(b))


def emul(x, y):
    a, b = x & M12, x >> 12
    c, d = y & M12, y >> 12
    bd = mul(b, d)
    return (mul(a, c) ^ mul(K, bd)) | ((mul(a, d) ^ mul(b, c) ^ bd) << 12)


def conj(x):
    # Frobenius x -> x^(2^12): w -> w+1
    a, b = x & M12, x >> 12
    return (a ^ b) | (b << 12)


def norm(x):
    a, b = x & M12, x >> 12
    return mul(a, a) ^ mul(a, b) ^ mul(K, mul(b, b))


def einv(x):
    assert x, 'inverse of zero in GF(2^24)'
    t = inv(norm(x))
    a, b = x & M12, x >> 12
    return mul(a ^ b, t) | (mul(b, t) << 12)


def ediv(x, y):
    return emul(x, einv(y))


def esq(x):
    return emul(x, x)


def escale(x, c):
    """GF(2^24) element times GF(2^12) scalar."""
    return mul(x & M12, c) | (mul(x >> 12, c) << 12)


# ---- polynomials over GF(2^12) ----
def trim(p):
    p = list(p)
    while len(p) > 1 and not p[-1]:
        p.pop()
    return p


def padd(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0) for i in range(n)])


def pmul(a, b):
    c = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    c[i + j] ^= mul(x, y)
    return trim(c)


def pscale(a, s):
    return trim([mul(x, s) for x in a])


def pdivmod(a, b):
    a = trim(a)
    b = trim(b)
    assert b != [0]
    if len(a) < len(b):
        return [0], a
    out = [0] * (len(a) - len(b) + 1)
    bi = inv(b[-1])
    for k in range(len(a) - len(b), -1, -1):
        t = mul(a[k + len(b) - 1], bi)
        out[k] = t
        if t:
            for j, v in enumerate(b):
                a[k + j] ^= mul(t, v)
    return trim(out), trim(a)


def pev(p, x):
    """Evaluate at a GF(2^12) point."""
    v = 0
    for a in reversed(p):
        v = mul(v, x) ^ a
    return v


def peval(p, g):
    """Evaluate at a GF(2^24) point (packed)."""
    v = 0
    for a in reversed(p):
        v = emul(v, g) ^ a
    return v


def pderiv(p):
    return trim([p[i] if i & 1 else 0 for i in range(1, len(p))]) if len(p) > 1 else [0]


def minpoly(g):
    """Minimal polynomial over GF(2^12) of g in GF(2^24) \\ GF(2^12): z^2 + (g+conj g) z + norm(g)."""
    assert g >> 12
    tr = g ^ conj(g)
    assert not tr >> 12
    return [norm(g), tr, 1]


def coords(v, g):
    """v = a + b*g with a, b in GF(2^12) (g = glo + ghi*w, ghi != 0)."""
    glo, ghi = g & M12, g >> 12
    b = div(v >> 12, ghi)
    a = (v & M12) ^ mul(b, glo)
    return a, b


def head_at(a, b, g):
    return a ^ escale(g, b)


def selftest():
    import random
    r = random.Random(1)
    for _ in range(2000):
        x, y, z = (r.randrange(1 << 24) for _ in range(3))
        assert emul(x, emul(y, z)) == emul(emul(x, y), z)
        assert emul(x, y ^ z) == emul(x, y) ^ emul(x, z)
        if x:
            assert emul(x, einv(x)) == 1
        assert emul(x, conj(x)) == norm(x)
        assert conj(conj(x)) == x
        e = x
        for _ in range(12):
            e = esq(e)
        assert e == conj(x)
    w = 1 << 12
    assert esq(w) == w ^ K
    return True


if __name__ == '__main__':
    print('gf selftest', selftest())
