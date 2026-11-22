# 2026-11-23 — exp-057 verifier-form screen, v16

Private Kaggle kernel v16 ran the existing integrated checksum circuit on 31
valid DQI-shaped syndrome cases at error weights 29–35, plus one synthetic
alternate-pivot case. The verifier-form cases use the official 70-syndrome to
FMA-sample linear map. Their weights were sampled uniformly from 29–35, not
from the verifier's full weight distribution. Cases were resampled until the
first-four prefix fit this cell's supported shape.

The run measured `Q=889`, `T=19,004`; all matrix, tag, and checksum checks
passed, all 66 tail words were preserved, 12 scratch qubits were clean, and
there were no phase flips. A local pure-field check reconstructed all 31
prefixes before the private run.

This confirms the existing checksum screen on valid high-weight DQI syndromes.
It still does not perform the remaining tail key-equation solve, produce the
DQI phase/output, restore the prefix/matrix state, or pass the official
verifier. The generated cases are conditioned on the supported prefix shape,
so this is not a coverage or failure-rate estimate.

Evidence: [evaluation receipt](../evals/2026-11-23-exp057-verifier-form-v16.json),
[private Kaggle kernel v16](https://www.kaggle.com/code/accelra/exp057-streaming-prefix-state/versions/16),
and the [raw kernel output](../experiments/exp-057/kaggle-v16-output.log).
