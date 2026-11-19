"""Exhaustively screen information loss in a direct FMA split update.

For small GF(2^m), run the paper's sequential modular approach on the left
block, apply its basis matrix to each pristine right input (g=1), and count
collisions in the resulting right (d,g) state. This only tests whether the
right state alone can replace the original input; it is not a lower bound on
other reversible schedules or on measurement-based uncomputation.
"""

from math import ceil, log2
from random import Random
from itertools import combinations, product


def gf_mul(a, b, modulus, degree):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & (1 << degree):
            a ^= modulus
    return out


def trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def poly_add(left, right):
    out = [0] * max(len(left), len(right))
    for i in range(len(out)):
        out[i] = (left[i] if i < len(left) else 0) ^ (right[i] if i < len(right) else 0)
    return trim(out)


def poly_mul(left, right, mul):
    out = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            out[i + j] ^= mul(a, b)
    return trim(out)


def poly_eval(poly, x, mul):
    out = 0
    for coefficient in reversed(poly):
        out = mul(out, x) ^ coefficient
    return out


def matrix_mul(left, right, mul):
    out = [[None, None], [None, None]]
    for i in range(2):
        for j in range(2):
            value = [0]
            for k in range(2):
                value = poly_add(value, poly_mul(left[i][k], right[k][j], mul))
            out[i][j] = value
    return out


def assert_basis(data, g_values, points, basis, mul):
    for value, g_value, point in zip(data, g_values, points):
        assert all(
            mul(value, poly_eval(basis[row][0], point, mul))
            ^ mul(g_value, poly_eval(basis[row][1], point, mul))
            == 0
            for row in range(2)
        )

    determinant = poly_add(
        poly_mul(basis[0][0], basis[1][1], mul),
        poly_mul(basis[0][1], basis[1][0], mul),
    )
    node = [1]
    for point in points:
        node = poly_mul(node, [point, 1], mul)
    scale = determinant[-1]
    assert scale != 0
    assert determinant == trim([mul(scale, coefficient) for coefficient in node])


def modular_basis(data, points, mul, g_values=None):
    """Algorithm 1's basis matrix over the given point block."""
    d = list(data)
    g = [1] * len(data) if g_values is None else list(g_values)
    basis = [[[1], [0]], [[0], [1]]]
    rank1, rank2 = 0, 1

    for j, point in enumerate(points):
        dj, gj = d[j], g[j]
        swap = gj == 0 or (dj != 0 and rank1 < rank2)
        x_minus_point = [point, 1]  # subtraction equals addition in characteristic 2
        zero = [0]
        step = (
            [[[gj], [dj]], [x_minus_point, zero]]
            if swap
            else [[[gj], [dj]], [zero, x_minus_point]]
        )

        old_rank1, old_rank2 = rank1, rank2
        if swap:
            rank1, rank2 = old_rank2, old_rank1 + 2
        else:
            rank2 = old_rank2 + 2

        for i in range(j + 1, len(data)):
            x = points[i]
            d0, g0 = d[i], g[i]
            d[i] = mul(poly_eval(step[0][0], x, mul), d0) ^ mul(poly_eval(step[0][1], x, mul), g0)
            g[i] = mul(poly_eval(step[1][0], x, mul), d0) ^ mul(poly_eval(step[1][1], x, mul), g0)

        basis = matrix_mul(step, basis, mul)

    assert_basis(data, g_values or [1] * len(data), points, basis, mul)
    return basis


def row_rank(basis, row):
    deg_w = len(basis[row][0]) - 1
    deg_n = len(basis[row][1]) - 1
    return max(2 * deg_w, 1 + 2 * deg_n)


def verify_70_symbol_splits():
    degree, modulus = 12, 0x1053
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    points = list(range(70))
    rng = Random(0xD004)
    data = [rng.randrange(1 << degree) for _ in points]
    g_values = [1] * len(points)
    direct = modular_basis(data, points, mul, g_values)
    direct_ranks = sorted(row_rank(direct, row) for row in range(2))

    for split in (38, 64):
        left = modular_basis(data[:split], points[:split], mul, g_values[:split])
        right_d, right_g = [], []
        for d, g, point in zip(data[split:], g_values[split:], points[split:]):
            right_d.append(mul(poly_eval(left[0][0], point, mul), d) ^ mul(poly_eval(left[0][1], point, mul), g))
            right_g.append(mul(poly_eval(left[1][0], point, mul), d) ^ mul(poly_eval(left[1][1], point, mul), g))
        right = modular_basis(right_d, points[split:], mul, right_g)
        combined = matrix_mul(right, left, mul)
        assert_basis(data, g_values, points, combined, mul)
        assert sorted(row_rank(combined, row) for row in range(2)) == direct_ranks
        print({"field": "GF(2^12)", "n": 70, "split": f"{split}+{70 - split}", "basis": "PASS"})

    blocks = ((0, 64), (64, 68), (68, 70))
    for start, stop in blocks:
        assert [points[i] ^ points[start] for i in range(start, stop)] == list(range(stop - start))

    combined = None
    start = 0
    for stop in (64, 68, 70):
        if start == 0:
            combined = modular_basis(data[:stop], points[:stop], mul, g_values[:stop])
        else:
            block_d, block_g = [], []
            for d, g, point in zip(data[start:stop], g_values[start:stop], points[start:stop]):
                block_d.append(mul(poly_eval(combined[0][0], point, mul), d) ^ mul(poly_eval(combined[0][1], point, mul), g))
                block_g.append(mul(poly_eval(combined[1][0], point, mul), d) ^ mul(poly_eval(combined[1][1], point, mul), g))
            block = modular_basis(block_d, points[start:stop], mul, block_g)
            combined = matrix_mul(block, combined, mul)
        start = stop

    assert_basis(data, g_values, points, combined, mul)
    assert sorted(row_rank(combined, row) for row in range(2)) == direct_ranks
    print({"field": "GF(2^12)", "n": 70, "blocks": "64+4+2", "affine_order": "PASS", "basis": "PASS"})


def decode_tuple(value, width, symbols):
    mask = (1 << width) - 1
    return [(value >> (width * i)) & mask for i in range(symbols)]


def screen(degree, modulus, n, split):
    q = 1 << degree
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    points = list(range(n))
    left_size, right_size = split, n - split
    left_count, right_count = q**left_size, q**right_size
    output_space = q ** (2 * right_size)
    seen = bytearray(output_space)
    matrices = []

    for left_index in range(left_count):
        left_data = decode_tuple(left_index, degree, left_size)
        matrices.append(modular_basis(left_data, points[:left_size], mul))

    unique, max_fiber = 0, 0
    for basis in matrices:
        table = []
        for offset in range(right_size):
            x = points[left_size + offset]
            entries = [poly_eval(basis[i][j], x, mul) for i in range(2) for j in range(2)]
            per_symbol = []
            for d in range(q):
                per_symbol.append((mul(entries[0], d) ^ entries[1], mul(entries[2], d) ^ entries[3]))
            table.append(per_symbol)

        for right_index in range(right_count):
            key = 0
            for i, d in enumerate(decode_tuple(right_index, degree, right_size)):
                first, second = table[i][d]
                key = (key << degree) | first
                key = (key << degree) | second
            if seen[key] == 255:
                raise OverflowError("fiber count exceeds the byte counter")
            seen[key] += 1
            if seen[key] == 1:
                unique += 1
            max_fiber = max(max_fiber, seen[key])

    domain = q**n
    return {
        "field": f"GF(2^{degree})",
        "n": n,
        "split": f"{left_size}+{right_size}",
        "domain_size": domain,
        "distinct_right_states": unique,
        "max_preimage": max_fiber,
        "minimum_side_information_bits": ceil(log2(max_fiber)),
    }


def sequential_state(data, points, mul):
    """Run the modular update and retain its branch history and right state."""
    d, g = list(data), [1] * len(data)
    rank1, rank2, history = 0, 1, 0

    for j, point in enumerate(points):
        dj, gj = d[j], g[j]
        swap = gj == 0 or (dj != 0 and rank1 < rank2)
        history |= int(swap) << j
        if swap:
            rank1, rank2 = rank2, rank1 + 2
        else:
            rank2 += 2

        for i in range(j + 1, len(data)):
            old_d, old_g = d[i], g[i]
            d[i] = mul(gj, old_d) ^ mul(dj, old_g)
            g[i] = mul(points[i] ^ point, old_d if swap else old_g)

    return d, g, history


def syndrome_to_fma_samples(syndrome, points, mul):
    """Apply the exact linear map from power syndromes to FMA samples.

    Let P(x)=prod_i (x+points[i]) and Q_i=P/(x+points[i]).  For
    S_k=sum_j e_j beta_j**(k+1), the returned sample is
    d_i=sum_k [x**k]Q_i * S_k = sum_j e_j beta_j Q_i(beta_j).
    The Q_i form a basis because Q_i(points[j]) is zero off the diagonal
    and nonzero on it.  This is the base-field map required by the DQI input.
    """
    n = len(points)
    if len(syndrome) != n:
        raise ValueError("syndrome and point counts must match")
    node_polynomial = [1]
    for point in points:
        node_polynomial = poly_mul(node_polynomial, [point, 1], mul)

    quotients = list(_quotients(node_polynomial, points, mul))
    samples = [
        _xor(mul(coefficient, value) for coefficient, value in zip(quotient, syndrome))
        for quotient in quotients
    ]
    for i, quotient in enumerate(quotients):
        for j, point in enumerate(points):
            value = poly_eval(quotient, point, mul)
            assert (value != 0) == (i == j)
    return samples


def _xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def _quotients(node_polynomial, points, mul):
    """Synthetic divisions P(x)/(x+point), coefficients in ascending order."""
    n = len(points)
    for point in points:
        quotient = [0] * n
        quotient[-1] = node_polynomial[-1]
        for k in range(n - 2, -1, -1):
            quotient[k] = node_polynomial[k + 1] ^ mul(point, quotient[k + 1])
        assert node_polynomial[0] ^ mul(point, quotient[0]) == 0
        yield quotient


def gf_inv(value, modulus, degree):
    if value == 0:
        raise ZeroDivisionError("zero has no field inverse")
    return next(
        candidate
        for candidate in range(1, 1 << degree)
        if gf_mul(value, candidate, modulus, degree) == 1
    )


def screen_valid_error_domain(degree, modulus, max_errors):
    """Exhaust valid RS error patterns through the exact syndrome map."""
    q = 1 << degree
    n = 2 * max_errors
    if n > q:
        raise ValueError("the small-field screen needs at least n distinct base-field points")
    points = list(range(n))
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    state_counts = {split: {} for split in (max_errors, max_errors + 1)}
    patterns = 0
    locator_failures = 0

    for weight in range(max_errors + 1):
        for positions in combinations(range(1, q), weight):
            for values in product(range(1, q), repeat=weight):
                syndrome = [0] * n
                for beta, error_value in zip(positions, values):
                    power = beta
                    for k in range(n):
                        syndrome[k] ^= mul(error_value, power)
                        power = mul(power, beta)

                data = syndrome_to_fma_samples(syndrome, points, mul)
                basis = modular_basis(data, points, mul)
                best = min(range(2), key=lambda row: row_rank(basis, row))
                locator, evaluator = (trim(poly) for poly in basis[best])

                expected_locator = [1]
                for beta in positions:
                    expected_locator = poly_mul(expected_locator, [beta, 1], mul)
                if not locator or locator[-1] == 0:
                    locator_failures += 1
                else:
                    scale = gf_inv(locator[-1], modulus, degree)
                    locator = trim([mul(coefficient, scale) for coefficient in locator])
                    if locator != expected_locator:
                        locator_failures += 1
                if evaluator != [0] and len(evaluator) > weight:
                    locator_failures += 1

                transformed_d, transformed_g, history = sequential_state(data, points, mul)
                for split, counts in state_counts.items():
                    key = (history, tuple(transformed_d[split:]), tuple(transformed_g[split:]))
                    counts[key] = counts.get(key, 0) + 1
                patterns += 1

    return {
        "field": f"GF(2^{degree})",
        "n": n,
        "valid_error_patterns": patterns,
        "fma_locator_failures": locator_failures,
        "split_fibers": {
            f"{split}+{n - split}": {
                "distinct_states": len(counts),
                "max_preimage": max(counts.values()),
                "extra_side_information_bits": (max(counts.values()) - 1).bit_length(),
            }
            for split, counts in state_counts.items()
        },
    }


def screen_branch_history(degree, modulus, n, split):
    """Exhaustively test branch bits plus final right pairs as a reversible state."""
    input_bits = degree * n
    output_bits = 2 * degree * (n - split) + n
    if input_bits > 20 or output_bits > 27:
        raise ValueError("branch-history screen is intentionally limited to small cases")

    q = 1 << degree
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    points = list(range(n))
    total = q**n
    counts = bytearray(1 << output_bits)
    unique, max_fiber = 0, 0

    for input_index in range(total):
        data = decode_tuple(input_index, degree, n)
        d, g, history = sequential_state(data, points, mul)
        key = history
        for value in d[split:] + g[split:]:
            key = (key << degree) | value
        if counts[key] == 255:
            raise OverflowError("fiber count exceeds the byte counter")
        counts[key] += 1
        if counts[key] == 1:
            unique += 1
        max_fiber = max(max_fiber, counts[key])

    return {
        "field": f"GF(2^{degree})",
        "n": n,
        "split": f"{split}+{n - split}",
        "domain_size": total,
        "distinct_history_and_right_states": unique,
        "max_preimage_with_history": max_fiber,
        "extra_side_information_bits": ceil(log2(max_fiber)),
    }


def main():
    verify_70_symbol_splits()
    for case in [(2, 0b111, 2), (3, 0b1011, 3)]:
        print(screen_valid_error_domain(*case))
    cases = [
        (2, 0b111, 4, 2),   # GF(4), 2+2
        (3, 0b1011, 6, 3),  # GF(8), 3+3
        (3, 0b1011, 6, 4),  # GF(8), 4+2
        (3, 0b1011, 8, 4),  # GF(8), 4+4
    ]
    for case in cases:
        print(screen(*case))
    for case in [(3, 0b1011, 6, 3), (3, 0b1011, 6, 4)]:
        print(screen_branch_history(*case))


if __name__ == "__main__":
    main()
