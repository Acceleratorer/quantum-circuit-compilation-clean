# Evaluation snapshots

This directory separates local verifier estimates from Kaggle results.

## 2026-11-26 exp-077 phase-product rank screen — no-go

- The experiment built the older `pro_q2_897` source variant, not exp-074's
  active DQI generator. It measured Q=897 and 440,632.83 mean Toffolis versus
  exp-074's Q=900 and 316,131.22. The default-hash verifier run also had one
  phase error; a second seed had none. No candidate was submitted. See the
  [evaluation](2026-11-26-exp077-phase-product-rank99.json),
  [experiment](../experiments/exp-077/README.md), and
  [run log](../log/2026-11-26-exp077-phase-product-rank99.md).

## 2026-11-26 DQI source stage profile

- Exact source assembly totals `318,972` static Toffoli-like gates. The largest
  stage is `decoder_return` at `109,515`; the four D16 substitutions total only
  `850`. A follow-up safe cancellation scan found no identical CCX/CCZ pairs,
  closing the generic peephole screen. Any next candidate needs an
  algorithm-level rewrite with a credible path to `37,346` mean-T savings at
  the current exp-082 tie gate.
  This is analysis, not a candidate. See the
  [receipt](2026-11-26-dqi-stage-profile.json) and
  [log](../log/2026-11-26-dqi-stage-profile.md).

## 2026-11-26 BM score gates

- The published 440,000-Toffoli BM circuit misses the current `R × Q² × T`
  rank-1 tie gate by `6.50×`. A second screen finds that the straightforward
  packed-state layout retaining the syndrome bank already costs `1.297×` the
  tie gate before omitted work; the direct packed-state feedback is not a
  degree-5 GF(2) function at prefix 12 either. Continue only if an in-place
  block/Hankel update can reuse that bank. See the
  [evaluation](2026-11-26-bm-published-cost-gate.json) and
  [run log](../log/2026-11-26-bm-published-cost-gate.md).

## 2026-11-26 BM block/Hankel screen

- The triangular H70 primitive passes a seeded forward/inverse check at
  `30,492T` round trip, but it is not the full key-equation matrix. A
  known-degree Hankel solve matches standard BM at degrees 1, 17, and 35;
  dense Gaussian elimination at degree 35 costs at least `926,100T` before
  inversions, phase, and cleanup. Close the dense solve; only a structured,
  degree-independent in-place update remains in scope. See the
  [evaluation](2026-11-26-bm-block-hankel-screen.json),
  [exp-045 notes](../experiments/exp-045/README.md), and
  [run log](../log/2026-11-26-bm-block-hankel-screen.md).
  The published block-factor-2 matrix-BM construction needs an extra syndrome
  at degree 35, so it cannot cover the full correction radius with the current
  70-symbol input. A separate valid GF(2^12) two-error sample also disproves
  the simple shift-counter elimination formula; the packed-state width is
  still not within the syndrome bank.

## 2026-11-26 exp-053 four-to-five-pivot handoff

- Private kernel v35 measured the compact 4+1 prefix at `Q=891`, one over
  limit, despite matching labels with clean scratch and phase. Version 36
  replaced the temporary branch ancilla with parity-controlled gates; checks
  still pass but width remains `Q=891` and Toffolis rise from `4,500` to
  `4,576`. Close this continuation before integrating the remaining 65 pivots.
  See the [v35 receipt](2026-11-26-exp053-four-plus-one-handoff-v35.json),
  [v36 receipt](2026-11-26-exp053-parity-handoff-v36.json), and
  [exp-053 notes](../experiments/exp-053/README.md).

## Live leaderboard and source-owned result (`2026-11-26T17:42:19Z`)

- Kaggle CLI top-ten read: `Cat with 2 Qubits` leads at `34.50408`.
- Source-owned best is exp-082, submission `58958257`, at `33.08801`; score gap
  is `1.41607`.
- Using exp-082's component costs, the derived DQI tie gate is `278,784.97`
  mean T at `Q=900` (`285,084.99` at `Q=890`). This is a score-equivalent
  target, not the leader's measured DQI cost. See the
  [updated gate receipt](2026-11-26-dqi-score-equivalent-gate.json).

## 2026-11-26 exp-057 root-conditioned phase gate

- Private Kaggle version 23 added `573,144` simulator-counted T for a gate
  covering only 66 denominator-root positions, against a `34,837.57T`
  remaining allowance. It also reached `Q=892` against the 890 screen, left
  scratch dirty, and had one phase error. Close this route; no candidate was
  integrated or submitted. See the
  [evaluation](2026-11-26-exp057-root-conditioned-phase-gate.json),
  [experiment notes](../experiments/exp-057/README.md), and
  [run log](../log/2026-11-26-exp057-root-conditioned-phase-gate.md).

## 2026-11-26 exp-082 source-built V22 chemistry

- All official verifiers pass. The source-built loader uses 3,324 Toffolis per
  pass; local verifier GM is `33.08804494`, up `0.00167755` from exp-074.
  Kaggle submission `58958257` completed at public score `33.08801`, making it
  the best source-owned submission. The `33.17067` account score used a public
  circuit archive and is not an eligible source-owned result. See the
  [evaluation](2026-11-26-exp082-source-built-v22-chemistry.json),
  [experiment](../experiments/exp-082/README.md), and
  [run log](../log/2026-11-26-exp082-v22-chemistry.md).

## 2026-11-26 source-built V20 chemistry screen

- exp-074 rebuilt the V20 chemistry loaders from source and passed all task
  verifiers. It measured 3,325 Toffolis/pass, only three below exp-073 and 207
  above the notebook's 3,118 claim. Its local verifier GM is `33.08637` versus
  exp-073's `33.08134`. Submission `58917074` scored `33.08634`, a `0.00465`
  improvement over the previous source-owned best. This remains far below rank
  1. See the
  [evaluation](2026-11-26-exp074-source-built-v20-chemistry.json),
  [experiment](../experiments/exp-074/README.md), and
  [run log](../log/2026-11-26-exp074-v20-chemistry.md).

## 2026-11-26 source-built V19 chemistry screen

- exp-072 rebuilt from source and passed all task verifiers. Chemistry cost
  fell to `249,967,854.72` at 3,328 Toffolis/pass; the V19 notebook claims
  3,310, which this source build did not reproduce. The local verifier GM was
  `32.91482` on a DQI draw with four value errors. A same-DQI-score diagnostic
  gives `33.08134`, still below the account best `33.17067`; no submission was
  made. The full leaderboard snapshot ranks Accelra `692 / 3722`; rank 1 is
  `34.34445`. See the
  [evaluation](2026-11-26-exp072-source-built-v19-chemistry.json) and
  [experiment](../experiments/exp-072/README.md).

## 2026-11-25 chemistry loader check

- exp-070 rebuilt the V18 chemistry loaders from source and passed the
  official verifier, but its chemistry cost (`284.625M`) is 11.52% above
  exp-066 (`255.215M`). Its projected portfolio is `31.84075`, so it was not
  submitted. See [the evaluation](2026-11-25-exp070-source-chemistry.json)
  and [experiment notes](../experiments/exp-070/README.md).

## 2026-11-25 source-built portfolio hybrid

- exp-071 uses source-built KMX loaders 0–1 with the V18 source-plan loaders
  and factorization. Chemistry passed at default and salt 42. With the
  source-built exp-069 DQI and exp-066 Invsqrt, Kaggle submission `58894750`
  completed at `33.05453`, below the team's `33.17067` best. The earlier
  `33.22214` local projection was invalidated; chemistry-only calibration
  predicts `33.05491` (inference). See the
  [the evaluation](2026-11-25-exp071-source-hybrid.json) and
  [experiment notes](../experiments/exp-071/README.md).

## Provenance correction (2026-11-23)

- Submission `58771243` scored `33.17067` using a public circuit archive.
- Submission `58479383` scored `28.14028` and also used public circuits.
- Both are historical account measurements, not source-owned candidates. As
  of 2026-11-24, the source-owned exp-065 archive is complete with public score
  `28.71611`.
  This is the source-owned baseline, but it is not rank 1. See the
  [58771243 receipt](2026-11-23-submission-58771243-provenance.json) and the
  [exp-065 submission receipt](../experiments/exp-065/receipts/submission.json).

## Latest full leaderboard snapshot (`2026-11-26T00:50:28Z`)

- Accelra rank: `746 / 3740`; account best: `33.17067` from public-circuit
  submission `58771243`.
- Rank 1: `Entangled Team`, `34.34445`; gap from account best: `1.17378`.
- Source-owned best at capture: `33.08634` from submission `58917074`; the
  score-equivalent rank is `1176`, and the rank-1 gap is `1.25811`.
- The complete CSV and its digest are in
  [`kaggle/snapshots/2026-11-26/`](../kaggle/snapshots/2026-11-26/); see the
  [exp-074 evaluation](2026-11-26-exp074-source-built-v20-chemistry.json).

## Previous CLI readback (`2026-11-24T15:21:56Z`); retained full snapshot: `13:32:09Z`

- Accelra account score: `33.17067`, submission `58771243`, rank `354 / 3671`.
  This submission used public circuit binaries and is ineligible for the
  source-owned goal.
- Rank 1: `Entangled Team`, `34.25544`; gap from the source-owned score:
  `5.53933`.
- Snapshot metadata and the retained CSV are in
  [the 13:32Z receipt](2026-11-24-live-leaderboard-133209Z.json) and
  [`kaggle/snapshots/`](../kaggle/snapshots/2026-11-24/).
- Source-owned exp-065: ref `58832495`, `COMPLETE`, score `28.71611` (`5.53933` below rank 1); rank 1 remains the target.

## Previous live status (`2026-11-23T04:27:24Z`)

- Accelra account score in this snapshot: `28.14028`, submission `58479383`
  (public-circuit blend; ineligible for the source-owned goal).
- Latest leader: `Entangled Team`, `33.85279`; gap from this account entry:
  `5.71251` (not a source-owned baseline).
- Accelra account rank: `1372 / 3606 ranked teams` in the full snapshot; see
  [metadata](2026-11-23-live-leaderboard-042724Z.json) and the
  [retained CSV](../kaggle/snapshots/2026-11-23/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-23T04-27-24.csv).
- Local zero-error geometric mean: `28.1402768383` (not a leaderboard result).
- DQI-only target with other task costs fixed: `199.830e9`, or mean
  `T <= 211,775.05` at `Q=890` and `R=1.1912605`. This is score-equivalence
  math, not the leader's measured circuit cost.
- The previous source-owned FMA projection of `202,075T` is unsupported after
  the v19 bridge diagnostic. `CONVERT + scan + reverse CONVERT` measured
  `Q=879`, `T=183,837`; the canonical DQI residue-pair control passed phase,
  while the padded FMA low-rank row did not. Adding the v18 repeated pair-update
  subtotal gives `314,247T`, above the `211,775.05T` score-equivalent gate
  before omitted work. See the [v19 receipt](2026-11-23-exp057-fma-convert-scan-v19.json)
  and [reproduction screen](../experiments/exp-057/convert_bridge_screen.py).
- Exp-057's private v15 screen composes compact-prefix decoding, matrix setup,
  and 66 tail actions at `Q=889`, `T=19,004`. It outputs a checksum and does
  not establish full DQI output/phase, cleanup, or verifier pass; this is not a
  candidate. See the [v15 receipt](2026-11-23-exp057-prefix-matrix-stream-v15.json).
- Exp-057 v18 measures one normalized MBU FMA pair update at `Q=50`, `T=54`
  with 13 clean scratch qubits. Repeating it for the 2,415 pair updates gives
  `130,410T`, matching the existing `42T` product plus `12T` controlled-swap
  ledger. This component result does not create new budget; the v19 diagnostic
  shows the measured converter path cannot fit with it. Full integration,
  width, DQI output/phase, cleanup, and verifier remain open. See the
  [v18 receipt](2026-11-23-exp057-fma-pair-update-mbu-v18.json).
- The 2026-11-25 classical derivative screen explains the failed native FMA
  phase: the raw scan sees `error(r) * sigma_prime(r)`. It does not build the
  reversible `omega/sigma_prime` map; the v15 tail solve remains the single
  active path. See the [receipt](2026-11-25-exp057-native-phase-derivative.json)
  and [run log](../log/2026-11-25-exp057-native-phase-derivative.md).
- Full member hashes, verifier evidence, and submission:
  [2026-11-18 hybrid evaluation](2026-11-18-bori-frontier-hybrid.json).

Leaderboard CSVs are retained under `kaggle/snapshots/`; their hashes and the
download archive hash are recorded in metadata. The ZIP remains ignored by the
repository rules. Row count, ordering, leader, and own-team rank were checked.
Refresh the leaderboard before every submission.

## Active direction

The rank-1 gate remains unmet. exp-074 is the current source-owned best at
`33.08634`; its all-verifier-pass 3,325-Toffoli chemistry build missed the
V20 notebook's 3,118 claim. Its public score is `1.41774` below the current
leader. The verifier-approved exp-063 DQI remains the baseline, but no lower-
cost redesign currently has a full schedule under the width and phase gates:
exp-057's root-conditioned phase route and exp-053's 4+1 handoff are closed.
Do not treat a component prefix as a submission candidate.
See the
[exp-074 evaluation](2026-11-26-exp074-source-built-v20-chemistry.json),
[archive milestone](../milestone/2026-11-23-source-owned-archive.md),
[exp-071 calibration](2026-11-25-exp071-source-hybrid.json),
[exp-072 evaluation](2026-11-26-exp072-source-built-v19-chemistry.json),
[exp-062 receipt](2026-11-23-exp062-invsqrt.json),
[exp-063 receipt](2026-11-23-exp063-dqi.json),
[exp-064 receipt](2026-11-23-exp064-dfthcsos.json), and
[exp-064 run log](../log/2026-11-23-exp064-dfthcsos-source-rebuild.md).
The archive and Kaggle submission readback are recorded in
[experiments/exp-065/](../experiments/exp-065/README.md).
