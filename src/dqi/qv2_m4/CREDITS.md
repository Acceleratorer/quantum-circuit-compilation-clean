# Credits

Credits of the three members of package combo-m4 (submission.zip sha256
f62a9ffe48c4c6bb4aa0cdebb7012320baf63c6e2cf2d4b8be6d56c40966d69c). Section A is copied byte for byte from team ThemBones'
public notebook; section B points to their NOTICE files; section C is the lineage of our own DQI member; section D
credits the third-party gauge used for the regenerated chemistry table.

## A. Team ThemBones, notebook "gift-from-thembones-vqcc-31-67924", section 9 (verbatim; applies to dfthcsos/ and to the generator that builds invsqrt.kmb; the modifications of this entry's invsqrt member are ours, see README.md)

## 9. Credits and licences

**invsqrt**
- **Syed Asad Ali**, public Apache-2.0 generator (Kaggle dataset `syed3000/vqcc-own-circuit-portfolio`, "Copyright 2026 Syed Asad Ali. Licensed under Apache-2.0."). Our invsqrt builder is a fork of it; the design adapts its ideas: the in-place root, quotient signs kept in freed wires, cyclic routing into the rotations. Its LICENSE and NOTICE are in `third_party__syed3000_invsqrt__*`.
- **manwithacat**, Kaggle notebook "VQCC Hedge Wizardry Notebook", tweak HW-27 ("measure-first": a wire that is only written and then measured is measured first, so the Toffolis onto it become CZ gates), and the public tool it names; our own tool applies the rewrite to our circuit.
- Prior art that overlaps our exact post-pass and angle solve, credited to be safe: the measure-out rewrite (manwithacat, HW-26), identical-Toffoli-pair deletion in boristown's public `qccscope` package, the public AND merge of jeffemerson's notebook, and the linear-programming angle re-solve in the public notebooks of asteriospanoras and hayatohikawa.

**DQI**
- **Atakan Aldemir** and the co-credited authors (Syed Asad Ali, Lera / marculera, qwertykeypadapple, manwithacat), Kaggle dataset `atakanaldemir/qcc-c44-five-helper-release-sources` (Apache-2.0, upstream notices retained): our DQI builder started from this public source bundle (its 892-qubit carry decoder, rebuilt byte for byte); everything from there to this file is our own work on it. Its LICENSE and CREDITS files are in `third_party__atakanaldemir_dqi_bundle__*`.
- The upstream lineage credited inside that bundle: **SomeJoint** (the 892-qubit decoder), **Ali Haydar Ozdag / yoyobar** (carry; cache reuses), **manwithacat** (HW06 / HW07 flag uncomputation templates), **Craig Gidney** (temporary-AND cleanup), **Busya PRIME / Ahmed Berat Ozer** (product caching).
- **James Day (jday96314)**, repository QuantumAI (github.com/jday96314/QuantumAI-archive, Apache-2.0 since 2026-11-09): the decoder design the public line descends from. Its LICENSE is in `third_party__jday96314_QuantumAI-archive__*`.
- **Syed Asad Ali**, public Apache-2.0 DQI decoder (dataset `syed3000/vqcc-own-circuit-portfolio`): our projective finish and CRT closing follow it, re-implemented in our code. Its LICENSE and NOTICE are in `third_party__syed3000_dqi__*`.
- Public mathematics behind our bilinear multiplication kernels: flip graphs (M. Kauers and J. Moosbauer, arXiv:2212.01175), flip graphs with plus transitions (Y. Arai, Y. Ichikawa and K. Hukushima, arXiv:2312.17094), Toom-Cook evaluation and interpolation.

**Chemistry**
- **Syed Asad Ali**, public Apache-2.0 chemistry plans (dataset `syed3000/vqcc-own-circuit-portfolio`): the loaders' high-cache form at 68 ANDs and the "sector closure" that meets its condition were learned from them, read as data. Their LICENSE and NOTICE are in `third_party__syed3000_dfthcsos__*`.
- **Lera / marculera**, `marculera/dfthc-compact-pipeline` (Apache-2.0): our fitting objective was first rebuilt from this public pipeline; the public loader notebooks of **Lera** and **maoxin** were read for our loader engine's early ideas.
- The hosts' **Verifiable Circuit Compilation Starter Kit**: the objective and the file format.
- Public mathematics: L. Lovasz's randomized algebraic test for linear matroid parity, used to price the loaders' product plans.

**General**
- **kickmix**, the verifiers and the competition paper (Khattar et al., arXiv:2610.23832) by Google Quantum AI. They are read from the attached competition data and are not redistributed.

Built by our team with the help of AI coding agents (the competition's Description invites them).

This notebook and our files in the dataset: Apache License 2.0 (`LICENSE`, `NOTICE`). Third-party files keep their own
LICENSE, NOTICE and CREDITS (the dataset's `third_party__*` files).

## B. ThemBones NOTICE files

NOTICE sections 4 and 5 reproduce thembones_generators/NOTICE and thembones_set/NOTICE verbatim. The upstream LICENSE,
NOTICE and CREDITS files they name are the third_party__* files in thembones_generators/ (unchanged).

## C. Our DQI member (dqi.kmb, sha256 3c03fa53dd86be8e2ea3caa5d37597d371bc49426605a57a6ae8d31adc3c2ef3)

Our compiler extends public Apache-2.0 work. Credit, from the materials chain of our packages and the source headers:
- **Syed Asad Ali**, public DQI decoder v12 source archive (Kaggle dataset syed3000/vqcc-own-circuit-portfolio,
  dataset version 12, Apache-2.0): the generator our compiler runs on and extends (dqi/repo/tools/dqi_public_syed_v12/).
  The bilinear field kernels J_A and J_B (dqi/repo/tools/dqi_pair_v12/ja_terms.py, jb_terms.py) were decoded from his
  compiled v13 DQI decoder (same dataset, Apache-2.0); original builder Syed Asad Ali. His NOTICE:
  > Copyright 2026 Syed Asad Ali. Licensed under Apache-2.0.
  > Credits: Syed Asad Ali, working with a team of AI agents (GPT-6 Astra Pro, Gemini 4 Argon, Fable 5.2, Mythos 5.2 and Opus 5.5), with Claude Science supporting the research.
- **Ertugrul Ozer**, extractor cutoff (public notebook lineage recorded in dqi/repo/tools/dqi_public_cut18/README.md).
- **areebbb**, retained-products pass `retain.py` (notebook areebbb/qai-fewer-toffolis-same-qubits-lb-27-11042,
  Apache-2.0 by that notebook's credits section), used verbatim.
- **SomeJoint**, public 892-qubit DQI kit (Apache-2.0): the 99-AND GF(2^24) product used as fallback kernel.
- **Balram Srinivasan's team**, norm-preserving GF(2^24) closing (dataset "VQCC 28.10 norm-preserving DQI closings",
  Apache-2.0): idea and reference implementation, re-implemented as our code (npclose.py).
- **Jeff Emerson**, the AND merge a.b + a.c = a.(b + c), first shown publicly for the inverse-sqrt circuit (Apache-2.0):
  the idea behind our rankmerge.py.
- **D. Bartoli, G. Zini and F. Zullo**, GF(8) multiplication terms (paper Table 1, CC BY 4.0): the start of the chain
  that produced our stored witness minorcircuit_22187.json.
- The notice shipped with our DQI compiler code (dqi/repo/tools/dqi_pair_v12/NOTICE), verbatim:
  > Copyright 2026 Syed Asad Ali. Licensed under Apache-2.0.
  > Credits: Syed Asad Ali, working with a team of AI agents (GPT-6 Astra Pro, Gemini 4 Argon, Fable 5.2, Mythos 5.2 and Opus 5.5), with Claude Science supporting the research.
  > 
  > Norm-preserving GF(2^24) closing (npclose.py, kit v11): idea and reference implementation by Balram Srinivasan's team,
  > dataset "VQCC 28.10 norm-preserving DQI closings" (Apache-2.0), written against Syed Asad Ali's builder; re-implemented
  > in this kit as our own code (lane dqi_close).
  > 
  > Shared-control merge pass (rankmerge.py, kit v12): own code (lane dqi_rank). The rewrite a.b + a.c = a.(b + c) for
  > Toffolis into one target was first shown publicly for the inverse-sqrt circuit by Jeff Emerson (Apache-2.0).

## D. Michael Rustad (chemistry gauge, regenerated variant only)

- **Michael Rustad**, Kaggle dataset `michaelrustad/vqcc-dfthc-r10-merged-groups`, version 5 (Apache-2.0), file
  `src/gauge.py` (Gram-preserving column rotations of a factorization's weights to lower the LCU one-norm), carried
  unchanged as chem/third_party_michaelrustad/gauge.py (sha256 c29c26bd8c156fc9b68733a677c346f7f9077e97faa7d1ad27e5a17fb1c3289a)
  with the dataset's LICENSE. It turns the ThemBones release's table/asm_words.npz into the regenerated submission.npz.

## E. General
kickmix, the verifiers and the competition paper (Khattar et al., arXiv:2610.23832) are by Google Quantum AI; they are
read from the competition data and are not redistributed. Built with the help of AI coding agents.

## E. What this entry changes against the kit of the 32.22304 entry: further credits

- **Almond Labs** (Kaggle `almondlabs`), notebook "Almond Labs QCC 31.69054 | Demonstrable Advantage" (`almondlabs/almond-labs-qcc-31-69054-demonstrable-advantage`; its section 8: "This notebook and all Almond Labs circuit/compiler contributions in it are released under the Apache License 2.0"): the optimisation `LEND29` of its section 6.1 (the generator's guard-lending pass applied also on the row of the `h1c` stage that has no auxiliary carry wire, with the lent wire kept out of the later merge pool). It is the one change that our inverse-square-root recipe makes to team ThemBones' generator. Almond Labs published the compiled circuit and the description; our source patch re-implements the change in ThemBones' generator from that description, and the circuit it emits equals theirs up to CNOT gates that cancel.
- **Team ThemBones**, public Apache-2.0 generator release (`danishlynxthembones/vqcc-thembones-milestone-generators`): the mechanism of the hoisted prefix in our DQI compiler (`generators/dqi/repo/tools/dqi_pair_v12/confluent_ext.py`: `hoist_block`, `hoist_block4`, `plain_query`, `carry_erase`, `carry_rebuild`), in which the e-products of the first old heads are summed in one block on the raw node words before the chain and the first node's carried scale is measured away, follows their "hoisted-L prefix" (`thembones_generators/dqi/tools/dqi_build_patch_prefix3.py`); our form, identities and code are our own.
