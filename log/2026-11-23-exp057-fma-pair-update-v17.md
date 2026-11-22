# 2026-11-23 — exp-057 sequential FMA pair update, v17

Private Kaggle kernel v17 checked one in-place sequential-FMA update for a
future `(d,g)` pair. The 32 seeded cases in each pivot branch matched the
reference update, preserved pivot inputs, left all 48 scratch qubits clean,
and produced no phase flips. The cell measured `Q=108`, `T=210` at `delta=37`.

The first implementation used 60 scratch qubits and 252 Toffoli-like gates.
The final version reuses the retained old-pair registers as XOR targets, saving
12 scratch qubits and 42 Toffoli-like gates without changing the output map.
It fits the 50-qubit scratch ceiling as a standalone component.

## Verification

- Local Kickmix 1.0.0 screen: 32 cases per branch, zero output/control errors,
  clean scratch, and zero phase flips.
- `py_compile` and `git diff --check` passed.
- Private Kaggle kernel `accelra/exp057-streaming-prefix-state`, version 17:
  `COMPLETE`.
- Commands: `python experiments/exp-057/build_private_kernel.py tmp/exp057-v17`;
  `kaggle kernels push -p tmp/exp057-v17`;
  `kaggle kernels logs accelra/exp057-streaming-prefix-state/17`.
- Source SHA-256:
  `3086CBA21976A4439AE99873B05C0A9DD15C85C22228E113BA4FF79D852DCA3B`.
- Submitted private script SHA-256:
  `74115014F1F65D2C9EA341298EE009BEB5576A0DF188D2DD925B71BCDAFC3938`.
- Raw log SHA-256:
  `ACF35CDA5059CD0FDD6B75079E12951C69CAB774A998E1D3A020E954D659134E`.
- [Kernel v17](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/17),
  [evaluation receipt](../evals/2026-11-23-exp057-fma-pair-update-v17.json),
  and [raw output](../experiments/exp-057/kaggle-v17-output.log).

## Scope and next gate

The circuit receives the selected pivot inverse as input and covers only one
pair update at one fixed `delta`. The 70-symbol FMA recurrence has 2,415 pair
updates; repeating this cell would cost `2,415 × 210T = 507,150T` before setup
or cleanup, already above the full DQI target of `212,110.59T`. This post-run
cost audit uses the leaderboard snapshot captured at `2026-11-22T23:05:56Z`.
This closes the
repeated-cell layout despite its correctness and width pass. Continue the
existing exp-057 stream toward key-equation output/phase and reversible cleanup
under the complete resource gate. The 2,415 count is from the
[exp-053 70-symbol FMA ledger](../experiments/exp-053/README.md#pivot-normalized-fma-recurrence).
No competition submission was made.
