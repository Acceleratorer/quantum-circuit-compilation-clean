# 2026-11-25 — exp-057 tail key-equation composition

## Result

The canonical four-point FMA basis composed with all 66 streamed tail updates
matched a direct 70-symbol basis and the expected error locator/evaluator on
32 deterministic GF(2^12) cases: 16 each at error weights 31 and 35. The
screen forced errors at prefix roots 1, 2, and 3 in 11 cases (4, 4, and 3).

## Reproduction and limits

```powershell
..\..\.venv\Scripts\python.exe -B experiments\exp-057\tail_key_equation_composition.py
```

Seed: `0xA66063`; field modulus: `0x1053`. This checks classical basis
composition only. It does not construct the DQI output or corrected phase,
measure reversible gates or cleanup, or run the official verifier. Receipt:
[`2026-11-25-exp057-tail-key-equation-composition.json`](../evals/2026-11-25-exp057-tail-key-equation-composition.json).

## Next step

Keep this in the existing DQI path: derive the `omega / sigma_prime` residue
from the streamed state, then measure the complete reversible implementation.
