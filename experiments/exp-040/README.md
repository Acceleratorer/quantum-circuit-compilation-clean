---
id: exp-040
title: Rishabh public rank-1 breakthrough archive audit
task: portfolio
tests: local dfthcsos verifier; static Kickmix circuit accounting
status: verified_no_improvement
result: chemistry PASS at 299654755.4367; DQI is 892 qubits / 395593 static Toffolis
---

# Rishabh public rank-1 breakthrough archive audit

The public notebook
`rishabhbafnaiiitd/quantum-circuit-compilation-rank-1-breakthrough` claims a
destructive 780-qubit DQI and a projected score of 39.14. Its downloadable
18-member archive was audited without submitting it.

| Task | Evidence | Result |
|---|---|---:|
| dfthcsos | local official verifier, 78,080 shots | PASS, cost `299,654,755.4367`, 427 qubits |
| dqi | Kickmix circuit accounting | 892 qubits, 395,593 static Toffoli-like gates |

The DQI is therefore the older baseline scale, not the claimed 780-qubit /
245k-Toffoli design, and its chemistry is worse than exp-039's
`294,878,470.7110`. It is not a submission candidate. The archive and notebook
remain outside Git; hashes are recorded in the companion evaluation JSON.

