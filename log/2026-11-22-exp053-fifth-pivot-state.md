# Exp-053 fifth-pivot state and inverse screen — 2026-11-22T11:00:55Z

Exhaustive enumeration covers all 32,768 five-word GF(8) inputs. The compact key (five ratios, normalized low row, and final ranks) has 46 collision groups of size two. The tag `branch[1] AND NOT branch[4]` separates all of them.

A constructive classical inverse filters histories by final ranks and tag, rebuilds each remaining basis/rank state, decodes its samples, and accepts only a history whose forward recurrence reproduces the supplied state. It recovered all 92 inputs from the GF(8) collision groups.

Filtering by final ranks and the one-bit tag leaves at most four of the 32 possible histories. There are 14 rank/tag signatures, with candidate counts `{1: 4, 2: 6, 4: 4}`. This bound follows from the five-step rank recurrence and tag alone, independent of field elements; it narrows the inverse circuit search but is not a reversible circuit result.

The same decoder recovered 32 of 32 sampled valid GF(2^12) weight-31 inputs and 32 of 32 weight-35 inputs. This is not a GF(2^12) proof or a reversible circuit.

The tag eraser, Q/T measurement, complete 4+66 schedule, and official verifier remain open. The current score-equivalence ceiling is Q=890 and mean T<=215,175.987 at R=1.1912605.

Receipt: [evals/2026-11-22-exp053-fifth-pivot-state.json](../evals/2026-11-22-exp053-fifth-pivot-state.json)
Source SHA-256: ab35474fe980fec51f8f8a82d9c8276484aa3124ad2a4c364a50c2ad80d69240
