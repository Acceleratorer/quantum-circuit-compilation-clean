"""Experimental rank-99 GF(2^24) phase rewrite; screened and closed in exp-077."""

from __future__ import annotations

import importlib
import sys
from functools import lru_cache
from pathlib import Path


_calls = 0


def install(kit: Path) -> dict:
    """Patch both import spellings before the decoder captures phase_product24."""
    arithmetic = kit / 'exp' / 'arithmetic'
    for path in (kit, arithmetic):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)

    # kickmix has already been installed as the decoder kit's `circ` alias.
    division = importlib.import_module('division')
    packaged_division = importlib.import_module('exp.arithmetic.division')
    from field import bits
    from exp.mul99.kernels import tensor99_extension

    @lru_cache(maxsize=8)
    def terms(k):
        return tensor99_extension(k)

    def phase_product24_rank99(builder, x, y, mask, k=None):
        global _calls
        _calls += 1
        for input_mask, output_mask in terms(k):
            xi = list(bits(input_mask))
            zi = list(bits(output_mask))
            xp, zp = xi[0], zi[0]
            for i in xi[1:]:
                builder.cx(x[i], x[xp])
                builder.cx(y[i], y[xp])
            for j in zi[1:]:
                builder.cx(mask[j], mask[zp])
            builder.ccz(x[xp], y[xp], mask[zp])
            for j in reversed(zi[1:]):
                builder.cx(mask[j], mask[zp])
            for i in reversed(xi[1:]):
                builder.cx(y[i], y[xp])
                builder.cx(x[i], x[xp])

    division.phase_product24 = phase_product24_rank99
    packaged_division.phase_product24 = phase_product24_rank99
    return {'phase_product_variant': 'rank99', 'rank_terms': 99}


def stats() -> dict:
    return {'phase_product_calls': _calls, 'rank_terms': 99}
