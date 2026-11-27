---
id: claims
updated: 2026-11-27
---

# Claims ledger

One section per claim, newest at the bottom. Only research-lead edits this file.
Status changes to `supported` or `refuted` require an experiment whose critic verdict is `accepted`.

<!-- Template:
## C-NNN: <one-line statement, falsifiable>
- status: hypothesis | supported | refuted | contested
- confidence: low | medium | high
- task: invsqrt | dqi | dfthcsos | all
- expected gain: <predicted score or cost change, e.g. "invsqrt cost -15%">
- sources: <lit-..., kg-..., exp-...>
- tests: <exp-NNN (verdict)>
- history: <YYYY-MM-DD status change and why>
-->

## C-001: A width-preserving BM history-recovery adaptation can clear the DQI tie gate
- status: hypothesis
- confidence: low
- task: dqi
- expected gain: reduce mean Toffoli from 356,677.49 to at most 273,588.12 at Q<=890 (23.30%, a 2% buffer under the current tie gate); conditional portfolio projection is 34.737, about 0.233 above the current leader
- sources: lit-reversible-bm-fit, exp-063, evals/2026-11-27-exp085-v20-portfolio.json, evals/2026-11-26-dqi-stage-profile.json
- tests: none
- history: 2026-11-27 created from the shared reversible BM history-reconstruction invariant; full published circuit is a no-go and this adaptation remains untested
