"""Check a known-degree Hankel key-equation solve against standard BM."""

from __future__ import annotations

import json
import random

from bm_state_model import GF2Field, bm_prefix_states


def solve(matrix: list[list[int]], rhs: list[int], field: GF2Field) -> tuple[list[int], int]:
    """Return the solution and counted nonzero Gaussian-elimination products.

    Pivot inversions are deliberately excluded from the product count, making
    the reported Toffoli conversion an optimistic lower subtotal.
    """
    size = len(rhs)
    augmented = [row[:] + [value] for row, value in zip(matrix, rhs)]
    products = 0

    for column in range(size):
        pivot = next((row for row in range(column, size) if augmented[row][column]), None)
        if pivot is None:
            raise ValueError("singular Hankel matrix")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]

        scale = field.inv(augmented[column][column])
        for index in range(column + 1, size + 1):
            if augmented[column][index]:
                augmented[column][index] = field.mul(scale, augmented[column][index])
                products += 1
        augmented[column][column] = 1

        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                for index in range(column + 1, size + 1):
                    if augmented[column][index]:
                        augmented[row][index] ^= field.mul(factor, augmented[column][index])
                        products += 1
                augmented[row][column] = 0

    return [augmented[row][size] for row in range(size)], products


def verifier_syndromes(error_count: int, rng: random.Random, field: GF2Field) -> list[int]:
    roots = []
    root = 1
    for _ in range(error_count):
        roots.append(root)
        root = field.mul(root, 2)
    magnitudes = [rng.randrange(1, field.order) for _ in roots]

    powers = [1] * error_count
    syndromes = []
    for _ in range(70):
        value = 0
        for index, (root, magnitude) in enumerate(zip(roots, magnitudes)):
            powers[index] = field.mul(powers[index], root)
            value ^= field.mul(magnitude, powers[index])
        syndromes.append(value)
    return syndromes


def main() -> None:
    field = GF2Field(12, 0x1053)
    rng = random.Random(20261126)
    rows = []

    for degree in (1, 17, 35):
        syndromes = verifier_syndromes(degree, rng, field)
        matrix = [[syndromes[row + column] for column in range(degree)] for row in range(degree)]
        rhs = syndromes[degree : 2 * degree]
        reversed_locator, products = solve(matrix, rhs, field)

        bm_state = bm_prefix_states(syndromes, field)[-1]
        assert bm_state.c_degree == degree
        assert reversed_locator == list(reversed(bm_state.c_coefficients))

        rows.append(
            {
                "error_count": degree,
                "known_degree_locator_matches_bm": True,
                "gaussian_field_products_excluding_inversions": products,
                "optimistic_T_at_42_per_product": products * 42,
                "dense_matrix_field_words": degree * degree,
            }
        )

    print(json.dumps({"field": "GF(2^12), modulus 0x1053", "patterns": rows}, indent=2))


if __name__ == "__main__":
    main()
