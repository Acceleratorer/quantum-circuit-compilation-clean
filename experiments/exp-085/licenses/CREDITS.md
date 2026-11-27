# Third-party work in this submission

Every circuit in this package is produced by generator code, and no build reads a public `.kmb` or `.kmx` file.

**invsqrt.kmb** (inverse square root): the generator of team **ThemBones** (Danish Ali and team), Kaggle dataset
`danishlynxthembones/vqcc-thembones-milestone-generators` (Apache License 2.0; notice: NOTICE_generators), run end to
end. For the one digit whose data file (`m9dev.json`) was not published, Quantum 2026 uses its own phase form. That form
is derived from the generator's own census, not from any circuit. Quantum 2026 then applies an affine rewrite of the
last DIV2 carry, applies the w8 phase as S on a parity already present (dial rewrite), and refits the angles. ThemBones' builder is a fork of **Syed Asad Ali**'s inverse-square-root
generator (Kaggle dataset `syed3000/vqcc-own-circuit-portfolio`, Apache License 2.0; see
third_party__syed3000_invsqrt__NOTICE).

**dqi.kmb** (DQI decoder): the lineage starting from **Syed Asad Ali** (original builder; the DQI builder of the same
portfolio, version 12, Apache License 2.0; notice: NOTICE_v12_dqi), then Ertuğrul Özer (extractor cutoff) and Areeb
Ali (retained products), then the source bundle of Atakan Aldemir and co-credited authors (Apache-2.0) and DQI generator modules
published by team ThemBones (Apache-2.0), followed by later stages by Quantum 2026.

**dfthcsos/** (chemistry): the fifteen loaders come from the Quantum 2026 exact generator (chemistry 757/766). It runs
ThemBones' Apache-2.0 loader tools, patched for exact reproduction, on their published table data. The data are the
words `asm_words.npz` and the weights `submission.npz`, from Kaggle datasets
`danishlynxthembones/vqcc-thembones-milestone-set` and `danishlynxthembones/vqcc-thembones-milestone-generators`
(notices: NOTICE, NOTICE_generators). Further credits:

- Syed Asad Ali (chemistry plans: the 68-AND high-cache form and the sector closure).
- Lera / marculera, dfthc-compact-pipeline (Apache-2.0): the fitting objective.
- Public loader notebooks by Lera and maoxin.
- The public channel-gauge idea (Kirill Tymchishin, Alex Chilton, Agniv Banerjee / SomeJoint, Isabe11aM00re,
  James Barlow / manwithacat).

The upstream LICENSE, NOTICE and CREDITS texts are the `third_party__*` files.
