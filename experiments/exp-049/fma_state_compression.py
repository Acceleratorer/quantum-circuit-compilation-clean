"""Exhaustively screen information loss in a direct FMA split update.

For small GF(2^m), run the paper's sequential modular approach on the left
block, apply its basis matrix to each pristine right input (g=1), and count
collisions in the resulting right (d,g) state. This only tests whether the
right state alone can replace the original input; it is not a lower bound on
other reversible schedules or on measurement-based uncomputation.
"""

from functools import lru_cache
from itertools import combinations, product
from math import ceil, log2
from random import Random

import numpy as np


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
    rank_terms = []
    w, n = basis[row]
    if w != [0]:
        rank_terms.append(2 * (len(w) - 1))
    if n != [0]:
        rank_terms.append(1 + 2 * (len(n) - 1))
    return max(rank_terms, default=0)


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


def verify_70_valid_error_patterns():
    """Check FMA locators for fixed-weight verifier syndromes at n=70."""
    degree, modulus = 12, 0x1053
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    points = list(range(70))
    rng = Random(0xD00470)
    results = []

    for weight in (1, 31, 35):
        betas = rng.sample(range(1, 1 << degree), weight)
        values = [rng.randrange(1, 1 << degree) for _ in betas]
        syndrome = [0] * len(points)
        for beta, error_value in zip(betas, values):
            power = beta
            for k in range(len(points)):
                syndrome[k] ^= mul(error_value, power)
                power = mul(power, beta)

        data = syndrome_to_fma_samples(syndrome, points, mul)
        four_point_basis = modular_basis(data[:4], points[:4], mul)
        four_point_basis_words = sum(
            len(polynomial) for row in four_point_basis for polynomial in row
        )
        assert four_point_basis_words == 11
        results.append(
            {
                "field": "GF(2^12)",
                "n": 70,
                "error_weight": weight,
                "split": "4+66",
                "full_left_basis_words": four_point_basis_words,
                "full_basis_plus_right_qubits": 12 * (66 + four_point_basis_words),
                "scope": "sampled full-matrix width; excludes all reversible scratch",
            }
        )
        expected_locator = [1]
        for beta in betas:
            expected_locator = poly_mul(expected_locator, [beta, 1], mul)
        node_polynomial = [1]
        for point in points:
            node_polynomial = poly_mul(node_polynomial, [point, 1], mul)
        expected_evaluator = [0]
        for beta, error_value in zip(betas, values):
            quotient = [1]
            for other_beta in betas:
                if other_beta != beta:
                    quotient = poly_mul(quotient, [other_beta, 1], mul)
            factor = mul(mul(error_value, beta), poly_eval(node_polynomial, beta, mul))
            expected_evaluator = poly_add(
                expected_evaluator,
                [mul(factor, coefficient) for coefficient in quotient],
            )

        def check_locator(basis):
            row = min(range(2), key=lambda index: row_rank(basis, index))
            locator, evaluator = (trim(poly) for poly in basis[row])
            assert locator[-1] != 0
            scale = gf_inv(locator[-1], modulus, degree)
            locator = trim([mul(scale, coefficient) for coefficient in locator])
            evaluator = trim([mul(scale, coefficient) for coefficient in evaluator])
            assert locator == expected_locator
            assert evaluator == trim(expected_evaluator)
            assert evaluator == [0] or len(evaluator) <= weight

        direct = modular_basis(data, points, mul)
        check_locator(direct)

        for stops, label in (((38, 70), "38+32"), ((64, 68, 70), "64+4+2")):
            combined = None
            start = 0
            left_basis_fields = None
            for stop in stops:
                if start == 0:
                    combined = modular_basis(data[:stop], points[:stop], mul)
                    if label == "38+32":
                        left_basis_fields = sum(
                            len(poly) for row in combined for poly in row
                        )
                else:
                    block_d, block_g = [], []
                    for sample, point in zip(data[start:stop], points[start:stop]):
                        block_d.append(
                            mul(poly_eval(combined[0][0], point, mul), sample)
                            ^ mul(poly_eval(combined[0][1], point, mul), 1)
                        )
                        block_g.append(
                            mul(poly_eval(combined[1][0], point, mul), sample)
                            ^ mul(poly_eval(combined[1][1], point, mul), 1)
                        )
                    block = modular_basis(block_d, points[start:stop], mul, block_g)
                    combined = matrix_mul(block, combined, mul)
                start = stop

            assert sorted(row_rank(combined, row) for row in range(2)) == sorted(
                row_rank(direct, row) for row in range(2)
            )
            check_locator(combined)
            results.append(
                {
                    "field": "GF(2^12)",
                    "n": 70,
                    "error_weight": weight,
                    "tree": label,
                    "locator_evaluator": "PASS",
                    "left_basis_field_coefficients": left_basis_fields,
                    "materialized_left_basis_qubits": (
                        None if left_basis_fields is None else degree * left_basis_fields
                    ),
                }
            )

    return results


def fma_block_variable_products(size):
    """Count data-dependent GF products in one power-of-two FMA block."""
    if size < 1 or size & (size - 1):
        raise ValueError("FMA block size must be a positive power of two")
    if size == 1:
        return 0
    half = size // 2
    return (
        2 * fma_block_variable_products(half)
        + 4 * half       # apply the left 2x2 basis to right-half input pairs
        + 8 * (size + 1) # multiply the two 2x2 bases at size+1 points
    )


@lru_cache(None)
def minimum_fma_product_cost(size, updated):
    """Minimize the FMA product recurrence; return (products, left_split)."""
    if size < 1:
        raise ValueError("FMA block size must be positive")
    if size == 1:
        return 0, None

    best = None
    best_split = None
    for left_size in range(1, size):
        right_size = size - left_size
        left_mode = updated
        left_cost, _ = minimum_fma_product_cost(left_size, left_mode)
        right_cost, _ = minimum_fma_product_cost(right_size, True)
        products_per_right = 4 if updated else 2
        cost = left_cost + right_cost + products_per_right * right_size + 7 * (size + 1)
        if best is None or cost < best:
            best, best_split = cost, left_size
    return best, best_split


def estimate_minimum_70_fma_products():
    """Reproduce the balanced-split product count, without claiming a space schedule."""
    products, split = minimum_fma_product_cost(70, False)
    left_products, _ = minimum_fma_product_cost(split, False)
    right_products, _ = minimum_fma_product_cost(70 - split, True)
    assert (products, split, left_products, right_products) == (4166, 38, 1961, 1644)
    scan_toffolis = 45045
    gate_limit = 259947
    return {
        "field": "GF(2^12)",
        "constraints": 70,
        "tree": f"{split}+{70 - split}",
        "variable_field_products": products,
        "basis_toffolis_at_42_per_product": products * 42,
        "scan_toffolis": scan_toffolis,
        "subtotal_toffolis": products * 42 + scan_toffolis,
        "margin_under_saved_gate": gate_limit - products * 42 - scan_toffolis,
        "scope": "count only; excludes phase extraction and has no <=50-qubit liveness proof",
    }


def estimate_70_fma_variable_products():
    """Count forward field products for the proposed 64+(4+2) FMA tree."""
    block_64 = fma_block_variable_products(64)
    block_6 = (
        fma_block_variable_products(4)
        + fma_block_variable_products(2)
        + 4 * 2
        + 8 * 7
    )
    total = block_64 + block_6 + 4 * 6 + 8 * 71
    assert (block_64, block_6, total) == (4344, 196, 5132)
    return {
        "field": "GF(2^12)",
        "constraints": 70,
        "tree": "64+(4+2)",
        "variable_field_products": total,
        "toffolis_at_42_per_product": total * 42,
        "scope": "forward FMA basis only; excludes cleanup, branch logic, scan, and phase extraction",
    }


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


@lru_cache(None)
def gf_inv(value, modulus, degree):
    if value == 0:
        raise ZeroDivisionError("zero has no field inverse")
    result = 1
    exponent = (1 << degree) - 2
    while exponent:
        if exponent & 1:
            result = gf_mul(result, value, modulus, degree)
        value = gf_mul(value, value, modulus, degree)
        exponent >>= 1
    return result


def poly_divmod(numerator, denominator, mul, modulus, degree):
    remainder = trim(list(numerator))
    denominator = trim(list(denominator))
    if denominator == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [0] * max(1, len(remainder) - len(denominator) + 1)
    inverse_lead = None
    while remainder != [0] and len(remainder) >= len(denominator):
        if inverse_lead is None:
            inverse_lead = gf_inv(denominator[-1], modulus, degree)
        shift = len(remainder) - len(denominator)
        factor = mul(remainder[-1], inverse_lead)
        quotient[shift] = factor
        for index, coefficient in enumerate(denominator):
            remainder[shift + index] ^= mul(factor, coefficient)
        trim(remainder)
    return trim(quotient), remainder


def poly_xgcd(left, right, mul, modulus, degree):
    old_r, r = trim(list(left)), trim(list(right))
    old_s, s = [1], [0]
    old_t, t = [0], [1]
    while r != [0]:
        quotient, remainder = poly_divmod(old_r, r, mul, modulus, degree)
        old_r, r = r, remainder
        old_s, s = s, poly_add(old_s, poly_mul(quotient, s, mul))
        old_t, t = t, poly_add(old_t, poly_mul(quotient, t, mul))
    if old_r == [0]:
        raise ValueError("the stored basis row cannot be zero")
    scale = gf_inv(old_r[-1], modulus, degree)
    return (
        trim([mul(value, scale) for value in old_r]),
        trim([mul(value, scale) for value in old_s]),
        trim([mul(value, scale) for value in old_t]),
    )


def _poly_divmod_monic(numerator, denominator, mul):
    remainder = trim(list(numerator))
    denominator = trim(list(denominator))
    if denominator[-1] != 1:
        raise ValueError("the divisor must be monic")
    quotient = [0] * max(1, len(remainder) - len(denominator) + 1)
    while remainder != [0] and len(remainder) >= len(denominator):
        shift = len(remainder) - len(denominator)
        factor = remainder[-1]
        quotient[shift] = factor
        for index, coefficient in enumerate(denominator[:-1]):
            remainder[shift + index] ^= mul(factor, coefficient)
        remainder[-1] = 0
        trim(remainder)
    return trim(quotient), remainder


def _reconstruct_four_point_coprime(row, points, mul, modulus, degree):
    """Closed form for a monic degree-2 / degree-1 coprime four-point row."""
    if len(points) != 4:
        return None
    w, n = (trim(list(poly)) for poly in row)
    if len(w) != 3 or len(n) != 2 or w[-1] == 0 or n[-1] == 0:
        return None
    scale = gf_inv(w[-1], modulus, degree)
    w = trim([mul(value, scale) for value in w[:-1]] + [1])
    n = trim([mul(value, scale) for value in n])

    inverse_lead = gf_inv(n[-1], modulus, degree)
    quotient = [
        mul(inverse_lead, w[1] ^ mul(inverse_lead, n[0])),
        inverse_lead,
    ]
    gcd = w[0] ^ mul(quotient[0], n[0])
    if gcd == 0:
        return None

    inverse_gcd = gf_inv(gcd, modulus, degree)
    node = [1]
    for point in points:
        node = poly_mul(node, [point, 1], mul)
    base_m = trim([mul(inverse_gcd, value) for value in node])
    base_v = poly_mul(
        [mul(inverse_gcd, coefficient) for coefficient in quotient], node, mul
    )
    quotient, v = _poly_divmod_monic(base_v, w, mul)
    m = poly_add(base_m, poly_mul(n, quotient, mul))
    if row_rank([[v, m]], 0) != 5:
        return None
    return (w, n), (v, m), []


def reconstruct_complementary_row(row, data, points, mul, modulus, degree):
    """Recover a minimum-rank row from one normalized basis row and its samples.

    The Euclidean identity gives a determinant-P solution. A correction is
    interpolated at common-zero points, then polynomial remainders choose a
    representative with the required complementary rank.
    """
    if len(data) != len(points):
        raise ValueError("data and point counts must match")
    fast = _reconstruct_four_point_coprime(row, points, mul, modulus, degree)
    if fast is not None:
        return fast
    w, n = (trim(list(poly)) for poly in row)
    pivot = w[-1] if w != [0] else n[-1]
    scale = gf_inv(pivot, modulus, degree)
    w = trim([mul(value, scale) for value in w])
    n = trim([mul(value, scale) for value in n])

    gcd, bezout_w, bezout_n = poly_xgcd(w, n, mul, modulus, degree)
    w_reduced, w_remainder = poly_divmod(w, gcd, mul, modulus, degree)
    n_reduced, n_remainder = poly_divmod(n, gcd, mul, modulus, degree)
    assert w_remainder == n_remainder == [0]

    node_polynomial = [1]
    for point in points:
        node_polynomial = poly_mul(node_polynomial, [point, 1], mul)
    quotient, remainder = poly_divmod(node_polynomial, gcd, mul, modulus, degree)
    assert remainder == [0]
    m0 = poly_mul(bezout_w, quotient, mul)
    v0 = poly_mul(bezout_n, quotient, mul)

    correction_points = []
    correction_values = []
    exceptional_samples = []
    for index, (point, value) in enumerate(zip(points, data)):
        if poly_eval(gcd, point, mul) != 0:
            continue
        denominator = mul(value, poly_eval(w_reduced, point, mul)) ^ poly_eval(
            n_reduced, point, mul
        )
        rhs = mul(value, poly_eval(v0, point, mul)) ^ poly_eval(m0, point, mul)
        if denominator:
            correction = mul(rhs, gf_inv(denominator, modulus, degree))
            exceptional_samples.append((index, value))
        else:
            assert rhs == 0
            correction = 0
        correction_points.append(point)
        correction_values.append(correction)

    correction = [0]
    for index, point in enumerate(correction_points):
        basis = [1]
        denominator = 1
        for other_index, other_point in enumerate(correction_points):
            if index == other_index:
                continue
            basis = poly_mul(basis, [other_point, 1], mul)
            denominator = mul(denominator, point ^ other_point)
        scale = mul(
            correction_values[index],
            gf_inv(denominator, modulus, degree),
        )
        correction = poly_add(correction, poly_mul(basis, [scale], mul))

    base_v = poly_add(v0, poly_mul(w_reduced, correction, mul))
    base_m = poly_add(m0, poly_mul(n_reduced, correction, mul))
    complementary_rank = 2 * len(points) + 1 - row_rank([[w, n]], 0)
    max_v_degree = complementary_rank // 2
    max_m_degree = (complementary_rank - 1) // 2

    for reduce_v, divisor, base in ((True, w, base_v), (False, n, base_m)):
        if divisor == [0]:
            continue
        quotient, remainder = poly_divmod(base, divisor, mul, modulus, degree)
        if reduce_v:
            v = remainder
            m = poly_add(base_m, poly_mul(n, quotient, mul))
        else:
            v = poly_add(base_v, poly_mul(w, quotient, mul))
            m = remainder
        if len(v) - 1 <= max_v_degree and len(m) - 1 <= max_m_degree:
            return (w, n), (v, m), exceptional_samples
    raise ValueError("Euclidean reduction did not meet the complementary rank")


def verify_complementary_row_reconstruction():
    def check(degree, modulus, points, data):
        mul = lambda a, b: gf_mul(a, b, modulus, degree)
        basis = modular_basis(data, points, mul)
        row = min(range(2), key=lambda index: row_rank(basis, index))
        low, complement, exceptions = reconstruct_complementary_row(
            basis[row], data, points, mul, modulus, degree
        )

        node = [1]
        for point in points:
            node = poly_mul(node, [point, 1], mul)
        determinant = poly_add(
            poly_mul(low[0], complement[1], mul),
            poly_mul(low[1], complement[0], mul),
        )
        assert determinant == node
        assert all(
            mul(value, poly_eval(low[0], point, mul))
            ^ poly_eval(low[1], point, mul)
            == 0
            and mul(value, poly_eval(complement[0], point, mul))
            ^ poly_eval(complement[1], point, mul)
            == 0
            for value, point in zip(data, points)
        )
        assert row_rank([low], 0) + row_rank([complement], 0) == 2 * len(points) + 1
        return len(low[0]) + len(low[1]) - 1, len(exceptions), low, complement

    def normalized_low_row(basis):
        row = min(range(2), key=lambda index: row_rank(basis, index))
        w, n = (trim(list(poly)) for poly in basis[row])
        pivot = w[-1] if w != [0] else n[-1]
        scale = gf_inv(pivot, modulus, degree)
        return (
            trim([mul(scale, value) for value in w]),
            trim([mul(scale, value) for value in n]),
        )

    results = []
    degree, modulus, points = 2, 0b111, list(range(4))
    for encoded in range(1 << (degree * len(points))):
        check(degree, modulus, points, decode_tuple(encoded, degree, len(points)))
    results.append({"field": "GF(4)", "points": 4, "inputs": 256, "reconstruction": "PASS"})

    for degree, modulus, n, count, seed in (
        (3, 0b1011, 8, 256, 0xB),
        (12, 0x1053, 38, 256, 0xC),
    ):
        rng = Random(seed)
        points = list(range(n))
        for _ in range(count):
            data = [rng.randrange(1 << degree) for _ in points]
            check(degree, modulus, points, data)
        results.append(
            {"field": f"GF(2^{degree})", "points": n, "inputs": count, "reconstruction": "PASS"}
        )

    degree, modulus = 12, 0x1053
    mul = lambda a, b: gf_mul(a, b, modulus, degree)
    points = list(range(70))
    rng = Random(0xD00470)
    for weight in (1, 31, 35):
        betas = rng.sample(range(1, 1 << degree), weight)
        values = [rng.randrange(1, 1 << degree) for _ in betas]
        syndrome = [0] * len(points)
        for beta, error_value in zip(betas, values):
            power = beta
            for index in range(len(points)):
                syndrome[index] ^= mul(error_value, power)
                power = mul(power, beta)
        data = syndrome_to_fma_samples(syndrome, points, mul)
        direct = modular_basis(data, points, mul)
        for split in (4, 8, 38):
            left_points = points[:split]
            left_data = data[:split]
            row_words, exception_count, low, complement = check(
                degree, modulus, left_points, left_data
            )

            right_d, right_g = [], []
            for sample, point in zip(data[split:], points[split:]):
                right_d.append(
                    mul(poly_eval(low[0], point, mul), sample)
                    ^ poly_eval(low[1], point, mul)
                )
                right_g.append(
                    mul(poly_eval(complement[0], point, mul), sample)
                    ^ poly_eval(complement[1], point, mul)
                )
            right = modular_basis(right_d, points[split:], mul, right_g)
            combined = matrix_mul(right, [low, complement], mul)
            assert_basis(data, [1] * len(points), points, combined, mul)
            assert sorted(row_rank(combined, row) for row in range(2)) == sorted(
                row_rank(direct, row) for row in range(2)
            )
            assert normalized_low_row(combined) == normalized_low_row(direct)

            right_words = len(points) - split
            persistent_words = row_words + exception_count + right_words
            results.append(
                {
                    "field": "GF(2^12)",
                    "errors": weight,
                    "split": f"{split}+{right_words}",
                    "normalized_left_row_words": row_words,
                    "exception_samples": exception_count,
                    "right_input_words": right_words,
                    "persistent_qubits": 12 * persistent_words,
                    "remaining_under_Q890": 890 - 12 * persistent_words,
                    "reconstruction_composition": "PASS",
                    "scope": "state count only; excludes reversible scratch and Toffolis",
                }
            )
    return results


def screen_valid_error_domain(degree, modulus, max_errors, retained_left_symbols=0):
    """Exhaust valid RS errors and measure fibers with retained left samples."""
    q = 1 << degree
    n = 2 * max_errors
    if n > q:
        raise ValueError("the small-field screen needs at least n distinct base-field points")
    if not 0 <= retained_left_symbols <= max_errors:
        raise ValueError("retained samples must fit both tested left blocks")
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
                    key = (
                        history,
                        tuple(transformed_d[split:]),
                        tuple(transformed_g[split:]),
                        tuple(data[:retained_left_symbols]),
                    )
                    counts[key] = counts.get(key, 0) + 1
                patterns += 1

    return {
        "field": f"GF(2^{degree})",
        "n": n,
        "valid_error_patterns": patterns,
        "retained_left_symbols": retained_left_symbols,
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


def screen_branch_history_vectorized(
    degree, modulus, n, split, retained_left_symbols=0, projective_pairs=False
):
    """Exhaustively screen small cases, optionally compressing right pairs projectively."""
    side_bits = degree * retained_left_symbols
    right_size = n - split
    pair_bits = degree + 1 if projective_pairs else 2 * degree
    output_bits = pair_bits * right_size + n + side_bits
    if (
        not 1 <= split < n
        or not 0 <= retained_left_symbols <= split
        or degree * n > 24
        or output_bits > 32
        or n > 1 << degree
    ):
        raise ValueError("vectorized screen is limited to at most 2^24 small-field inputs")

    q = 1 << degree
    right_size = n - split
    mul_table = np.array(
        [[gf_mul(a, b, modulus, degree) for b in range(q)] for a in range(q)],
        dtype=np.uint8,
    )
    inverse_table = np.zeros(q, dtype=np.uint8)
    if projective_pairs:
        for value in range(1, q):
            inverse_table[value] = np.flatnonzero(mul_table[value] == 1)[0]
    left_count = q**split
    right_count = q**right_size
    left_ids = np.arange(left_count, dtype=np.uint32)
    d = np.empty((split, left_count), dtype=np.uint8)
    for j in range(split):
        d[j] = (left_ids >> (degree * j)) & (q - 1)
    g = np.ones((split, left_count), dtype=np.uint8)
    rank1 = np.zeros(left_count, dtype=np.uint16)
    rank2 = np.ones(left_count, dtype=np.uint16)
    history = np.zeros(left_count, dtype=np.uint32)
    basis = [
        [
            np.ones((right_size, left_count), dtype=np.uint8),
            np.zeros((right_size, left_count), dtype=np.uint8),
        ],
        [
            np.zeros((right_size, left_count), dtype=np.uint8),
            np.ones((right_size, left_count), dtype=np.uint8),
        ],
    ]

    for j, point in enumerate(range(split)):
        dj, gj = d[j], g[j]
        swap = (gj == 0) | ((dj != 0) & (rank1 < rank2))
        history |= swap.astype(np.uint32) << j
        old_rank1, old_rank2 = rank1, rank2
        rank1 = np.where(swap, old_rank2, old_rank1)
        rank2 = np.where(swap, old_rank1 + 2, old_rank2 + 2)

        for i in range(j + 1, split):
            old_d, old_g = d[i].copy(), g[i].copy()
            d[i] = mul_table[gj, old_d] ^ mul_table[dj, old_g]
            factor = i ^ point
            g[i] = np.where(swap, mul_table[factor, old_d], mul_table[factor, old_g])

        for offset, x in enumerate(range(split, n)):
            factor = x ^ point
            a, b = basis[0][0][offset].copy(), basis[0][1][offset].copy()
            c, e = basis[1][0][offset].copy(), basis[1][1][offset].copy()
            basis[0][0][offset] = mul_table[gj, a] ^ mul_table[dj, c]
            basis[0][1][offset] = mul_table[gj, b] ^ mul_table[dj, e]
            basis[1][0][offset] = np.where(swap, mul_table[factor, a], mul_table[factor, c])
            basis[1][1][offset] = np.where(swap, mul_table[factor, b], mul_table[factor, e])

    dense_counts = retained_left_symbols == 0 and output_bits <= 27
    output_space = 1 << output_bits if dense_counts else 0
    counts = np.zeros(output_space, dtype=np.uint32) if dense_counts else None
    all_keys = np.empty(q**n, dtype=np.uint32) if not dense_counts else None
    side_mask = (1 << side_bits) - 1
    state_bits = pair_bits * right_size
    check_left = {0, left_count // 2, left_count - 1}
    check_right = {0, right_count // 2, right_count - 1}

    for right_index in range(right_count):
        right_data = decode_tuple(right_index, degree, right_size)
        right_d = np.empty((right_size, left_count), dtype=np.uint8)
        right_g = np.empty((right_size, left_count), dtype=np.uint8)
        for offset, value in enumerate(right_data):
            right_d[offset] = (
                mul_table[basis[0][0][offset], value] ^ basis[0][1][offset]
            )
            right_g[offset] = (
                mul_table[basis[1][0][offset], value] ^ basis[1][1][offset]
            )

        r1, r2, right_history = rank1.copy(), rank2.copy(), history.copy()
        for j, point in enumerate(range(split, n)):
            dj, gj = right_d[j], right_g[j]
            swap = (gj == 0) | ((dj != 0) & (r1 < r2))
            right_history |= swap.astype(np.uint32) << point
            old_rank1, old_rank2 = r1, r2
            r1 = np.where(swap, old_rank2, old_rank1)
            r2 = np.where(swap, old_rank1 + 2, old_rank2 + 2)
            for i in range(j + 1, right_size):
                old_d, old_g = right_d[i].copy(), right_g[i].copy()
                factor = (split + i) ^ point
                right_d[i] = mul_table[gj, old_d] ^ mul_table[dj, old_g]
                right_g[i] = np.where(
                    swap, mul_table[factor, old_d], mul_table[factor, old_g]
                )

        key = right_history.copy()
        if projective_pairs:
            for d_value, g_value in zip(right_d, right_g):
                projective = np.where(
                    g_value == 0,
                    q,
                    mul_table[d_value, inverse_table[g_value]],
                ).astype(np.uint32)
                key = (key << pair_bits) | projective
        else:
            for values in right_d:
                key = (key << degree) | values.astype(np.uint32)
            for values in right_g:
                key = (key << degree) | values.astype(np.uint32)
        if side_bits:
            key = (key << side_bits) | (left_ids & side_mask)
        if dense_counts:
            counts += np.bincount(key.astype(np.int64), minlength=output_space).astype(np.uint32)
        else:
            start = right_index * left_count
            all_keys[start : start + left_count] = key

        if right_index in check_right:
            for left_index in check_left:
                data = decode_tuple(left_index, degree, split) + right_data
                ref_d, ref_g, ref_history = sequential_state(
                    data, list(range(n)), lambda a, b: gf_mul(a, b, modulus, degree)
                )
                state = 0
                if projective_pairs:
                    for d_value, g_value in zip(ref_d[split:], ref_g[split:]):
                        value = (
                            q
                            if g_value == 0
                            else gf_mul(d_value, int(inverse_table[g_value]), modulus, degree)
                        )
                        state = (state << pair_bits) | value
                else:
                    for value in ref_d[split:] + ref_g[split:]:
                        state = (state << degree) | value
                expected = (ref_history << state_bits) | state
                assert int(key[left_index] >> side_bits) == expected
                assert (int(key[left_index]) & side_mask) == (int(left_ids[left_index]) & side_mask)

    if dense_counts:
        assert int(counts.sum()) == q**n
        max_fiber = int(counts.max())
    else:
        _, fibers = np.unique(all_keys, return_counts=True)
        assert int(fibers.sum()) == q**n
        max_fiber = int(fibers.max())
    return {
        "field": f"GF(2^{degree})",
        "n": n,
        "split": f"{split}+{right_size}",
        "domain_size": q**n,
        "mean_fiber": q**n / (1 << output_bits),
        "max_preimage_with_history": max_fiber,
        "extra_side_information_bits": (max_fiber - 1).bit_length(),
        "retained_left_symbols": retained_left_symbols,
        "right_state_encoding": "projective" if projective_pairs else "raw pair",
        "reference_samples": "PASS",
    }


def main():
    verify_70_symbol_splits()
    for result in verify_70_valid_error_patterns():
        print(result)
    for result in verify_complementary_row_reconstruction():
        print(result)
    print(estimate_70_fma_variable_products())
    print(estimate_minimum_70_fma_products())
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
    for case in [(3, 0b1011, 8, 6), (3, 0b1011, 8, 7)]:
        print(screen_branch_history_vectorized(*case))
    for case in [(3, 0b1011, 8, 6, 3), (3, 0b1011, 8, 7, 3)]:
        print(screen_branch_history_vectorized(*case))


if __name__ == "__main__":
    main()
