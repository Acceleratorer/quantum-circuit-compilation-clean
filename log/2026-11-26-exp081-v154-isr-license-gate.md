# 2026-11-26 — exp-081 v154 source gate

**Decision: no-go.** The v154 bundle labels itself `private`; its archive-level
license scope for the Quantum 2026 additions is unclear despite including
Apache-2.0 licenses for Syed and ThemBones components. I read the archive as
text only and did not execute, port, or add its source to Git.

The embedded inverse-square-root result reports 39 qubits and cost `62,993.5`,
but it is not independently reproduced and is above exp-074's source-owned
reference cost `61,696.23`. Hashes and the screen are in the
[evaluation receipt](../evals/2026-11-26-exp081-v154-isr-license-gate.json).

Continue with one source-owned DQI direction that first demonstrates a
credible path below the current `37,388.65` mean-Toffoli tie gap.
