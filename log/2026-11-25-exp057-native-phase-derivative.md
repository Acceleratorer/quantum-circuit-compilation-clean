# 2026-11-25 — exp-057 native phase derivative diagnosis

## Result

The FMA pair matched the classical error locator/evaluator on all 64 cases
(32 each at weights 31 and 35). Across the 64 cases, the direct FMA numerator
produced 30 phase mismatches against the expected MBUC parity. The exact
per-root identity held in every case:

```text
omega(r) / (r * P_data(r)) = error(r) * sigma_prime(r)
```

Applying the corresponding derivative correction to the predicted parity
removed all 30 mismatches. There were no sample-node roots, padding-root
collisions, FMA-pair mismatches, zero locator derivatives, or correction
identity errors.

## Method and limits

Command:

```powershell
..\..\.venv\Scripts\python.exe -B experiments\exp-057\native_phase_derivative_diagnostic.py
```

This is a deterministic classical GF(2^12) screen with seed `0xA66062`. It
does not import or run the DQI scanner, a circuit simulator, a reversible phase
correction, the full DQI cleanup path, or the official verifier. It identifies
the mathematical factor missing from the direct native-node phase expression;
it does not show that the factor can be corrected inside the score budget.

## Decision

Do not retry the unconverted FMA scan. Continue the single exp-057 path by
deriving how the v15 streamed state can supply the required
`omega / sigma_prime` residues to the tail key-equation solve, then measure the
complete reversible schedule. The evaluation receipt is
[`2026-11-25-exp057-native-phase-derivative.json`](../evals/2026-11-25-exp057-native-phase-derivative.json).
