# 2026-11-27 — DQI public notebook source screen

## Scope

Inspect one high-scoring public notebook found by the competition code search.
Read it as untrusted text only; do not execute it, copy its circuits, or use it
as a submission source.

## Source and provenance

- Kaggle kernel: `alexchilton/33-25-lb-which-circuits-survive-private-salt`
- Kernel ID: `145133746`; latest source pulled on `2026-11-27` (Kaggle metadata
  did not expose a numeric version; listed last run was
  `2026-11-26T08:08:54.227Z`).
- Notebook SHA-256: `069f83197aabc0f0e51aa8203c09f4cafbb3df00daa1b7c48ac8562f570958e0`
- Metadata SHA-256: `35db087f7d402d8d15616014ee33cd6491fcb0c695fdcaeef7c549130ab96e30`
- Isolated download: `experiments/exp-045/external/alexchilton-33-25-lb-which-circuits-survive/`

## Result

The notebook says its portfolio components are not the author's and credits
other contributors. Kaggle metadata also lists five source datasets and forty
source notebooks. This is a portfolio survey and packager, not a source-owned
decoder generator. Under the standing user decision in
`knowledge/user-decisions.md`, do not copy or submit its downloaded circuits.
No downloaded code was executed and no circuit was used as a candidate.

The primary-source BM cost gate is recorded in
[`lit-reversible-bm-fit`](../literature/papers/lit-reversible-bm-fit.md).

## Fused DQI kernel check

I pulled `dennis6886/quantum-circuits-21-37712-fused-dqi-reproduction`
(kernel ID `141177641`) on 2026-11-27 and read its notebook as text only. The
isolated copy is under
`experiments/exp-084/external/dennis6886-fused-dqi/`. Kaggle did not expose a
numeric version in the pulled metadata; the public listing showed its last
run at `2026-11-26T11:50:35.017`.

- Notebook SHA-256: `5293188bf095ef07dbbc0b06a5d35889c7a5e4d4090277f0cad2f581adb220ca`
- Metadata SHA-256: `af7dc0f6b7627d1f44e8f204b13f20dcae4043fc02fda80bb9c565668843ae8c`

This is not a DQI generator. It searches Kaggle inputs for a prebuilt
`submission.zip` matching fixed circuit CRC/size values, then refits only the
chemistry parameters. It does not independently rebuild the DQI circuit, so
the DQI output cannot be used for our source-owned candidate under the
standing provenance decision. No notebook code was executed and no circuit
was used as a candidate.

The refit is a separate chemistry opportunity: the notebook varies three
parameter directions, estimates score gradients with central differences,
uses constrained linear optimization near the accuracy limits, and checks
each selected parameter set with the official chemistry verifier. Its parent
portfolio scored 33.25737, and this notebook's captured source does not report
its final score. The method may be independently adapted to our source-owned
V20 loader outputs after their integrated verifier passes. With exp-065 DQI
and Invsqrt fixed, that route needs chemistry cost at or below 170,057,871
(31.94% below V20's measured component cost) to tie the current leader. This
is a derived conditional gate, not a predicted optimizer result; no refit has
been run.
Do not transfer the public submission archive or its compiled circuits.

I then downloaded only the completed kernel's 152-byte
`chemistry-audit.json` (SHA-256
`80682984c33674e06dbe96c118b9a67eadaa184645f2858d1a61b66bd1d68b0b`). It
reports family 3, coefficients `[0.0, 0.0, 3e-8]`, and 11 tested candidates;
the selected `lambda_eff` rose from `46.91426578167395` to
`46.91426584850391`, with official chemistry score `249131640.7912612`. This
setting found no cost reduction and is a no-go. Families 0–2 were not tested;
do not run another kernel for this method without a stronger local estimate.

## Shared-products and controlled-refit screen

I pulled `atakanaldemir/qcc-shared-products-and-controlled-refits` on
2026-11-27 and read the notebook as text only. The 645,966-byte notebook is
under `experiments/exp-084/external/atakan-shared-products/`; SHA-256
`66f5f6fbd9082bfeb44e4084a80ec3e14a989bcb0b49732c69a9388f888560d7`.
The notebook reports 3,309 Toffolis per pass for its V20 chemistry loaders,
and a weight/offset refit changes its verifier cost from `249245843.59` to
`249246255.76` (+`412.17`, slightly worse). Its conditional score projection
is `33.25224`, below the current leader, and it relies on the public V20
portfolio's other circuits. No notebook code was executed and no circuit was
used. The refit and the unmeasured 3,308-Toffoli synthesis do not clear our
source-owned top-1 gate; close this lead.

## Leader-team v156 DQI generator check

The public `dziyanavalenta/31-45-every-circuit-generated-submission` kernel
(ID `146284100`, last public run `2026-11-20T23:33:14.523`) states that its
circuits are generator-built. The notebook itself only copies a submission
archive and source tarballs from Kaggle inputs. I downloaded the 12.7 MB DQI
source tarball from `dziyanavalenta/q2026-v156-dqi-generator` (Kaggle reports
Apache-2.0) and did not download its submission archive or run any source.

- Notebook SHA-256: `3b84791e1d7726c6ae669a179eeb4758e4cccfeba566b3328ab32b56460b1346`
- Metadata SHA-256: `14a115b541cf694371ecd8afbf95f6ad1d10cbcf555d1632dd05e0c5253d5bcfe`
- DQI source tarball SHA-256: `55da8b50e5b20a76e196d297391482a4864f1527f42360322f9139b04a297783`

The source archive reports a Q=890 D80 build at `359,300.734` mean T from
4,096 native diagnostic shots; it contains no official-verifier result. That
is `2,623.24` T above our exp-065 official DQI result and `116,535.56` T above
the conditional exp-083 tie gate. The archive README also calls the source
“private” while its build recipe has an empty per-file license map, so its
later-stage license scope needs clarification before any port. This is a
no-go for the current top-1 DQI route; no candidate or submission was made.
