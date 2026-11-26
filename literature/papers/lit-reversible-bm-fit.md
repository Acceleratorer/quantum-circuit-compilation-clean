---
id: lit-reversible-bm-fit
title: "Shared reversible Berlekamp–Massey for the DQI decoder"
year: 2026
tasks: dqi
relevance: "Exact task match and a working reversible BM architecture; published full circuit misses the current Q²T gate by about 9.2×"
read: 2026-11-27
---

# Shared reversible Berlekamp–Massey for the DQI decoder

## Source claims

Gu et al. study the same Reed–Solomon DQI instance: 70 twelve-bit syndromes over GF(2^12), 4,095 positions, and correction through weight 35. Their circuit performs 70 BM rounds. It rescales the replace branch so retain and replace share one arithmetic update, maintains `sigma_0 * delta = 1` to reconstruct the overwritten discrepancy on reverse, and stores only discrepancies from retain rounds. Distribution-measured coefficient windows and a one-entry, 19-qubit stack yield a combined measured failure rate of `1.4e-4` over 400 million draws. [Paper, §I.1](https://arxiv.org/html/2610.22367v1) [Released circuit notes](https://github.com/andigu/uncompute/blob/main/tasks/dqi-reed-solomon/circuits/discovered/README.md)

The circuit avoids a separate evaluator register by overwriting syndrome words with the evaluator polynomial, then restoring them. It computes a reciprocal derivative polynomial with a half-degree EEA, scans only the 4,024 residual mask positions, and contracts Forney recovery directly into the one required phase bit. The released notes report this complete phase breakdown: BM `141,071T`, reverse BM `86,176T`, evaluator transform and restore `15,246T` each, half-degree EEA and reverse `44,470T` each, scan `92,552T`, and monicize/unmonicize `1,583T` each. Exact released result: `442,397T`, `Q=1,837`. [Circuit notes](https://github.com/andigu/uncompute/blob/main/tasks/dqi-reed-solomon/circuits/discovered/README.md) [Certified results](https://github.com/andigu/uncompute/blob/main/tasks/dqi-reed-solomon/results.jsonl)

## Fit to this workspace

The transition sought by `exp-045` exists in a source-available construction, but it is not the direct low-degree packed-state map screened by `exp-046`: the circuit uses shared branch routing, a normalization invariant, MBU, a small history stack, and distribution-specific coefficient cutoffs. This is a concrete architecture reference for any future BM port.

It is **not** a rank-1 candidate as released. The current eligible gate is about `205,608 mean T` at `Q=890` (`evals/2026-11-26-dqi-score-equivalent-gate.json`). At the published `Q=1,837`, the circuit has `9.17×` the reference `Q²T` allowance if the current repetition factor is held fixed; its `T` also exceeds the gate before any attempt to reduce `Q`. The paper reports its own `TQ` objective, so this `Q²T` comparison is a local conditional calculation, not a claim made by the paper.

## Decision

**No-go on directly porting the released circuit for the current top-1 gate.** Keep the paper’s BM history-reconstruction invariant as the only BM implementation lead worth reopening. Reopen only after a concrete adaptation projects the *complete* locator, MBU phase, evaluator/scan, syndrome restoration, and cleanup below the current `Q²T` gate; the released complete circuit does not.

Primary sources: [Gu et al., arXiv:2610.22367v1](https://arxiv.org/html/2610.22367v1); [the authors’ released circuit and certified evaluator results](https://github.com/andigu/uncompute/tree/main/tasks/dqi-reed-solomon).
