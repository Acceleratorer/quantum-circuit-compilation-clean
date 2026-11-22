from pathlib import Path
from random import Random
import sys
import unittest


ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "exp-049"))
import fma_state_compression as fma


class TailMapFactorizationTests(unittest.TestCase):
    def test_branchless_lu_matches_the_inverse_matrix(self):
        degree, modulus = 12, 0x1053
        mul = lambda left, right: fma.gf_mul(left, right, modulus, degree)
        inv = lambda value: fma.gf_inv(value, modulus, degree)
        rng = Random(0xA66057)
        checked = 0

        while checked < 256:
            a0 = rng.randrange(1 << degree)
            a1 = rng.randrange(1 << degree)
            w0 = a0
            w1 = a0 ^ a1 ^ 1
            w2 = a0 ^ mul(2, a1) ^ 4
            if not w0 or not w1 or not w2:
                continue

            n00 = mul(6, mul(a0, a0)) ^ mul(12, a0)
            n01 = mul(a0, mul(6, a1) ^ 10)
            n11 = (
                mul(6, a0)
                ^ mul(6, mul(a1, a1))
                ^ mul(10, a1)
                ^ 12
            )
            determinant = mul(n00, n11) ^ mul(n01, n01)
            denominator = mul(mul(w0, w1), w2)
            self.assertEqual(determinant, mul(20, denominator))

            inv20 = inv(20)
            l00 = mul(n00, inv20)
            l01 = mul(n01, inv20)
            l11 = mul(n11, inv20)
            u = l00 ^ l01
            v = l01
            z = l01 ^ l11
            d = mul(w2, inv(6))
            q = mul(v, inv(u))
            r_prime = mul(z, inv(d))

            w = mul(6, mul(w0, w1))
            self.assertEqual(u, mul(w, inv20))
            self.assertEqual(q, mul(mul(6, a1) ^ 10, inv(mul(6, w1))))
            self.assertEqual(mul(u, d), mul(denominator, inv20))

            c0 = rng.randrange(1 << degree)
            c1 = rng.randrange(1 << degree)
            x0 = c0
            x1 = c0 ^ c1
            x0 ^= mul(q, x1)
            x1 ^= mul(r_prime, x0)
            x1 = mul(d, x1)
            x0 = mul(u, x0)

            expected0 = mul(l00, c0) ^ mul(l01, c1)
            expected1 = mul(l01, c0) ^ mul(l11, c1)
            self.assertEqual((x0, x1), (expected0, expected1))
            checked += 1


if __name__ == "__main__":
    unittest.main()
