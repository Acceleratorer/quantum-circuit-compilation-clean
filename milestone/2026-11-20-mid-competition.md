# 2026-11-20 mid-competition gate

## Provenance correction (2026-11-23)

The `28.14028` score below belongs to submission `58479383`, a public-circuit
blend. A later account submission, `58771243`, scored `33.17067` from a public
circuit archive. These are historical account scores, not source-owned results;
the source-owned submitted baseline remains unverified. See the
[provenance receipt](../evals/2026-11-23-submission-58771243-provenance.json).

## Target

Reach the top public leaderboard position with a source-complete portfolio.
The latest persisted full Kaggle CLI snapshot is at `2026-11-21T12:55:34Z`;
refresh the target before every submission. The dated frontier below supersedes
older score and rank figures in this historical milestone.

## 2026-11-21 live frontier

- Account submission before the provenance audit: `58479383`, score `28.14028`,
  rank `1202 / 3519`; public-circuit blend, ineligible.
- Leader: `Z³C¹oherence`, score `33.34845`; gap `5.20817`.
- Holding inverse and chemistry costs fixed, the DQI gate is `209.035e9`, or
  mean `T <= 221,529` at `Q=890`, `R=1.1912605`.
- The source-owned FMA projection is `202,075T`, leaving `19,454T` for all
  omitted work. The complete 4+66 width, phase, and cleanup schedule is still
  unproven, so this is not a candidate.
- One active path remains: prove that schedule under the 890-qubit and
  221,529-Toffoli gates. No submission is ready.
- Snapshot, CSV hash, and score calculation:
  [evaluation](../evals/2026-11-21-live-leaderboard-125534Z.json).

### 2026-11-21 branch-history width screen

Kernel version 22 erased the four branch bits from the source-owned sentinel
label state, with matching labels/rank, clean scratch, and no phase flips.
However, the measured prefix is `Q=928`, `T=6,212`, exceeding the 890-qubit
gate by 38. Close this explicit layout; the only open DQI path is a full
4+66 schedule that reuses payload wires and proves both `Q <= 890` and
`T <= 221,529`. See [exp-053](../experiments/exp-053/README.md).

## Historical frontier (2026-11-20T01:43:00Z)

- Account submission at this historical snapshot: `58479383`, public score
  `28.14028`; public-circuit blend, ineligible.
- Current public leader: `Z³C¹oherence`, `31.74002`; gap: `3.59974` points.
- Own team rank is `981 / 3414` in the latest full snapshot; the previous
  `2026-11-19T13:59:41Z` snapshot recorded rank `917 / 3384`. See [the latest
  snapshot metadata](../evals/2026-11-20-live-leaderboard-014300Z.json) and
  [CSV](../kaggle/snapshots/2026-11-20/google-verifiable-quantum-circuit-compilation-publicleaderboard-2026-11-20T01-43-00.csv).
- Current DQI cost: `347.904e9` at 890 qubits. If the other task costs stay
  fixed, DQI must reach about `242.451e9` (a `30.31%` reduction) to match the
  current leader's score. With zero failures in 102,400 shots (`R=1.1912605`),
  that means mean `T <= 256,943` at `Q=890`. Alternatively, reducing each of
  any two task costs by about `16.52%` reaches the same product target. These are
  score-equivalence estimates, not measured leader circuit costs.

## Public-circuit frontier refresh

The `manwithacat/vqcc-apache-public-circuits` manifest last updated
`2026-11-17` contains 565 circuit records (SHA-256
`69d6e2afce31be00496c81a7446adea1eff2fe8c2361523ebefca23e297aee65`). Its
best expected-cost DQI is `575b043f` at `347.162e9`, only `0.213%` below our
`347.904e9`; its zero-failure cost is `346.410e9`, but the source reports one
lost shot on six of nine salt draws. Do not submit it. The current inverse
`563d0583` remains the lowest-cost public entry in this manifest; its best
chemistry cost is `294,642,170.57` versus our `294,642,305.56`, a negligible
difference. No public component in this refresh closes the DQI-sized gap.

## Candidate decision

The published verifier receipt for the `28.23163` Ozertuu portfolio reports
all three tasks PASS. It would rank `99 / 3355` by score in the
`2026-11-19T00:12:18Z` snapshot, but is not submitted: it consists of
downloaded public circuits and we do not have our own generator for those
exact bytes. The receipts and decision are recorded in
[`evals/2026-11-18-ozertuu-282316.json`](../evals/2026-11-18-ozertuu-282316.json).

## Kaggle source sweep (2026-11-19 10:49 UTC)

- **Data:** the files endpoint lists the official verifiers and an 886 MB DQI
  sample circuit. I did not pull that large sample into the workspace.
- **Code:** the newest public portfolio listings cluster around `28.23`. The
  `Inside the iadd Circuit` listing reports no score in its title; I did not
  download or run it. The four current rank-1 members have no quantum
  competition notebook listed under their Kaggle accounts.
- **Models:** searching for `DQI` finds no model; the only nearby result is a
  DF-THC factorization negative-result model, not a decoder.
- **Discussion:** the latest technical posts report the same public `28.2x`
  frontier. The source-delivery thread still has no organizer follow-up to
  its open questions; our standing rule remains to submit only a complete,
  reproducible generator.

No newly listed public source closes the current score gap. Keep the DQI FMA
route as the active research path; do not create another public-portfolio
assembly experiment.

The top-1 target is not met at this refresh: the best completed submission is
`28.14028`, against a public leader at `31.74002`.

The `575b043f` DQI reports two clean verifier draws, but its own README reports
one lost shot on six of nine draws. Keep it as measurement evidence only; do
not submit its circuit.

The next DQI experiment needs a materially lower cost and a deterministic
generator in this repository. Verify the exact generated bytes on multiple
salts, including the known low-weight cases, before preparing a replacement.

The balanced-split FMA subtotal is `220,017T`, leaving about `36,926T` for all
unaccounted work at the refreshed target. A direct 38-point basis still needs
948 qubits, and the simple recomputation schedule costs `390,537T` before
remaining work. Continue only with a streamed/in-place schedule that proves
the 890-qubit live-state bound and includes branch and phase costs.

## GF(2^24) multiplier screen

The proposed GF(4)^12 rank-30 lead was a table-column mix-up. The cited survey
lists symmetric complexity bounds of 30 for degree 11 and 33 for degree 12;
the latter corresponds to 99 Toffolis at three Toffolis per GF(4) product,
matching the existing GF(16)^6 kernel. No rank-30 decomposition for degree 12
was found, so the 90-Toffoli implementation is closed unless an explicit
decomposition appears. Source: [Ballet et al., Table 2](https://arxiv.org/html/1906.07456#S9.SS2).

## Truncated-radius screen

The official verifier's DQI weight distribution has mean error weight 31.05
out of 35. Cutting the decoder to radius 34 would fail about 2.77% of inputs,
so the repetition factor is at least 3.79; radius 33 fails about 11.97%, above
the verifier's 1/16 limit. Even if qubits fell from 890 to the 840-qubit input
floor, radius 34 would need to cut Toffolis by over 70% just to break even.
Keep the full radius; this shortcut is not a useful score path.

## High-space decoder screen

A reversible Berlekamp–Massey design with two 35-symbol GF(2^12) state
registers would add roughly 840 qubits, taking the circuit near `Q=1730`. At
the current no-error repetition factor, matching the refreshed score target
requires mean `T <= 68.8k`, about an `81%` reduction from the current `368.7k`.
Using the current 42-Toffoli GF(2^12) product as a rough yardstick, that leaves
room for about 1,637 such products before all other reversible work. A
straightforward 70-round BM schedule has up to 1,225 discrepancy-product
slots and roughly another 1,225 coefficient-update products: about 105.8k
Toffolis at 42 per product, or 83.2k even at 33 per product, before inversions,
flags, and cleanup. That schedule misses the score gate. This is not a lower
bound on BM; continue only with a concrete faster/fused schedule that fits the
68.8k budget.

The exact exp-046 packed-state screen now rejects a direct degree-4 Boolean
formula for the low-space transition: at prefix length 9, only `21 / 29`
forward outputs and `24 / 28` full-inverse outputs fit. The inverse with the
syndrome symbol retained fits `27 / 27`, but that is the high-space form. A
factored transition remains unproven; require a complete resource count before
building it.

## Submission gate

- Every submitted circuit has a reproducible generator and recorded source
  lineage.
- Official verification covers the exact archived bytes; DQI gets multiple
  salts and targeted checks for known counterexamples.
- The candidate beats `28.14028` before replacing the current submission.
- Record the completed Kaggle submission and a dated public leaderboard rank.

## 2026-11-20 FMA pivot-replay update

`exp-053` verifies that each pivot can be recomputed from its pristine sample
and prior normalized ratios with the same 2,415 variable products as the direct
suffix update. This is a pair-bank liveness lead only. The ratio sequence is
non-injective in the exhaustive GF(8) screen (maximum fiber 8), and the valid
70-symbol sample screen saw up to 69 zero ratios at weight 1. A reversible
branch/phase label and final basis-generation schedule remain open; no full
circuit or submission is ready.

The same screen caught and fixed an output-order bug in the swap branch of the
compiled pair cell. Allocating its ratio register after the inverse output is
freed reuses those wires: the cell now matches the classical recurrence at
`Q=871, T=300`, with 22 clean scratch qubits and zero phase flips across 32
sampled pivots. The exact branch/rank gate now projects at `Q=863`; its general
cell is `Q=55, T=83`, and the rank-sum specialization is `Q=47, T=69` per step.
The latter passed 19,880 valid rank/zero-class cases, while the general branch
cell passed 262,144 rank/zero-class cases; both had clean scratch and no phase
flips. The earlier projection was `201,375T`, leaving `55,568T`. The later
rank-invariant comparator raises the branch/rank cell from `4,830T` to
`5,530T`, revising the projection to `202,075T` with `54,868T` before the
still-unbuilt width, phase, and cleanup schedule.

The updated GF(8) screen found that ratio plus full branch history uniquely
labels all 4,096 four-sample inputs. A rank-comparison default still needs up to
69 exception bits in the sampled GF(2^12) weight-one case, so it does not
resolve the 50-qubit history/workspace limit. Across 16 samples per weight, the
screen saw 2/1/3 distinct exception masks for weights 1/31/35; the final rank
pair did not distinguish masks at weights 1 or 35. A separate screen applied
16 left bases to all 4,096 right four-sample inputs at ten rank states
(`655,360` GF(8) cases): two fixed parities `[1,2]` resolve every observed
fiber. This is not a GF(2^12) bound or a reversible decoder. Keeping two tags
for each of 17 blocks would raise the pair-cell projection from `Q=871` to
`Q=905`, 15 qubits over the limit. The blockwise tag schedule or an in-place
encoding that fits the tags into the 840-qubit payload remains unbuilt.

The focused four-point compact-state recovery screen exhausts all 4,096 GF(8)
inputs and reproduces the source samples, a valid complementary row, and branch
history. A branch-history-only round trip normalizes/factors the low row,
recovers the four samples, and replays their history; it peaks at 5,118T with at
most four factorized words (median 4,488T). The full block transform still
needs the complementary row. A crude additive screen for both paths is
11,508T, leaving 43,360T of the current 54,868T projection before other omitted
work. These are arithmetic proxies, not circuit counts; they can overlap the
FMA ledger and omit controls, live scratch, phase, and cleanup. The next gate
is a reversible encoder/decoder with measured width and Toffoli count. Its
classical four-word layout uses a four-bit shape tag, which fits the unused
rank1 bits at the four-point split and leaves one bit free; it round-trips all
GF(8) cases and 2,048 seeded GF(2^12) samples without collisions. Tag
computation and cleanup remain unbuilt.

The same GF(8) sweep finds an 11-word full four-point basis on one input.
Replacing the four source words with those coefficients projects the payload
at `Q=924`, 34 over the limit before workspace. The next schedule must stream
the basis evaluations or prove a smaller valid-domain representation.

## 2026-11-20 rank-exception transition screen

`exp-054` found 70 rank-default exception masks across all 4,095 nonzero
single-error locations at magnitude 1; each has at most two transitions. Across
50,000 samples at each of weights 31 and 35, it found 258 masks. Weight 31
reached nine transitions once; weight 35 reached four. A generic enumerative
code for that nine-transition cap needs 37 qubits, 18 above the remaining 19
after the `Q=871` pair-cell projection. A codebook for the observed masks would
fit in nine bits, but the sample does not establish a valid-domain bound or give
a reversible encoder. Close the generic transition-count encoding route; keep
the FMA work on a direct oracle or the 4+66 schedule. See
[`exp-054`](../experiments/exp-054/README.md) and the
[official-status digest](../kaggle/digests/2026-11-20-status.md).

## 2026-11-20 constant-aware four-point recovery screen

`exp-053` recounted 48 seeded GF(2^12) DQI prefixes. Charging every
multiplication 42T and inverse 138T gives mean/max 4,822.25/5,238T for
factorization, sample recovery, and branch replay after low-row formation.
Treating public-point multiplication and the monic gcd's leading `1` as linear
operations reduces this arithmetic proxy to 2,876.125/3,114T; both paths
produce the same factors, samples, ratios, and branches. This omits low-row
construction, CNOTs, circuit liveness, and the full 4+66 schedule. It is a
cost-screen refinement, not a candidate or a compiled-circuit result.

The same exhaustive GF(8) factorized-state screen finds that the direct
four-bit shape ID can be replaced by a three-color, two-bit label: 802 of the
3,200 four-word payloads are ambiguous without a tag, and the color map clears
all collisions. The map also has no collisions in the 48 seeded GF(2^12)
prefixes, but that is sample evidence only. Building the reversible color
decoder and proving its use in the full schedule remain open.

The generic packer support-pattern audit requires seven colors, or three tag
bits, when it ignores the arithmetic constraints of valid FMA states. That is
a conservative format bound; the two-bit color map only applies to the
exhaustively screened GF(8) image and the 48 GF(2^12) samples.
