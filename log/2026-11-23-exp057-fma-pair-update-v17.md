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
pair update at one fixed `delta`. It is not the 70-symbol key-equation solve;
its `T` count is not a full-circuit projection. Next, compose the pair update
into the existing streamed FMA state, prove the complete width and gate
ledger, produce DQI output/phase, clean all workspace, and run the official
verifier. No competition submission was made.
