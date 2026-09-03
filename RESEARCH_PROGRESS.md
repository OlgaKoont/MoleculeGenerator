# RESEARCH_PROGRESS

Last updated: 2026-08-20.

Canonical content remains YAML under `site/content/`. Research overlays live in `site/content/research/` and are merged at load time. Do not edit `site/dist/` HTML.

Status values: not_started | sources_identified | paper_read | code_inspected | drafted | verified | partially_verified | blocked.

| Page | Page type | Primary sources found | SI found | Repository inspected | Status | Missing information |
|---|---|---|---|---|---|---|
| `architecture:active-learning` | architecture | Settles 2009; EVOLVEpro paper+code | n/a class | via EvolvePro | verified | — |
| `architecture:autoregressive-generation` | architecture | Madani Nat. Biotechnol. 2023 PMC10400306; Nijkamp Cell Systems 2023 / arXiv 2206.13517; Shuai Cell Systems 2023 STAR; Dauparas Science 2022 | ProGen SI not page-by-page; IgLM Table S1/S2 not extracted as files | Graylab/IgLM@de819b5; salesforce/progen tip c27a419 (not full progen2/*.py audit) | verified | PALM-H3/HuDiff AR decoder methods; ProteinMPNN commit |
| `architecture:autoregressive-structure-generation` | architecture | Sabban RamaNet bioRxiv 10.1101/671552; Wu FoldingDiff Nat. Commun. 2024 (AR baseline); Gaujac arXiv 2405.15840; Qu PAR arXiv 2602.04883 | FoldingDiff SI PDF not page-by-page; Gaujac appendix A.4.1 split not extracted | none this pass (no catalog tool; Gaujac github not audited) | partially_verified | PAR/Gaujac commits; RamaNet version LSTM vs LSTM-GAN; antibody-specific AR structure evidence |
| `architecture:bayesian-optimization` | architecture | Frazier 2018 arXiv 1807.02811; Jones 1998 EGO; Romero PNAS 2013; Stanton LaMBO ICML 2022; EvolvePro@1c77697 negative control | Shahriari IEEE PDF paywall; Srinivas 2010 HTML conversion failed this pass; LaMBO repo not commit-audited | EvolvePro@1c77697 (GP without acquisition); LaMBO github not audited | verified | Khan 2022 antibody SSK BO methods; Srinivas theorem restatement from primary PDF |
| `architecture:coordinate-diffusion` | architecture | Ingraham Nature 2023 / bioRxiv 2022.12.01; Krishna Science 2024; Lin Genie ICML 2023; Ho DDPM; Song SDE | Chroma SI Appendices C–G, L not page-by-page; RFdiffusion-AA SI figures not page-by-page; BoltzGen methods unread | none this pass (Chroma gated; rf_diffusion_all_atom README only) | partially_verified | Chroma/RFdiffusion-AA commits; BoltzGen all-atom equations; Genie repo |
| `architecture:few-shot-mutation-optimization` | architecture | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `architecture:flow-matching` | architecture | Lipman ICLR 2023; Liu Rectified Flow; Wu et al. Cell Systems 2025 / bioRxiv 2024.11.07; Geffner Proteina ICLR 2025; Yim FrameFlow 2310.05297 / TMLR 2024 | FlowDesign Cell Systems SI not page-by-page; Proteina App. F–O not fully extracted; FrameFlow TMLR motif SI not page-by-page | FlowDesign GitHub exists, commit NR; proteina / frame-flow not audited | partially_verified | FlowDesign/Proteina/FrameFlow commits; Cell Systems SI; discrete interpolant vs Campbell CTMC |
| `architecture:frame-diffusion` | architecture | Watson 2023; Yim FrameDiff; Bennett 2025 | RFdiffusion/RFantibody SI not fully parsed | via RFantibody repo | verified | exact schedules per checkpoint |
| `architecture:geometric-transformers` | architecture | Jing ICLR 2021 GVP; Hsu ICML 2022 / bioRxiv 2022.04.10; Høie AntiFold 2025; Jumper 2021 IPA schematic; Wu tFold Nat. Commun. 2025 | AF2 SI IPA Algorithm 22 not copied; tFold SI not page-by-page; Hsu appendix A.3 proofs not restated | AntiFold@789d467 (stack inherited); facebookresearch/esm and TencentAI4S/tfold commits NR | partially_verified | ESM-IF1/tFold commits; tFold-Ab Evoformer depth in Nat. Commun. SI; exact tFold loss weights |
| `architecture:graph-neural-networks` | architecture | Gilmer ICML 2017; Dauparas Science 2022 HTML; Dauparas Nat. Methods 2025 HTML; Kong ICML 2023 / arXiv 2302.00203; Ingraham Nature 2023 (Chroma design GNN) | ProteinMPNN Science SI fig. S1–S4 not page-by-page; LigandMPNN SI not page-by-page; Chroma SI App. C–G NR | dauparas/ProteinMPNN, dauparas/LigandMPNN, thunlp-mt/dyMEAN commits NR this pass | partially_verified | ProteinMPNN/LigandMPNN/dyMEAN commits; Chroma design-net hyperparameters; Science SI figures |
| `architecture:invariant-models` | architecture | Jing ICLR 2021 GVP HTML; Hsu ICML 2022 / bioRxiv 2022.04.10; Bennett Nature 2025 HTML (2D FR template); Watson Nature 2023 (motif as 3D, contrast) | RFantibody Supplementary Fig. 1a not page-by-page; Villar 2010.13856 proofs unread; AF2 SI distogram/IPA not copied | facebookresearch/esm commit NR; RFantibody template featurizer not re-audited this pass (tool commit 8fe3114 listed elsewhere) | partially_verified | ESM-IF1 commit; RF template pair-feature list from SI; Weyl/Villar proofs |
| `architecture:inverse-folding` | architecture | Hsu 2022; Dauparas 2022; Høie 2025 | ESM-IF1 SI not re-attached | via AntiFold | verified | ProteinMPNN code not re-audited here |
| `architecture:joint-sequence-structure-diffusion` | architecture | Luo 2022 + FullDPM code | NeurIPS extra SI if any | diffab@c3e2966 | verified | — |
| `architecture:joint-sequence-structure-generation` | architecture | Hayes Science 2025 ESM3 HTML/PDF; Lisanza Nat. Biotechnol. 2025 HTML; Luo DiffAb; Wu FlowDesign; Kong dyMEAN; Ingraham Chroma staged | ESM3 SI A.1.5–A.2.1 / VQ codebook not copied; GFP wells besides B8/C10 n NR; PG Algorithms S1–S4 / SI Table 2 not page-by-page; AlphaProteo/BoltzGen methods unread | Biohub/esm and protein_generator commits NR; DiffAb@c3e2966 on tool page | partially_verified | ESM3/PG commits; VQ codebook size; BoltzGen/AlphaProteo equations |
| `architecture:masked-token-infilling` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:multi-objective-optimization` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:protein-language-models` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:se3-equivariant-models` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:sequence-diffusion` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:torsion-diffusion` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `architecture:zero-shot-mutation-scoring` | architecture | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `tool:abdiffuser` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:alphaproteo` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:antifold` | tool | Bioinformatics Advances 10.1093/bioadv/vbae202 + arXiv 2405.03370 | standalone SI not downloaded; methods in arXiv HTML | oxpig/AntiFold@789d467 | verified | exact training hardware |
| `tool:bindcraft` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:boltzgen` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:chroma` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:diffab` | tool | NeurIPS 2022 PDF + bioRxiv 10.1101/2022.07.10.499510 | appendix not separate file | luost26/diffab@c3e2966 | verified | train yaml λ weights if not 1 |
| `tool:dymean` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:esm-1v-efficient-evolution` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:esm-if1` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:esm3` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:evodiff` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:evolvepro` | tool | Science 10.1126/science.adr6006 + bioRxiv 10.1101/2024.07.17.604015 | Science SI not retrieved | mat10d/EvolvePro@1c77697 | verified | Science PDF paywall; SI |
| `tool:flowdesign` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:framediff` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:huabdiffusion` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:hudiff` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:humatch` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:iglm` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:ligandmpnn` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:makowski-affinity-specificity` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:palm-h3` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:progen` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:protein-generator` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:proteinmpnn` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:rfantibody` | tool | Nature 10.1038/s41586-025-09721-5 + IPD PDF | SI not page-by-page | RosettaCommons/RFantibody@8fe3114 | partially_verified | FT mixture weights; exact diffusion T from configs |
| `tool:rfdiffusion-aa` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:rfdiffusion` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:structural-evolution` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `tool:tfold` | tool | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-abdiffuser` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-alphaproteo` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-antifold` | paper | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `paper:paper-bindcraft` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-boltzgen` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-chroma` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-diffab` | paper | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `paper:paper-dymean` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-esm-1v-efficient-evolution` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-esm-if1` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-esm3` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-evodiff` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-evolvepro` | paper | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `paper:paper-flowdesign` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-framediff` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-huabdiffusion` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-hudiff` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-humatch` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-iglm` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-ligandmpnn` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-makowski-affinity-specificity` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-palm-h3` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-progen` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-protein-generator` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-proteinmpnn` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-rfantibody` | paper | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `paper:paper-rfdiffusion-aa` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-rfdiffusion` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-structural-evolution` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `paper:paper-tfold` | paper | catalog / matrix DOI | NR this pass | NR this pass | sources_identified | Full paper/SI/code not re-read |
| `task:affinity-maturation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:antibody-structure-aware-sequence-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:antigen-conditioned-antibody-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:cdr-backbone-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:cdr-sequence-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:cho-expression-engineering` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:codon-optimization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:combinatorial-mutation-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:de-novo-antibody-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:de-novo-backbone-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:de-novo-non-antibody-binder-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:de-novo-vhh-nanobody-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:developability-assessment` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:expression-prediction` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:few-shot-active-learning` | task | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `task:framework-redesign` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:full-3d-structure-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:functional-site-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:general-protein-sequence-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:humanization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:inverse-folding` | task | Hsu 2022; Dauparas 2022; Høie 2025 | ESM-IF1 SI not re-attached | via AntiFold | verified | ProteinMPNN code not re-audited here |
| `task:joint-cdr-sequence-structure-design` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:joint-sequence-structure-generation` | task | Hayes Science 2025 ESM3 HTML/PDF; Lisanza Nat. Biotechnol. 2025 HTML; Luo DiffAb; Wu FlowDesign; Kong dyMEAN; Ingraham Chroma staged | ESM3 SI A.1.5–A.2.1 / VQ codebook not copied; GFP wells besides B8/C10 n NR; PG Algorithms S1–S4 / SI Table 2 not page-by-page; AlphaProteo/BoltzGen methods unread | Biohub/esm and protein_generator commits NR; DiffAb@c3e2966 on tool page | partially_verified | ESM3/PG commits; VQ codebook size; BoltzGen/AlphaProteo equations |
| `task:manufacturability-assessment` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:ml-guided-directed-evolution` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:motif-scaffolding` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:multi-objective-optimization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:off-target-optimization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:polyspecificity-optimization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:secretion-engineering` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:single-mutation-proposal` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:specificity-optimization` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `task:target-conditioned-binder-generation` | task | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:antibody-inverse-folding` | workflow | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `workflow:antibody-sequence-infilling` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:cdr-codesign-diffab` | workflow | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `workflow:cdr-h3-sequence-palm` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:de-novo-antibody-rfantibody` | workflow | foundational method papers + class synthesis | varies | varies / none | partially_verified | tool-specific tensors often NR |
| `workflow:de-novo-backbone-then-mpnn` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:epitope-mab-tfold` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:few-shot-active-learning` | workflow | foundational method papers + class synthesis | varies | varies / none | verified | tool-specific tensors often NR |
| `workflow:fixed-backbone-inverse-folding` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:humanization-framework` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:joint-multimodal-generation` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:miniprotein-binder-bindcraft` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:sequence-first-de-novo` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:universal-all-atom-binder` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |
| `workflow:zero-shot-mutation` | workflow | catalog / matrix DOI | NR this pass | NR this pass | not_started | Full paper/SI/code not re-read |

## Inspection commits

- EvolvePro `1c77697d0c09bf6989a1562a55da99301a12e2cd`
- AntiFold `789d46786624c01eb44f177ef4c0deeeb6e77469`
- RFantibody `8fe311415754e0276d1a39c87c57e69c88927a2d`
- DiffAb `c3e2966601bf8025025ab87717b31b08fdd4834e`
- IgLM `de819b56238b5cb9c23d7a6fec4c55d7fc0395e4`
- salesforce/progen tip `c27a419c234a0997923761e1fe7daffcebf0eaf5` (LICENSE/SECURITY at tip; ProGen2 methods from paper)

## Build

```bash
cd site
python scripts/write_research.py
python scripts/validate.py
python src/build.py
python -m http.server 8000 --directory dist
```

Do not run `scripts/seed_all.py` after enrichment: it overwrites YAML tools/papers.

