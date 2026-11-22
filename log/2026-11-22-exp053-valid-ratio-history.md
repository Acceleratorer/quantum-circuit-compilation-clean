# Exp-053 valid-ratio history screen — 2026-11-22

Ran `py -3.12 experiments/exp-053/valid_ratio_history.py` over all 97,119
valid GF(8) error patterns with weights 0–4. Its first 32 cases matched the
existing normalized recurrence.

Ratios alone produced 69,956 vectors, 10,758 collision groups, and a maximum
fiber of 42. The smallest fixed branch-history projection that separates all
ratio fibers has six bits at positions 2–7. Adding final rank reduces this to
four bits; nine four-position sets work. The rank-assisted screen has 85,445
keys, 7,306 collision groups, and a maximum fiber of 10.

This is a small-field information screen only. It gives no GF(2^12) bound,
reversible decoder, full 4+66 schedule, or official-verifier result. No Kaggle
kernel was pushed and no competition submission was made.

- Evaluation: [2026-11-22-exp053-valid-ratio-history.json](../evals/2026-11-22-exp053-valid-ratio-history.json)
- Source: [valid_ratio_history.py](../experiments/exp-053/valid_ratio_history.py)
- Aggregated counts: [exp-053/results.json](../experiments/exp-053/results.json)

Decision: retain the four-bit result as a lead for valid-domain decoding, but
do not treat it as a tail compression proof. The next step stays on the single
4+66 integration lane.
