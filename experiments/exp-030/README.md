---
id: exp-030
title: SomeJoint chemistry and DQI candidate sweep
task: portfolio
tests: [C-033]
status: verified_no_improvement
date: 2026-11-13
---

# SomeJoint sweep

The retained `somejoint_ds_` cache was checked rather than discarded blindly. Six
chemistry payloads passed the official verifier, but the best was `309207580.14`,
far above the current Kirderf chemistry cost `296010654.33`. Seven DQI artifacts
were loaded with KickMix and their static Toffoli counts were all worse than the
current 889-qubit cutoff18 retained circuit.

Conclusion: no replacement component from this cache is suitable for the next
submission. The source and search scripts remain preserved for future work.
