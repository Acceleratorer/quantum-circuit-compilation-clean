# Exp-053 fifth-pivot state and inverse screen — 2026-11-22T11:07:51Z

Exhaustive enumeration covers all 32,768 five-word GF(8) inputs. The compact key (five ratios, normalized low row, and final ranks) has 46 collision groups of size two. The tag `branch[1] AND NOT branch[4]` separates all of them.

A constructive classical inverse filters histories by final ranks and tag, rebuilds each remaining basis/rank state, decodes its samples, and accepts only a history whose forward recurrence reproduces the supplied state. It recovered all 92 inputs from the GF(8) collision groups.

Filtering by final ranks and the one-bit tag leaves at most four of the 32 possible histories. There are 14 rank/tag signatures, with candidate counts `{1: 4, 2: 6, 4: 4}`. This bound follows from the five-step rank recurrence and tag alone, independent of field elements; it narrows the inverse circuit search but is not a reversible circuit result.

For each of 64 sampled valid GF(2^12) DQI inputs, all four rank/tag candidates were decoded and forward-replayed using only ratios, final ranks, and tag. Exactly one history matched in every case. This avoids the low-row comparison on these samples, but it is not a proof for the full input domain; the replay remains classical.

The same decoder recovered 32 of 32 sampled valid GF(2^12) weight-31 inputs and 32 of 32 weight-35 inputs. This is not a GF(2^12) proof or a reversible circuit.

The tag eraser, Q/T measurement, complete 4+66 schedule, and official verifier remain open. The current score-equivalence ceiling is Q=890 and mean T<=215,175.987 at R=1.1912605.

Receipt: [evals/2026-11-22-exp053-fifth-pivot-state.json](../evals/2026-11-22-exp053-fifth-pivot-state.json)
Source SHA-256: b086d0a2fe9bbc1bb0156a8ad51081bd3f9f699652a8743b26e7ea93c5e33327
