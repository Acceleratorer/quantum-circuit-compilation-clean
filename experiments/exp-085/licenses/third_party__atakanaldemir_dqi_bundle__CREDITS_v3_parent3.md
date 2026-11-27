# Product-chain compiler on our repaired source pipeline

Busya PRIME (Akmal Xodarev), V16/run364775339: repeated-product caching,
empty-wire scheduling and measurement-based flag cleanup; Apache2 notebook.
https://www.kaggle.com/code/busyaprime/lb-23-91003-exact-dqi-rewrites-at-892-qubits
Ahmed Berat Ozer's earlier product-caching idea, manwithacat HW07 and Craig
Gidney temporary-AND phase repayment remain credited. Our implementation
uses exact affine vectors over opaque products; hashes nominate only.
CSWAP is represented by c*(x XOR y), with all three CCZ control pairs.
Our addition is explicit provenance of zero-wire facts across captured
conditions; source reconstruction, sparse selected certificates and tests.
This is a derivative compiler research bank, not an independent decoder
invention or a universal DQI correctness proof. The parent source files,
per-file notices, cut12/gap3 repairs and one-clean flag bridge are preserved.

For a retained p=ab, replacing CCX/CZ uses by CX/CZ from p is exact. A
CSWAP of x,y is x^=p,y^=p for p=c*(x XOR y). It preserves x XOR y. Measuring
the cache adds m*p to the phase; conditional CZ on the certified final
operand pair adds m*p again, cancelling for each independent outcome m.
Every cache is zero in its captured condition and untouched by the original
circuit over its interval. Integer scheduling is a finite optimization of
these certificates; it is not a global circuit optimum. No native KMB or
gated Hamiltonian is an input to this bank. Unchanged inverse proofs may
be reused by exact hash explicitly; fresh-all-tasks must not be asserted.
