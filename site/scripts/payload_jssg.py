from research_lib import C, F, M, P, R, S, T, U, W, ref

JSSG = R(
    "partially_verified",
    last_reviewed="2026-08-27",
    commit=None,
    inaccessible=[
        "ESM3 Science SI sections A.1.5–A.2.1 (точный codebook size structure VQ-VAE, geometric attention listing, IF-label recipe) не копируются; масштабы 1.4B/7B/98B, 216 blocks, 771B tokens, GFP wells B8/C10, FWHM 39 nm vs EGFP 56 nm — Science HTML/PDF 10.1126/science.ads0018. Число синтезированных GFP wells кроме B8/C10 — NR this pass.",
        "Biohub/esm (ESM3) commit в этом проходе не аудировался; open 1.4B vs API 7B/98B; README 8-step / T=0.7 example — [DOC], не paper hyperparameter law.",
        "ProteinGenerator Nat. Biotechnol. SI Algorithms S1–S4 / square-root schedule / SI Table 2 не постранично; CE+FAPE+bond+distogram+lDDT+KL, L×20 ±1, clamp [-3,3], wet-lab n=42/32, crystal 3.70 Å, hemolysis 15 µM, GB1 96×3 — Nature HTML 10.1038/s41587-024-02395-w. RosettaCommons/protein_generator commit NR.",
        "AlphaProteo technical report / BoltzGen methods в этом проходе не перечитывались: catalog tags only.",
        "Chroma design-net как CRF после backbone — coordinate-diffusion page; не выдавать Chroma за simultaneous joint sampler.",
    ],
    sections=[
        S(
            "1. Область определения",
            P(r"Joint sequence–structure generation — <strong>надкласс</strong> генераторов, у которых один sampling process выдаёт связанную пару \((s,x)\) (и иногда function tokens), а не два независимых этапа «сначала backbone, потом inverse folding». Это generative class, не predictor и не affinity model."),
            P(r"Не путать с задачей <a href=\"/tasks/joint-sequence-structure-generation.html\">joint sequence–structure generation</a> (что сгенерировать) и с одним subtype <a href=\"/architectures/joint-sequence-structure-diffusion.html\">joint diffusion</a> (DiffAb). Не <a href=\"/architectures/inverse-folding.html\">inverse folding</a> \(p(s\mid x)\) при фиксированном \(x\). Не staged <a href=\"/architectures/frame-diffusion.html\">frame diffusion</a> + ProteinMPNN (RFantibody). Не ELISA AL."),
            P(r"Каталог: multimodal LM <a href=\"/tools/esm3.html\">ESM3</a>; sequence-space RF diffusion <a href=\"/tools/protein-generator.html\">ProteinGenerator</a>; joint diffusion <a href=\"/tools/diffab.html\">DiffAb</a> / <a href=\"/tools/abdiffuser.html\">AbDiffuser</a> / <a href=\"/tools/boltzgen.html\">BoltzGen</a>; joint FM <a href=\"/tools/flowdesign.html\">FlowDesign</a>; iterative GNN <a href=\"/tools/dymean.html\">dyMEAN</a>. <a href=\"/tools/chroma.html\">Chroma</a> помечен этим id, но канон — coords then design GNN. <a href=\"/tools/alphaproteo.html\">AlphaProteo</a> — closed binder generator, methods NR."),
            P(r"Задачи: <a href=\"/tasks/joint-sequence-structure-generation.html\">coupled pair</a>, <a href=\"/tasks/joint-cdr-sequence-structure-design.html\">CDR co-design</a>, <a href=\"/tasks/functional-site-design.html\">function/motif prompts</a>. Не developability score и не few-shot ELISA."),
        ),
        S(
            "2. Интуитивный принцип",
            P("Если sequence и геометрию семплируют раздельно, IF может «не узнать» петлю, которую только что нарисовал diffusion, а PLM — предложить последовательность, которая не складывается в нужный fold. Joint process держит оба объекта в одном состоянии: тип аминокислоты обновляется вместе с позой, или structure tokens живут в том же Transformer, что и AA."),
            P(r"ESM3 делает это через <em>один</em> masked Transformer на трёх discrete tracks: можно задать chromophore residues + кусок центральной спирали GFP и итеративно дописать остальное (Hayes Fig. 4 «chain of thought»). ProteinGenerator шумит <em>sequence</em> one-hot и на каждом шаге RoseTTAFold предсказывает и \(s_0\), и структуру — guidance (состав, DSSP, activity classifier) входит в update \(x_{t-1}\), чего RFdiffusion на coords делает неудобно. [PAPER]"),
            P("Цена: нужен paired supervision (структуры, не только UniRef), дороже sampling, и внутренняя уверенность модели всё равно не Kd. Staged RFdiffusion+MPNN часто достаточна, если topology уже зафиксирована."),
            W(r"pTM / scTM / pLDDT / AAR / Rosetta \(\Delta G\) / model likelihood ≠ experimental \(K_D\) или fluorescence physics. esmGFP — одна функциональная кампания GFP, не antibody evidence. FlowDesign Ibalizumab BLI — на FM page, не axiom класса."),
        ),
        S(
            "3. Формальная математическая постановка",
            P("Общая цель класса — совместный закон. Факторизация tool-specific. Не записывать один DiffAb DDPM как уравнение ESM3."),
            S(
                "Joint law",
                M(
                    r"p_\theta(s,x\mid c)\qquad\text{or}\qquad p_\theta(s,x,f\mid c)",
                    caption=r"\(s\) — AA sequence; \(x\) — coords/frames или discrete structure tokens; \(f\) — function keywords (ESM3). \(c\) — partial observations любой модальности, antigen/framework, DSSP, composition. [INTERPRETATION] class; tool factorizations ниже.",
                    source="[INTERPRETATION] class definition",
                ),
                level=3,
            ),
            S(
                "Multimodal masked LM (ESM3)",
                M(
                    r"""\begin{aligned}
z&=(s,\,\tau,\,f),\qquad
\mathcal{L}=\mathbb{E}_{m}\sum_{i\in m}-\log p_\theta(z_i\mid z_{\setminus m}),\\
\text{sample: }&\text{iterative unmask until }m=\emptyset.
\end{aligned}""",
                    caption=r"Hayes: generative MLM по всем mask rates (не фиксированные 15% BERT), поэтому токены можно семплировать в любом порядке с любого partial prompt — any-order factorization, не causal AR ProGen. Tracks fused в одном latent: sequence, structure tokens, function; prompts также SS8, SASA, atomic coords. [PAPER] Fig. 1.",
                    source="[PAPER] Hayes et al. Science 2025, 10.1126/science.ads0018",
                ),
                P(r"Structure track: local atomic neighborhood каждого residue → один discrete token (VQ-VAE); decoder восстанавливает all-atom. Autoencoder loss — pairwise distances и relative orientations bond vectors/normals (SI A.1.7.3.1, listing не копируем). Reconstruction \(<0.5\) Å RMSD на CAMEO (fig. S3). Geometric attention только в первом блоке: local frames от bond geometry, interaction через transform в global frame (SI A.1.6 schematic, не AF2 IPA SI). [PAPER]"),
                P(r"Масштабы: 1.4B (open weights, non-commercial), 7B и 98B (API). Depth>width в ablations; 98B = 216 transformer blocks (SI A.1.5). Train: 3.15B sequences, 236M structures, 539M function annotations, 771B unique tokens; 98B compute \(1.07\times 10^{24}\) FLOPs. Predicted structures получают IF labels (SI A.2.1.3). [PAPER]"),
                P(r"Alignment (Fig. 3): preference pairs из prompted generations — positive = high pTM / low cRMSD vs negative; loss поднимает likelihood positives. Оценка: tertiary-contact coordinate prompts, Pass@128. После alignment 98B улучшает cRMSD и pTM; число различных решений (TM>0.8 clusters) растёт. Это не ELISA fine-tune. [PAPER]"),
                level=3,
            ),
            S(
                "Sequence-space diffusion + structure head (ProteinGenerator)",
                M(
                    r"""\begin{aligned}
x_0&=2\cdot\mathrm{OH}(s)-1\in\{-1,+1\}^{L\times 20},\\
x_t&=\sqrt{\bar\alpha_t}\,x_0+\sqrt{1-\bar\alpha_t}\,\varepsilon,\quad\varepsilon\sim\mathcal{N}(0,I),\\
\mathcal{L}&=\mathrm{CE}(\hat s,s^\star)+\lambda_{\mathrm{FAPE}}\mathrm{FAPE}+\lambda_{\mathrm{geom}}(\mathrm{bond}+\mathrm{distogram}+\mathrm{lDDT})+\mathrm{KL}(x_{t-1}).
\end{aligned}""",
                    caption=r"Lisanza Methods / Eq. 1: native one-hot \(\times 2-1\) (true AA \(=+1\), остальные \(-1\)); embed linear; Ho VP Gaussian на этом continuous tensor, не на learned embedding — чтобы sequence classifiers guided'или сырые logits. Square-root schedule (Austin-style discrete diffusion): при малых \(t\) argmax ещё тривиален, поэтому шума больше на ранних шагах. Sample \(t\sim U[0,T]\). [PAPER]",
                    source="[PAPER] Lisanza et al. Nat. Biotechnol. 2025, 10.1038/s41587-024-02395-w",
                ),
                P(r"Train: timestep в sequence template RF; losses на \(\hat x_0\): CE sequence + FAPE + bond angle/length + distogram + lDDT; extra KL на вычисленном \(x_{t-1}\) (Austin). Self-conditioning: no-grad predict \(x_0\) from \(x_{t+1}\), подать как template; RF 1–3 extra recycles uniformly. Algorithm S1 / Fig. S2 NR page-by-page. [PAPER]"),
                P(r"Inference: predict \(x_0\) и структуру \(y\) simultaneously; back-calculate \(x_{t-1}\) по Eq. 1; self-cond на предыдущем \(\hat x_0\). \(T\) inference можно менять независимо от train (SI Table 2); авторы: решения за 10 шагов (Fig. 1c). Clamp logits \([-3,3]\) лучше согласует AF2 (Fig. S3b). Sample \(x_{t-1}\) из \(\mathcal{N}(0,I)\) или GMM2/GMM3 на \(\{\pm 1\}\) / \(\{-1,0,1\}\). Не RFdiffusion: там шумится structure. [PAPER]"),
                P(r"Multistate (Algorithm S4): один \(x_t\), три RF forwards (parent + child A/B) с разными DSSP strings, linear combination logits → noise to \(x_{t-1}\). Classifier guidance GB1: 2-layer MLP на fitness\(>2\), 96 designs/round \(\times\) 3 vs batched UCB — не EVOLVEpro. [PAPER]"),
                level=3,
            ),
            S(
                "Joint diffusion / flow / iterative GNN (подтипы с собственными страницами)",
                M(
                    r"q(s_t,x_t,R_t\mid s_0,x_0,R_0)=q(s_t\mid s_0)\,q(x_t\mid x_0)\,q(R_t\mid R_0)",
                    caption=r"DiffAb: discrete AA + C\(\alpha\) + SO(3) шумятся независимо, reverse общий. Denoiser: \(\varepsilon\) позиции, cosine loss на \(R\), KL на sequence posterior. [CODE] FullDPM@c3e2966: tensors res_feat \((N,L,d)\), pair_feat \((N,L,L,d)\), \(R\) \((N,L,3,3)\), \(p\) \((N,L,3)\), \(s\) \((N,L)\); EpsilonNet rotate coordinate updates. Полная страница — <a href=\"/architectures/joint-sequence-structure-diffusion.html\">joint diffusion</a>.",
                    source="[PAPER] Luo et al. NeurIPS 2022; [CODE] luost26/diffab dpm_full.py",
                ),
                P(r"FlowDesign: Euclidean CFM на one-hot + C\(\alpha\) + SLERP ориентаций, IPA drift; dyMEAN prior \(\approx 15\%\) H3 AAR vs random; Ibalizumab BLI на <a href=\"/architectures/flow-matching.html\">flow-matching</a> (не копировать кампанию как axiom класса). dyMEAN: \(T=3\) AME, один structure/forward — <a href=\"/architectures/graph-neural-networks.html\">GNN</a>, не diffusion ensemble. [PAPER]"),
                level=3,
            ),
            S(
                "Смежные постановки, которые нельзя смешивать",
                T(
                    ["Постановка", "Что совместно", "Sampler", "Каталог"],
                    [
                        ["Joint generation (эта страница)", r"\(p(s,x\mid c)\) надкласс", "LM / DDPM / FM / iterative", "ESM3, PG, DiffAb, FlowDesign, dyMEAN"],
                        [r'<a href=\"/architectures/joint-sequence-structure-diffusion.html\">Joint diffusion</a>', "AA+geometry noised together", "shared reverse", "DiffAb, AbDiffuser, BoltzGen family"],
                        [r'<a href=\"/architectures/flow-matching.html\">Flow matching</a>', "joint CDR CFM", "ODE", "FlowDesign"],
                        [r'<a href=\"/architectures/protein-language-models.html\">PLM</a>', "sequence only (unless multimodal)", "AR/MLM", "ProGen, IgLM; ESM3 is more than PLM"],
                        [r'<a href=\"/architectures/inverse-folding.html\">Inverse folding</a>', r"\(p(s\mid x)\), \(x\) fixed", "AR/MPNN", "ProteinMPNN, ESM-IF1"],
                        ["Staged backbone→IF", "два процесса", "diffusion then MPNN", "RFantibody; Chroma design net"],
                    ],
                ),
                W("FAPE в ProteinGenerator — structure head RF, не default ESM3. UCB GB1 baseline у PG — сравнение авторов, не EVOLVEpro protocol."),
                level=3,
            ),
        ),
        S(
            "4. Представление данных",
            U(
                r"ESM3: три fused discrete tracks — sequence (AA+special), structure (VQ tokens from local atomic neighborhoods), function (InterPro-like keywords). Additional prompt channels: SS8, SASA, atomic coordinate prompts. Geometric attention (block 1 only) строит local frames из bond geometry и общается в global frame. Codebook cardinality structure VQ — SI NR this pass. [PAPER] Fig. 1, SI A.1.6–A.1.7.",
                r"ESM3 train mix: 3.15B sequences, 236M structures, 539M function annotations, 771B unique tokens. Predicted structures получают inverse-fold labels (SI A.2.1.3). Temporal hold-out натуральных белков для prompt-fidelity (Fig. 2A). Leakage vs therapeutic mAbs — NR. [PAPER]",
                r"ProteinGenerator: \(L\times 20\) scaled one-hot \(\{-1,+1\}\); timestep embedding в RF sequence template; optional DSSP strings; motif/composition clamps. PDB natives для fine-tune RF. Self-cond template = предыдущий \(\hat x_0\). Не learned sequence embedding как объект диффузии. [PAPER]",
                r"DiffAb (стоит на этой странице, не только ссылкой): residue encoder \(\to\) res_feat \((N,L,d)\); pair encoder \(\to\) pair_feat \((N,L,L,d)\); frames \(R\in\mathrm{SO}(3)^{N\times L}\), C\(\alpha\) \(p\in\mathbb{R}^{N\times L\times 3}\), AA \(s\in\{1,\ldots,20\}^{N\times L}\). generate_flag на CDR; framework+antigen clamped. [CODE] FullDPM@c3e2966.",
                r"FlowDesign: residue MLP (AA, all-atom, \(\chi\)); pair distances/dihedrals; IPA; CDR slice vs context \(C\); SAbDab 13 279 complexes, H3 50% cluster, 20-complex test. [PAPER] — числа на <a href=\"/architectures/flow-matching.html\">FM</a>, здесь чтобы страница не была пустой картой.",
                r"dyMEAN: full-atom multi-channel \(X_i\in\mathbb{R}^{3\times c_i}\); epitope + shadow paratope; \(T=3\) AME, \(k=9\); RAbD in silico. [PAPER] <a href=\"/architectures/graph-neural-networks.html\">GNN</a>.",
                r"Chroma: backbone coords in polymer-correlated SDE, then separate design GNN/CRF — не multimodal tokens и не simultaneous \((s,x)\) update. [PAPER]",
            ),
        ),
        S(
            "5. Физическое представление",
            P(r"Generated state — первичная структура плюс геометрия (backbone и/или all-atom decoder). ESM3 structure tokens кодируют local atomic neighborhoods, не MD trajectory. ProteinGenerator/DiffAb/FlowDesign выдают coords/frames в лабораторной системе; глобальный SE(3) обрабатывается geometric attention / equivariant layers / local frames, не «инвариантностью класса»."),
            P("Side chains: ESM3 decoder all-atom reconstruction; FlowDesign — Rosetta pack after; DiffAb — backbone+types, packer внешний. Glycans, solvent, protonation обычно отсутствуют. Chain permutation: sequence order is biological, не S_n-invariant."),
            P(r"Function track ESM3 — InterPro-like keywords, не assay \(K_D\). Fluorescence esmGFP проверялась спектрами, не antibody SPR."),
        ),
        S(
            "6. Физико-химический смысл",
            T(
                ["Feature / operation", "Physical/chemical interpretation", "Encoded how", "Limitation"],
                [
                    ["AA identity", "ковалентная первичная структура", "tokens / one-hot / categorical", "без rotamers until pack/decoder"],
                    ["Structure tokens / frames / Cα", "fold geometry", "VQ / SO(3)+R³ / coords", "snapshot, not ensemble"],
                    ["Function keywords (ESM3)", "GO/InterPro-like annotation stats", "discrete track", "не experimental function"],
                    ["DSSP / SS8 / SASA prompts", "secondary structure / exposure", "conditioner", "predicted or desired, not NMR"],
                    ["Composition / hydropathy bias (PG)", "sequence chemistry", "logit bias each step", "not expression assay"],
                    ["Multistate logit average (PG)", "one sequence, two folds", "two RF calls", "CD/HSQC ≠ antibody binder"],
                    ["Antigen coords (DiffAb/FlowDesign)", "steric context of CDR", "clamped structure", "wrong dock → wrong CDR"],
                    ["pTM / scTM / pLDDT / AAR", "self-consistency / recovery", "in silico", r"not \(K_D\) / fluorescence physics"],
                ],
                source="[INTERPRETATION] класс; tool rows — cited papers",
            ),
        ),
        S(
            "7. Что обучается",
            P(r"ESM3: masked token CE по всем tracks и всем mask rates (не BERT-15%). Structure autoencoder: pairwise distances + relative orientations bond vectors/normals (SI A.1.7.3.1, listing не копируем). Alignment: preference pairs (high pTM / low cRMSD vs worse), поднимает likelihood positives; eval Pass@128 на tertiary-contact prompts (Fig. 3). Это не ELISA fine-tune и не catalog default 1.4B checkpoint. [PAPER]"),
            P(r"ProteinGenerator: CE native sequence + FAPE + bond geometry + distogram + lDDT + KL(\(x_{t-1}\)); square-root schedule; self-conditioning; RF 1–3 extra recycles. Negative — другие 19 AA и wrong geometry via FAPE. Classifier (GB1 MLP) — optional guidance at inference, не часть RF loss. [PAPER]"),
            P(r"DiffAb: MSE на predicted coordinate noise, cosine на \(R\), KL на sequence posterior — shared reverse, факторизованный forward. FlowDesign: CFM MSE on interpolant (one-hot Euclidean ≠ discrete CTMC). dyMEAN: CE paratope + coord losses, \(T=3\). Chroma design net: sequence CE after frozen/backbone sample — не joint ELBO. [PAPER]"),
        ),
        S(
            "8. Прямой проход и information flow",
            F(
                "partial s / x / f / antigen",
                "joint network (TF tracks / RF / DPM / IPA / AME)",
                "update sequence and geometry",
                "iterate unmask / reverse / ODE / T steps",
                "optional pack / AF self-consistency",
                "assay (fluorescence, BLI, CD) if any",
                note="Схема класса. Не копия Hayes Fig. 1 / Lisanza Fig. 1 / Luo Fig. 2.",
            ),
            P(r"ESM3: prompt any subset of tracks → geometric attention (block 1) + remaining Transformer blocks → logits on masked positions → sample/unmask → iterate. Structure tokens decode all-atom отдельно. Alignment не меняет этот graph, только веса preference. [PAPER]"),
            P(r"ProteinGenerator: \(x_t\) (noisy \(L\times 20\)) + timestep + optional DSSP/motif → RoseTTAFold (recycles) → \(\hat x_0\) sequence + structure \(y\) → compute \(x_{t-1}\) (Eq. 1) → self-cond next step. Multistate: three RF calls, mix logits. Classifier guidance: extra gradient/bias on sequence logits, не отдельный ELISA loop. [PAPER]"),
            P(r"DiffAb: pair/res encoder on complex → EpsilonNet(\(\varepsilon_p,\varepsilon_R,p_{\mathrm{AA}}\)) → reverse DDPM on CDR only. FlowDesign: IPA drift along CFM interpolant. dyMEAN: three AME then Kabsch. Chroma: sample \(x\) then CRF \(s\mid x\) — staged, не этот forward."),
        ),
        S(
            "9. Training procedure",
            P(r"ESM3 pretrain: 3.15B sequences / 236M structures / 539M function annotations / 771B unique tokens. Depth помогала больше width; 98B = 216 blocks, \(1.07\times 10^{24}\) FLOPs. Inverse-fold labels на predicted structures (SI A.2.1.3). Prompt fidelity: temporally held-out naturals (Fig. 2A); после ESM-IF1 + ESMFold median pTM \(0.80\pm 0.08\), scTM \(0.96\pm 0.04\). Alignment — отдельный этап preference pairs, не pretrain CE. Leakage vs therapeutic antibodies: NR. Open 1.4B non-commercial; 7B/98B API. [PAPER]"),
            P(r"ProteinGenerator: PDB natives, \(t\sim U[0,T]\), square-root schedule, CE+FAPE+geom+KL, self-cond, RF 1–3 recycles. Antibody-specific split нет. Inference \(T\) и train \(T\) можно развести (SI Table 2). [PAPER]"),
            P(r"DiffAb: SAbDab complexes, CDR generate_flag, framework+antigen clamped; primary wet-lab нет (in silico AAR/RMSD). FlowDesign: 13 279 complexes, H3 50% identity cluster, 20-complex test, dyMEAN prior; Ibalizumab BLI — на FM page, не class axiom. dyMEAN: RAbD in silico, \(T=3\), \(k=9\). [PAPER]"),
            P("AlphaProteo/BoltzGen train sets: methods NR this pass. Chroma polymer SDE + design GNN — coordinate-diffusion page."),
        ),
        S(
            "10. Inference and generation",
            P(r"ESM3: start fully or partially masked; unmask any order until \(m=\emptyset\). README example (не paper law): 8 steps, sequence-track temperature \(T=0.7\) [DOC]. Decode structure tokens → all-atom. Alignment checkpoint vs base 1.4B — разные fidelity/diversity (Fig. 3 Pass@128). Не ancestral AR ProGen: нет фиксированного left-to-right порядка."),
            S(
                "ESM3 GFP chain-of-thought (Hayes Fig. 4) — wet-lab, не antibody",
                P(r"Prompt: sequence + structure tokens хромофор-формирующих residues и части центральной спирали natural GFP (семейство \(\approx 238\) AA). Эксп. 1: экспрессия сгенерированных designs в E. coli; well B8 \(\approx 57\%\) identity к известным FP. Эксп. 2: продолжить генерацию от B8; well C10 = esmGFP, \(58\%\) ID к известным FP. Ближайший BLAST/MMseqs hit — tagRFP (\(96\) мутаций); ближайший WT — eqFP578 (\(53\%\) ID, \(107\) позиций). \(22\) мутации внутри barrel vs tagRFP. Флуоресценция сопоставима с ordinary GFP; ширина возбуждения FWHM \(39\) nm vs EGFP \(56\) nm (в HTML «mm» — опечатка, физика спектров в nm). Оценка авторов \(\sim 500\) Myr — не молекулярные часы. Число wells кроме B8/C10 — NR. Не antibody evidence. [PAPER]"),
                level=3,
            ),
            P(r"ProteinGenerator reverse: composition bias \(25\) steps, \(70\)–\(80\) aa; charge/hydropathy \(25\) steps, \(50\) aa; repeats \(50\) steps, \(125\)–\(150\) aa, five units; barcodes \(50\) steps, \(100\) aa, C-term fixed. Unconditional in silico: \(6\%\) AF2 pLDDT\(>90\) и RMSD\(<2\) Å. Clamp \([-3,3]\). Multistate: average logits parent/child each step; MS1 CD parent \(26\%\) \(\beta\) vs children \(4\%\). GB1: 96 designs/round \(\times\) 3 vs batched UCB. [PAPER]"),
            P(r"ProteinGenerator wet-lab (не Ab): unconditional \(n=42\) expressed, \(32\) soluble monomeric SEC, designed SS, stable to \(95^\circ\mathrm{C}\). Composition \(20\%\) W/C/V/H/M, \(n=200\) in silico/AA, filter AF2 pLDDT\(>90\), RMSD\(<2\), SAP\(<30\), order top \(10\)–\(22\)/AA; expressed \(68\) soluble; Cys \(4/5\), Trp \(8/19\), Val \(19/22\), His \(10/12\), Met \(10/10\) monomeric SEC; Cys \(3\)–\(4\) disulfides by MS \(\pm\)TCEP without structural conditioning. Repeat protein crystal \(3.70\) Å vs AF2. Melittin cage: N-term \(26\) AA GIGAVLKVLTTGLPALISWIKRKRQQ, \(155\) aa, \(25\) steps, furin GRRKR; hemolysis \(15\,\mu\mathrm{M}\) vs free melittin / Triton. [PAPER]"),
            P(r"DiffAb: \(T\) reverse from random SO(3)/Gaussian/random AA on CDR; нет primary wet-lab. FlowDesign: \(T\) scaled-drift steps, one-step inferior; Ibalizumab BLI — FM page. dyMEAN: one structure per forward. [PAPER]"),
            P(r"Не путать iterative unmask ESM3 с DDPM \(T\)-steps DiffAb/PG: разная математика, похожий «цикл до готовности»."),
        ),
        S(
            "11. Conditioning",
            P("Partial sequence, partial coords/motifs, function keywords, SS/SASA, tertiary-contact coordinate prompts (ESM3 GFP: chromophore residues + helix fragment). Sequence composition 20% W/C/V/H/M, hydropathy, repeat symmetry, peptide N-term cage, DSSP multistate (ProteinGenerator). Antigen+framework clamps, CDR mask (DiffAb/FlowDesign). Epitope graph + shadow paratope (dyMEAN). Language captions — Chroma classifier guidance, не ESM3 function track."),
            P("Нет ELISA labels в ESM3 pretrain. Alignment preference pairs — pTM/cRMSD, не wet-lab Kd. PG GB1 MLP — experimental sequence–activity на GB1, не EVOLVEpro few-shot ELISA protocol. Нет UCB as class default (PG сравнивает с batched UCB как baseline авторов)."),
        ),
        S(
            "12. Вычислительная сложность",
            P(r"ESM3: Transformer depth \(\times\) length \(\times\) unmask steps; 98B / 216 blocks \(\neq\) runtime 1.4B. Geometric attention только в первом блоке (не каждый слой IPA). OOM на больших комплексах — failure mode. GFP campaign: generation cheap vs spectra/expression oracle."),
            P(r"ProteinGenerator: \(T_{\mathrm{diff}}\) \(\times\) RoseTTAFold forward (multistate \(\times 3\) RF). Typical published \(T\in\{10,25,50\}\), не обязательно train \(T\). DiffAb/FlowDesign: \(T\times(L_{\mathrm{Ab+Ag}})^2\) pair/IPA. dyMEAN: 3 layers \(\times\) 3 iters, cheaper ensemble. Staged RFdiffusion+MPNN может быть дешевле, если topology уже зафиксирована и joint state не нужен."),
            P("Wall-clock oracle (spectra, BLI, CD, crystallography) доминирует claims of function."),
        ),
        S(
            "13. Преимущества",
            U(
                r"Один процесс согласует identity и fold: меньше «IF не узнаёт петлю, которую diffusion только что нарисовал».",
                r"ESM3: any-order multimodal prompts; CAMEO recon \(<0.5\) Å; prompted generations median pTM \(0.80\pm 0.08\), scTM \(0.96\pm 0.04\) after ESM-IF1+ESMFold; alignment поднимает Pass@128. esmGFP (well C10): \(58\%\) ID к известным FP, \(96\) мутаций vs tagRFP, \(22\) в barrel, \(53\%\) vs eqFP578; FWHM возбуждения \(39\) nm vs EGFP \(56\) nm — fluorescence campaign, не Ab. [PAPER]",
                r"ProteinGenerator: sequence-level guidance (composition, repeats, hydropathy, activity classifiers) на \(L\times 20\) tensor; solutions за \(\approx 10\) steps; unconditional \(32/42\) soluble to \(95^\circ\mathrm{C}\); Cys disulfides without structural conditioning; \(3.70\) Å crystal; melittin hemolysis \(15\,\mu\mathrm{M}\); GB1 96\(\times\)3 vs UCB. General-protein wet-lab, не Ab. [PAPER]",
                r"DiffAb: CDR type+geometry together, tensors на этой странице, wet-lab нет. FlowDesign: dyMEAN prior \(\approx 15\%\) H3 AAR; Ibalizumab BLI — FM page. dyMEAN: full-atom epitope-conditioned CDR in silico.",
            ),
            P("Ни одно из in silico чисел не есть affinity. esmGFP fluorescence ≠ antibody campaign. PG GB1 guidance ≠ EVOLVEpro. Не складывать GFP spectra, PG CD/crystal и DiffAb AAR в одну метрику «joint quality»."),
        ),
        S(
            "14. Ограничения",
            U(
                "Математика: надкласс без единой loss; ESM3 discrete tokens ≠ DiffAb continuous frames; PG one-hot Gaussian ≠ categorical CTMC.",
                "Представление: paired structures required (кроме чисто sequence PLM); ESM3 7B/98B API; Chroma weights gated.",
                "Физика: joint sample ≠ bound complex; function keywords ≠ assay.",
                "Данные: PDB/AFDB bias; ESM3 leakage vs mAbs NR; FlowDesign 20-complex test; PG no Ab split.",
                "Обобщение: GFP/GB1/melittin/multistate CD не переносятся на CDR–epitope.",
                "Deployment: ESM3 small non-commercial; AlphaProteo trusted-tester; AbDiffuser no turnkey repo; BoltzGen methods unread; PG/DiffAb commits: DiffAb@c3e2966 on tool page, PG NR this pass.",
            ),
        ),
        S(
            "15. Failure modes",
            U(
                "Считать staged RFantibody или Chroma CRF этим классом как канон (pipeline даёт seq+struct, процессы разные).",
                "Считать ESM3 «просто PLM» без structure/function tracks.",
                "Считать DiffAb уравнением ESM3 или ProteinGenerator.",
                r"Считать pTM / scTM / pLDDT / AAR / Rosetta \(\Delta G\) измеренным \(K_D\).",
                "Приписать esmGFP или Ibalizumab ΔKd всему надклассу.",
                "Antibody claim от ESM3/PG/Chroma без Ab evidence.",
                "Wrong antigen dock в DiffAb/FlowDesign → sequence под чужой геометрией.",
                "Framework leakage: модель копирует native CDR (dyMEAN unigram warning на GNN page).",
            ),
        ),
        S(
            "16. Реализации в инструментах",
            T(
                ["Tool / method", "Generic architecture", "Tool-specific implementation", "Important difference"],
                [
                    [r'<a href=\"/tools/esm3.html\">ESM3</a>', "multimodal masked LM", "seq/struct/function tracks; VQ local-neighborhood tokens; geom attn block 1; 1.4/7/98B (216 blocks); all mask rates", "Science 2025; esmGFP C10 58% ID; not Ab; 1.4B non-commercial; commit NR"],
                    [r'<a href=\"/tools/protein-generator.html\">ProteinGenerator</a>', "sequence-space RF diffusion", r"\(L\times 20\) \(\pm 1\); CE+FAPE+geom+KL; clamp [-3,3]; DSSP/multistate; T=10–50", "Nat. Biotechnol. 2025; 32/42 soluble; 3.70 Å; no Ab; commit NR"],
                    [r'<a href=\"/tools/diffab.html\">DiffAb</a>', "joint seq–struct diffusion", r"CDR AA+Cα+SO(3); res_feat/pair_feat/R/p/s; EpsilonNet", "NeurIPS 2022; in silico; @c3e2966"],
                    [r'<a href=\"/tools/flowdesign.html\">FlowDesign</a>', "joint CDR flow matching", "IPA; dyMEAN prior; Rosetta pack", "канон: flow-matching page"],
                    [r'<a href=\"/tools/dymean.html\">dyMEAN</a>', "iterative full-atom E(3) GNN", "T=3 AME; shadow paratope", "канон: GNN; not a diffusion ensemble"],
                    [r'<a href=\"/tools/abdiffuser.html\">AbDiffuser</a>', "full-atom Ab joint diffusion", "HER2 campaign claimed", "repo NR; subclass diffusion"],
                    [r'<a href=\"/tools/boltzgen.html\">BoltzGen</a>', "all-atom joint family", "nanobody/peptide binders", "methods NR this pass"],
                    [r'<a href=\"/tools/chroma.html\">Chroma</a>', "staged coords then design GNN", "polymer SDE + CRF", "tagged joint; канон coordinate-diffusion"],
                    [r'<a href=\"/tools/alphaproteo.html\">AlphaProteo</a>', "closed binder generator", "target-conditioned", "no local weights; methods NR"],
                    [r'<a href=\"/tools/rfantibody.html\">RFantibody</a>', "не этот класс как канон", "frame diffusion + MPNN", "staged"],
                ],
            ),
        ),
        S(
            "17. Где применимо и где не применимо",
            P(r"Применимо: когда нельзя честно разделить backbone и sequence — multimodal prompts (<a href=\"/tools/esm3.html\">ESM3</a>, <a href=\"/workflows/joint-multimodal-generation.html\">joint multimodal workflow</a>); sequence-conditioned / multistate design (ProteinGenerator); antibody CDR co-design при известном комплексе (<a href=\"/tools/diffab.html\">DiffAb</a>, <a href=\"/tools/flowdesign.html\">FlowDesign</a>, <a href=\"/workflows/cdr-codesign-diffab.html\">CDR codesign</a>)."),
            P(r"Не применимо как замена staged de novo Fv (<a href=\"/tools/rfantibody.html\">RFantibody</a>), few-shot ELISA AL, или developability scoring. Не сравнивать esmGFP spectra, PG CD/HSQC, FlowDesign Ibalizumab BLI и DiffAb in silico AAR как одну метрику «joint quality»."),
        ),
        S(
            "18. Методологические источники",
            C(
                ref("Hayes et al., Simulating 500 million years of evolution with a language model, Science 2025, 10.1126/science.ads0018 (ESM3).", "https://doi.org/10.1126/science.ads0018"),
                ref("ESM3 code/README (Biohub/esm; commit NR this pass).", "https://github.com/biohub/esm"),
                ref("Lisanza et al., Multistate and functional protein design using RoseTTAFold sequence space diffusion, Nat. Biotechnol. 2025, 10.1038/s41587-024-02395-w (ProteinGenerator).", "https://doi.org/10.1038/s41587-024-02395-w"),
                ref("Luo et al., DiffAb, NeurIPS 2022.", "https://proceedings.neurips.cc/paper_files/paper/2022/hash/3fa7d76a0dc1179f1e98d1bc62403756-Abstract-Conference.html"),
                ref("Wu et al., FlowDesign, Cell Systems 2025.", "https://doi.org/10.1016/j.cels.2025.101270"),
                ref("Kong et al., dyMEAN, ICML 2023.", "https://proceedings.mlr.press/v202/kong23c.html"),
                ref("Ingraham et al., Chroma, Nature 2023 (staged design net).", "https://doi.org/10.1038/s41586-023-06728-8"),
                ref("Architecture joint sequence–structure diffusion", "/architectures/joint-sequence-structure-diffusion.html"),
                ref("Architecture flow matching", "/architectures/flow-matching.html"),
                ref("Architecture protein language models", "/architectures/protein-language-models.html"),
                ref("Architecture inverse folding", "/architectures/inverse-folding.html"),
                ref("Architecture graph neural networks", "/architectures/graph-neural-networks.html"),
                ref("Tool ESM3", "/tools/esm3.html"),
                ref("Tool ProteinGenerator", "/tools/protein-generator.html"),
                ref("Tool DiffAb", "/tools/diffab.html"),
                ref("Tool FlowDesign", "/tools/flowdesign.html"),
            ),
        ),
    ],
)
