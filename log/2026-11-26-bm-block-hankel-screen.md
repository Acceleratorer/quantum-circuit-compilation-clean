# 2026-11-26 — BM block/Hankel screen

## Scope

Test one block key-equation route within exp-045: compare the known-degree
Hankel solve to standard BM on valid GF(2^12) power syndromes, and measure the
existing in-place triangular Hankel primitive at size 70. No Kaggle circuit was
built or submitted.

## Commands

```powershell
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' src/dqi/pro_q2_897/exp/convert/hankel_check.py
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' experiments/exp-045/hankel_locator_screen.py
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' tests/test_exp045_bm_state.py
& 'D:\Code\Kaggle\competitions\Google Quantum AI\.venv\Scripts\python.exe' -m kaggle competitions leaderboard google-verifiable-quantum-circuit-compilation --show --page-size 10 --format json
```

Verifier settings: GF(2^12) modulus `0x1053`; deterministic seed `20261126`;
70 power syndromes from distinct nonzero locations and magnitudes; known
degrees 1, 17, and 35. This is a classical verifier-form sample check, not an
official Kaggle verifier run. No candidate archive was produced.

Source SHA-256:

- `src/dqi/pro_q2_897/exp/convert/hankel_check.py`:
  `8dcfe45b3f18946815a821c9fde7f2f002ae99507ef1a24406485fc4c118410b`
- `experiments/exp-045/hankel_locator_screen.py`:
  `a983c98fc19a749cb3784c06cfbd032b8de041e134ac1adef277e983c96de9dd`
- `tests/test_exp045_bm_state.py`:
  `649310c99a38173b6953352e04931673e5057ff38caef4402980a78595df4eda`

## Result

- The anti-triangular H70 primitive passed one seeded direct-product and
  forward/inverse check at 363 GF(2^12) products per direction (30,492T for
  the pair at 42T/product). Its coefficient sequence is external; it is not
  the full BM key-equation matrix.
- For known degrees 1, 17, and 35, the Hankel key-equation solution matched the
  standard BM locator on deterministic verifier-form syndromes.
- Dense Gaussian elimination at degree 35 used 22,050 non-unit field
  products, or 926,100T before pivot inversions, phase, and cleanup. Its
  straightforward dense matrix occupies 1,225 GF(2^12) words.
- The current Q=900 tie gate allows 278,742.57 mean T. Close the dense solve;
  the degree-independent structured solver remains the only BM/Hankel follow-up.
- The live Kaggle CLI read at `2026-11-26T15:46:00Z` still shows `Cat with 2
  Qubits` first at `34.50408`; the score-equivalent tie gate is unchanged.
- The primary-source matrix-BM construction groups scalar terms into matrix
  sequences and returns the scalar locator from the matrix generator
  determinant, but states an overhead of `b-1` extra scalar samples. For
  `b=2`, that implies at least 71 samples at `t=35`; the decoder has 70. Close
  this documented block route for full-radius decoding. See Kaltofen,
  [“What parallel computations I do today,” PASCO 2010, §2.2](https://www.csd.uwo.ca/~mmorenom/Publications/pasco2010.pdf).
- A second proposed width reduction, deriving `shift` from processed count,
  current complexity, and actual backup degree, also failed. A valid two-error
  GF(2^12) syndrome with roots `[2, 2089]` and magnitudes `[3436, 1351]`
  begins `[1, 0, 1]`; after three symbols BM stores `shift=1`, while the
  formula predicts 2. The regression check is in
  `tests/test_exp045_bm_state.py`; the full exp-045 test file passes.

The machine-readable receipt is
[`evals/2026-11-26-bm-block-hankel-screen.json`](../evals/2026-11-26-bm-block-hankel-screen.json).
