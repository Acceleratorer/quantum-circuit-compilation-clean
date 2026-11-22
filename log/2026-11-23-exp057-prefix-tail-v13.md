# exp-057 integrated prefix and first tail action, v13

Private kernel version 13 composes compact-prefix-to-coefficient decoding with
the coefficient-derived tail action at point 4 in one circuit. It passed 32
cases covering both prefix pivots (`a0`: 31, `a1`: 1): coefficients and tail
outputs matched, the remaining 66 tail words and rank/pivot were preserved,
16 scratch qubits were clean, and there were no phase flips.

The integrated component measured `Q=889`, `T=10,084`, one qubit below the
890-qubit gate. Version 12 measured `Q=912` because its output registers were
allocated before the prefix peak. Version 13 allocates those outputs after the
prefix decoder so the builder reuses its clean scratch.

This is a 4+1 composition, not the full 4+66 schedule. The official verifier
was not run and no competition submission was made. The full schedule remains
the next gate.

Receipt: [v13 evaluation](../evals/2026-11-23-exp057-prefix-tail-v13.json).

Source SHA-256: `D5430C275F4832142AB2637F0D4D295597A739AEA4F8D699966528C9E6584E03`  
Private kernel script SHA-256: `8E6674A9142341239F5D941C9C7B0C47EAA6591EE8D8F0FB9EAB83C265D8D9BB`
