"""Classical BM state model for the streaming-state DQI experiment.

This file is our small-field feasibility model. It does not build or run a
Kickmix circuit. The packed state omits the fixed constant coefficients C[0]
and B[0], both of which remain one in standard Berlekamp-Massey.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable


class GF2Field:
    """Polynomial-basis GF(2^degree); modulus includes its leading x^degree bit."""

    def __init__(self, degree: int, modulus: int) -> None:
        if degree < 1 or modulus.bit_length() != degree + 1:
            raise ValueError("modulus must have degree+1 bits")
        self.degree = degree
        self.modulus = modulus
        self.order = 1 << degree

    def mul(self, left: int, right: int) -> int:
        if not (0 <= left < self.order and 0 <= right < self.order):
            raise ValueError("field operands are out of range")
        out = 0
        a = left
        b = right
        while b:
            if b & 1:
                out ^= a
            b >>= 1
            a <<= 1
            if a & self.order:
                a ^= self.modulus
        return out

    @lru_cache(maxsize=None)
    def inv(self, value: int) -> int:
        if not 0 < value < self.order:
            raise ZeroDivisionError("zero has no field inverse")
        exponent = self.order - 2
        result = 1
        base = value
        while exponent:
            if exponent & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            exponent >>= 1
        return result


@dataclass(frozen=True)
class PackedBMState:
    """BM state with active polynomial coefficients and its scalar controls."""

    c_coefficients: tuple[int, ...]
    backup_coefficients: tuple[int, ...]
    linear_complexity: int
    shift: int
    last_discrepancy: int

    @property
    def c_degree(self) -> int:
        return len(self.c_coefficients)

    @property
    def backup_degree(self) -> int:
        return len(self.backup_coefficients)

    @property
    def coefficient_words(self) -> int:
        return self.c_degree + self.backup_degree

    def key(self) -> tuple[object, ...]:
        return (
            self.c_coefficients,
            self.backup_coefficients,
            self.linear_complexity,
            self.shift,
            self.last_discrepancy,
        )


def _trim(coefficients: list[int]) -> tuple[int, ...]:
    degree = max(i for i, value in enumerate(coefficients) if value)
    return tuple(coefficients[: degree + 1])


def _pack(
    c: list[int], backup: list[int], linear_complexity: int, shift: int, last_discrepancy: int
) -> PackedBMState:
    c_trimmed = _trim(c)
    backup_trimmed = _trim(backup)
    if c_trimmed[0] != 1 or backup_trimmed[0] != 1:
        raise AssertionError("standard BM keeps both constant coefficients equal to one")
    return PackedBMState(
        c_coefficients=c_trimmed[1:],
        backup_coefficients=backup_trimmed[1:],
        linear_complexity=linear_complexity,
        shift=shift,
        last_discrepancy=last_discrepancy,
    )


def bm_prefix_states(sequence: Iterable[int], field: GF2Field) -> tuple[PackedBMState, ...]:
    """Return the packed state before input and after each BM input symbol.

    This intentionally uses the original syndrome prefix to calculate each
    discrepancy. The model tests state injectivity and the coefficient-space
    bound; it does not claim that the next discrepancy can yet be computed
    from the packed state alone.
    """

    samples = tuple(sequence)
    if any(not 0 <= value < field.order for value in samples):
        raise ValueError("sequence contains an element outside the field")

    c = [0] * (len(samples) + 1)
    backup = [0] * (len(samples) + 1)
    c[0] = backup[0] = 1
    linear_complexity = 0
    shift = 1
    last_discrepancy = 1
    states = [_pack(c, backup, linear_complexity, shift, last_discrepancy)]

    for index, sample in enumerate(samples):
        discrepancy = sample
        for offset in range(1, linear_complexity + 1):
            discrepancy ^= field.mul(c[offset], samples[index - offset])

        if discrepancy == 0:
            shift += 1
        else:
            old_c = c.copy()
            factor = field.mul(discrepancy, field.inv(last_discrepancy))
            for offset in range(len(samples) + 1 - shift):
                if backup[offset]:
                    c[offset + shift] ^= field.mul(factor, backup[offset])

            if 2 * linear_complexity <= index:
                linear_complexity = index + 1 - linear_complexity
                backup = old_c
                last_discrepancy = discrepancy
                shift = 1
            else:
                shift += 1

        states.append(_pack(c, backup, linear_complexity, shift, last_discrepancy))

    return tuple(states)


def max_prefix_degree_excess(sequence: Iterable[int], field: GF2Field) -> int:
    """Maximum of deg(C)+deg(B)-processed_symbols over all prefixes."""

    states = bm_prefix_states(sequence, field)
    return max(state.coefficient_words - processed for processed, state in enumerate(states))
