# exp-057 phase-node alignment

The FMA sample sequence uses the node polynomial `P_data(x)=prod_{i=0}^{69}(x+i)`. The phase scanner had been using the separate `P_scan` from the DQI extractor. A private Kaggle gate showed that pairing the oracle-constructed FMA residue with `P_data` restores the expected phase for error weights 31 and 35. The pair and mask banks returned unchanged at Q=879, T=183,155, with 39 clean scratch qubits.

The converter-free control used 43,593 T at Q=851 but disagreed with the expected phase on one of its two cases. The passing converter path plus the measured repeated FMA update subtotal is 313,565 T, about 102,696 T above the score-equivalent 210,869 T gate at Q=890, before the remaining decoder and cleanup. This is a phase gate, not a candidate; the residue pair was built from known error locations, and the sample-node branch, full schedule, and official verifier remain open.

Receipts: [evaluation](../evals/2026-11-23-exp057-phase-node-alignment.json). Kaggle private kernel `accelra/exp057-streaming-prefix-state`, versions 19 and 20. No competition submission was made.

One local exploratory invocation imported the DQI scanner contrary to the standing Kaggle-only execution rule. Its output was not captured or used. All reported numbers above come from the private Kaggle kernel logs in the evaluation record.
