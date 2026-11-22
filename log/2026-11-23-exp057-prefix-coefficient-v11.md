# exp-057 private prefix-to-coefficient gate, v11

## Change

Replaced the pivoted 2x2 prefix-to-coefficient map with a branchless matrix
factorization using the nonzero pivot `u=6*a0*(a0+a1+1)/20`. Reused clean
scratch fields for inverse and phase cleanup to stay below the 890-qubit gate.

The matrix screen uses `N/20` with
`N00=6*a0^2+12*a0`, `N01=a0*(6*a1+10)`, and
`N11=6*a0+6*a1^2+10*a1+12`. The factorization and determinant passed 256
seeded local GF(2^12) cases. The regression is
`tests/test_exp057_tail_map_factorization.py`.

## Local and private-kernel result

The full local private-gate screen completed with no errors. Kaggle private
kernel version 11 completed at `Q=888`, `T=9,262`. It reconstructed all four
coefficients for 32 cases across both pivots, preserved the rank/pivot and 66
spectator words, left 39 scratch qubits clean, and reported zero phase flips.
The coefficient-to-prefix and tail component screens also passed.

Regression command:

```text
python -m unittest tests.test_exp057_tail_map_factorization tests.test_exp057_tail_transition -v
```

## Scope

This is a component gate only. It does not compile the integrated 4+66
schedule or run the official DQI verifier. No competition submission was
made. The private run receipt is
[`2026-11-23-exp057-prefix-coefficient-v11.json`](../evals/2026-11-23-exp057-prefix-coefficient-v11.json).

Source SHA-256: `921BE6DC62A39E4F14CF2818DBE78C7811A0975EC7F33F174CCF84ED18A5F197`  
Private kernel script SHA-256: `3882D3DA43B7A59D5476088BCC2AF4EAAB56384DE2137CA66CCD290CA0CCDE9B`
