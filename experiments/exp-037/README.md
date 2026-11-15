---
id: exp-037
title: Owned 897-qubit DQI generator baseline
task: dqi
tests: C-038
status: verified_no_improvement
result: source-owned build b3354f60; 897 qubits; 454477 static Toffoli-like gates
---

# Owned 897-qubit DQI generator baseline

Built `src/dqi/generate.py` from the pinned 68-file kit with Kickmix 1.0.0.
The build reproduced the upstream SHA exactly, so the source and build path are
reproducible. It is not a submission candidate: the circuit has 897 qubits and
454,477 static Toffoli-like gates, versus the retained 889-qubit member's
401,180 static count. No verifier run or Kaggle submission was made.

The generated 505 MB KMB was deleted after the receipt was recorded. Rebuild it
only when a verifier run is justified:

```powershell
python -I -B src/dqi/generate.py kaggle/staging/dqi-owned-897.kmb
```
