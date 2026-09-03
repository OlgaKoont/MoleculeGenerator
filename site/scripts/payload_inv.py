from research_lib import C, F, M, P, R, S, T, U, W, ref

INV = R(
    "partially_verified",
    last_reviewed="2026-08-26",
    commit=None,
    inaccessible=[
        "facebookresearch/esm (ESM-IF1) commit в этом проходе не аудировался; p(Y∣TX)=p(Y∣X) и recovery — Hsu ICML 2022 / geometric-transformers page, не новый code audit.",
        "RFantibody Nature SI Supplementary Fig. 1a (точный набор pair features template track) не разбирался постранично; формулировка 2D distances+dihedrals — Nature HTML 10.1038/s41586-025-09721-5.",
        "Villar et al. «Scalars are universal» доказательства и Weyl FFT restatement не извлекались из PDF; на странице — class statement, не копия теоремы.",
        "AlphaFold2 SI distogram/IPA Algorithm 20–22 намеренно не копируются; IPA здесь только как пример invariant logits внутри equivariant module.",
        "RosettaCommons/RFantibody@8fe3114 template featurizer не перечитывался в этом проходе (commit числится на tool page).",
    ],
    sections=[
        S(
            "1. Область определения",
            P(r"Invariant models — это <strong>свойство отображения</strong>, а не generative process. Сеть (или её голова) выдаёт скаляры / discrete labels / pairwise 2D features, которые <em>не меняются</em> при глобальном вращении и переносе входа. Это inductive bias внутренней геометрии, не sampler поз и не affinity predictor."),
            P(r"Не путать с <a href=\"/architectures/se3-equivariant-models.html\">SE(3)-эквивариантностью</a>: там векторы/frames поворачиваются вместе со входом. Не путать с <a href=\"/architectures/geometric-transformers.html\">geometric transformers</a> и <a href=\"/architectures/graph-neural-networks.html\">GNN</a> как семействами слоёв: оба могут быть invariant, equivariant или смешанными. Не <a href=\"/architectures/inverse-folding.html\">inverse folding</a> как задача \(p(s\mid x)\). Не ELISA AL."),
            P(r"В каталоге свойство проявляется как: encoder <a href=\"/tools/esm-if1.html\">ESM-IF1</a> / <a href=\"/tools/antifold.html\">AntiFold</a> (GVP scalars → Transformer); 2D template framework в <a href=\"/tools/rfantibody.html\">RFantibody</a>; distance edges <a href=\"/tools/proteinmpnn.html\">ProteinMPNN</a> (канон класса — GNN). Генерация CDR+dock у RFantibody живёт на <a href=\"/architectures/frame-diffusion.html\">frame diffusion</a>."),
            P(r"Задачи, где invariant map уместен: <a href=\"/tasks/inverse-folding.html\">inverse folding</a> (pose-independent sequence logits), <a href=\"/tasks/antibody-structure-aware-sequence-design.html\">structure-aware sequence</a>, ranking мутаций при фиксированном backbone. Не de novo backbone from noise."),
        ),
        S(
            "2. Интуитивный принцип",
            P("Внутренние расстояния, углы и типы аминокислот не зависят от того, как кристалл положили на столик или как PDB выровняли в лабораторной системе. Сеть, которой нужен только этот внутренний объект, не должна тратить ёмкость на все ориентации."),
            P(r"Обратная сторона: абсолютная поза, направление «куда смотрит» интерфейс и хиральность не восстанавливаются из одних unsigned distances. Поэтому генераторы поз держат equivariant vector/frame path, а invariant 2D template в RFantibody как раз <em>не</em> фиксирует dock."),
            W(r"Sequence recovery / IF \(\log p(s\mid x)\) / distogram CE / pLDDT / Rosetta \(\Delta\Delta G\) ≠ experimental \(K_D\). Инвариантность к SE(3) ≠ термодинамическая корректность."),
        ),
        S(
            "3. Формальная математическая постановка",
            P("Несколько constructions. Не записывать FAPE/IPA SI как default loss этого класса и не выдавать diffusion reverse за invariant head."),
            S(
                "Скалярная SE(3)-инвариантность",
                M(
                    r"""\begin{aligned}
f(Rx+t)&=f(x)
\quad\forall R\in\mathrm{SO}(3),\; t\in\mathbb{R}^3,\\
g(Rx+t)&=Rg(x)+t
\quad\text{(equivariance, не этот класс)}.
\end{aligned}""",
                    caption=r"\(x\) — point cloud / backbone coords. \(f\) — энергия, тип, MQA scalar, sequence logits, distogram. \(g\) — координаты/frames: страница SE(3). Translation: достаточно функций от разностей \(x_i-x_j\). [PAPER] geometric DL; контраст Thomas TFN / Satorras EGNN.",
                    source="[PAPER] class definition; Jing ICLR 2021; Hsu ICML 2022",
                ),
                level=3,
            ),
            S(
                "Конструкция через внутреннюю геометрию",
                M(
                    r"""\begin{aligned}
d_{ij}&=\lVert x_i-x_j\rVert_2,\\
f(x)&=\tilde f\bigl(\{d_{ij}\}_{i,j},\{\theta_{ijk}\},\{\omega_{ijkl}\}\bigr).
\end{aligned}""",
                    caption=r"Любая \(\tilde f\) от distances/angles/dihedrals автоматически SE(3)-invariant. Unsigned distances и углы ещё и inversion-invariant (O(3)): не отличают энантиомеры. Знаковые dihedrals / triple product \(a\cdot(b\times c)\) ломают отражения, оставаясь SO(3)-invariant. [INTERPRETATION] invariant theory; [PAPER] Bennett: pairwise distances + dihedrals as RF template.",
                    source="[PAPER] Bennett et al. Nature 2025 (template contents); [INTERPRETATION] O(3) vs SO(3)",
                ),
                P(r"Реконструкция 3D из полного distogram определяется с точностью до глобального SE(3) (и, без знаковых углов, отражения). Это не доказательство, что сеть «сгенерировала позу»: MDS/template recapitulation ≠ diffusion sample."),
                level=3,
            ),
            S(
                "GVP: invariant scalars рядом с equivariant vectors",
                M(
                    r"""\begin{aligned}
\mathrm{GVP}(s,V)&=(s',V'),\qquad
\mathrm{GVP}\bigl(s,R(V)\bigr)=\bigl(s',R(V')\bigr),\\
s'&=\sigma\bigl(W_m[\lVert V_h\rVert_2;s]+b\bigr).
\end{aligned}""",
                    caption=r"Jing Algorithm 1 / Eq. (1): \(s'\) invariant, \(V'\) equivariant к rotations <em>и reflections</em> (операции — линейные комбинации и \(L_2\)). Теорема: GVP \(G_s\) с \(n=\mu=0\) \(\varepsilon\)-approximates любую непрерывную rotation- и reflection-invariant \(F(V)\) при \(\nu\ge 3\) и линейной независимости первых трёх строк. [PAPER]",
                    source="[PAPER] Jing et al. ICLR 2021 Algorithm 1, Eq. (1), Theorem",
                ),
                P(r"Ablation Table 4 CATH 4.2 CPD: full GVP perplexity 5.29 / recovery 40.2%; only scalars 7.31 / 32.4%; only vectors 11.05 / 23.2%. Финальный invariant head не отменяет vector channels в промежуточных слоях. [PAPER]"),
                P(r"Hsu: после 4 GVP-GNN (\(k=30\)) change of basis в локальные residue frames → invariant scalars → 8+8 Transformer; \(p(Y\mid TX)=p(Y\mid X)\) для \(T\in\mathrm{SE}(3)\) (Appendix A.3). Transformer сам по себе не equivariant — инвариантность уже в его входе. [PAPER]"),
                level=3,
            ),
            S(
                "Invariant 2D template (RF / RFantibody)",
                M(
                    r"T^{\mathrm{2D}}_{ij}=\bigl(d_{ij},\,\omega_{ij},\,\ldots\bigr)\qquad\text{(pairwise distances + dihedrals)}",
                    caption=r"Bennett: framework sequence+structure подаётся в template track RF2/RFdiffusion как 2D matrix pairwise distances и dihedral angles, «from which 3D structures can be accurately recapitulated». Framework и target templates <em>не</em> кодируют взаимную 3D позу. Antibody coords шумятся; target не шумится. Dock + CDR генерирует SE(3) diffusion, не этот 2D объект. [PAPER] Fig. 1b–c; Supplementary Fig. 1a NR page-by-page.",
                    source="[PAPER] Bennett et al. Nature 2025, 10.1038/s41586-025-09721-5",
                ),
                P(r"Контраст: vanilla RFdiffusion motif scaffolding подаёт motif как <em>3D coordinates</em> (sequence+side chains), чтобы держать абсолютную геометрию сайта. [PAPER] Watson et al. Nature 2023. 2D template — другой conditioner, не «RFdiffusion всегда invariant»."),
                level=3,
            ),
            S(
                "Смежные постановки, которые нельзя смешивать",
                T(
                    ["Постановка", "Что инвариантно / нет", "Роль", "Каталог"],
                    [
                        ["Invariant map (эта страница)", r"\(f(Rx+t)=f(x)\)", "свойство головы/фич", "ESM-IF1 encoder; RFantibody 2D FR"],
                        [r'<a href=\"/architectures/se3-equivariant-models.html\">SE(3) equivariant</a>', r"\(g(Rx+t)=Rg(x)+t\)", "генерация/обновление поз", "FrameDiff, DiffAb EpsilonNet"],
                        [r'<a href=\"/architectures/geometric-transformers.html\">Geometric transformer</a>', "GVP→invariant scalars, затем TF", "сеть", "ESM-IF1, AntiFold"],
                        [r'<a href=\"/architectures/graph-neural-networks.html\">GNN</a>', "часто invariant distances; dyMEAN mixed", "sparse MPNN", "ProteinMPNN; dyMEAN seq head"],
                        [r'<a href=\"/architectures/frame-diffusion.html\">Frame diffusion</a>', "equivariant frames; optional invariant template", "генератор backbone", "RFdiffusion, RFantibody"],
                        [r'<a href=\"/architectures/autoregressive-structure-generation.html\">Torsion / AR structure</a>', "angles already SE(3)-invariant", "параметризация остова", "RamaNet / FoldingDiff, не tools"],
                    ],
                ),
                W("IPA attention logits зависят от invariant расстояний query/key points; обновление кадров эквивариантно. Это не делает AF2/tFold генератором этой страницы. FAPE не default IF loss."),
                level=3,
            ),
        ),
        S(
            "4. Представление данных",
            U(
                r"ESM-IF1 / AntiFold: N, C\(\alpha\), C; dihedral scalars; GVP vector channels из backbone; kNN \(k=30\); после encoder — invariant scalars для Transformer. Decoder one-hot AA. [PAPER] Hsu Table A.1; AntiFold inherits.",
                r"RFantibody: framework (и, по тексту, target templates) — pairwise distances + dihedrals; hotspot one-hot на epitope; CDR lengths / contigs; antibody 3D corrupted, target 3D not. [PAPER]",
                r"ProteinMPNN / LigandMPNN: residue graph; distances among N/C\(\alpha\)/C/O/virtual C\(\beta\) (LigandMPNN: 25 distances на protein graph). Канон — GNN page. [PAPER] Dauparas.",
                r"Jing GVP-GNN: node orientations (forward/reverse C\(\alpha\), imputed C\(\beta\)); edge unit C\(\alpha\)–C\(\alpha\) и length; torsion scalars. MQA: node-wise GVP → scalars → mean pool. [PAPER]",
                r"Predictor distograms (AF2/tFold/RF2): pair bins расстояний — invariant heads на другой странице. Не catalog generator.",
                "Chain permutation / ligand atom set permutation — другая группа, не SE(3). Sequence order не SE(3)-инвариантен.",
            ),
        ),
        S(
            "5. Физическое представление",
            P(r"Generated/predicted object этого свойства — скаляр или дискретная метка (AA type, GDT-like score, pair feature), не абсолютные координаты. Backbone как физический вход: пептидная геометрия. Global SE(3) лабораторной системы должен исчезнуть в \(f\). Перестановка несвязанных цепей зависит от chain encoding (Hsu: 10 gap tokens; ProteinMPNN: same-chain binary), это не SE(3)."),
            P(r"Chirality: GVP Eq. (1) reflection-equivariant на векторах и reflection-invariant на \(s'\) без явных chiral features. Jing imputed C\(\beta\) из тетраэдра \(n=\mathrm{N}-C\alpha\), \(c=\mathrm{C}-C\alpha\) — ориентированный вектор, не unsigned distance. ProtDiff/EGNN на одних C\(\alpha\) distances даёт mixed-handed helices — урок для «только \(d_{ij}\)». [PAPER] Jing; Trippe et al. ICML 2023 limitation."),
            P("Side chains, растворитель, гликаны, протонирование в invariant IF encoder обычно отсутствуют. 2D template RFantibody хранит внутреннюю геометрию framework, не химию интерфейса."),
        ),
        S(
            "6. Физико-химический смысл",
            T(
                ["Feature / operation", "Physical/chemical interpretation", "Encoded how", "Limitation"],
                [
                    [r"Pairwise \(d_{ij}\)", "внутренние контакты / packing", "explicit invariant", "O(3); нет абсолютной позы"],
                    ["Bond/torsion angles, dihedrals", r"ковалентная геометрия, \(\phi/\psi/\omega\)", "scalars / 2D template", "статичный PDB snapshot"],
                    [r"Virtual C\(\beta\)", "Cβ geometry even for Gly context", "vector or distances", "не side-chain packing"],
                    [r"GVP \(\lVert V_h\rVert_2\)", "rotation-invariant content of vectors", "concat into scalar MLP", "Jing: scalars-only хуже full GVP"],
                    ["Local-frame projection (Hsu)", "geometry in residue basis", "then discard vectors", r"Transformer не видит raw \(\mathbb{R}^3\)"],
                    ["RF 2D FR template", "сохранить Fv fold, отпустить dock", "pair distances+dihedrals", "framework не дизайн"],
                    ["IF CE / recovery", "какие AA в похожих геометриях", "softmax 20", r"not \(\Delta G\) / \(K_D\)"],
                    ["MQA GDT-TS head (Jing)", "сходство с experimental backbone", "global invariant pool", "не binding assay"],
                    ["H-bonds, solvent, glycans", "корреляты PDB", "absent explicit", "AntiFold/ESM-IF1 не моделируют glycans"],
                ],
                source="[INTERPRETATION] класс; tool rows — cited papers",
            ),
        ),
        S(
            "7. Что обучается",
            P("Обучается любая голова с invariant target. Класс не задаёт один loss."),
            P(r"ESM-IF1 / AntiFold: CE native sequence; negative — остальные 19 AA. Нет FAPE. Инвариантность — архитектурная (GVP + local frames), не штраф на аугментированные позы как единственный механизм (хотя noise на coords есть: AntiFold 0.1 Å Gaussian). [PAPER]"),
            P(r"Jing MQA: regression на GDT-TS candidate vs experimental — глобальный скаляр. CPD: 20-way softmax. [PAPER]"),
            P(r"RFantibody: train loss — MSE predicted \(x_0\) frames (equivariant generator). 2D template — conditioner, его не «обучают как генератор». Distogram CE у predictors (tFold/AF) — другая страница. [PAPER]"),
            P(r"dyMEAN: sequence head invariant CE; coords E(3)-equivariant (Kong Theorem 4.1). Predicted \(\Delta\Delta G\) MLP — не assay. [PAPER] GNN page."),
        ),
        S(
            "8. Прямой проход и information flow",
            F(
                "coords / frames in lab frame",
                "invariant features (d, angles, GVP s, 2D template)",
                "optional equivariant path (vectors, IPA, diffusion)",
                "scalar / type / pair head",
                "sample sequence or condition a pose generator",
                "external predictor / assay",
                note="Схема класса. Не копия Jing Fig. 1 / Bennett Fig. 1 / Hsu Fig. 1.",
            ),
            P(r"ESM-IF1: structure-only encoder → invariant tokens → AR decoder. RFantibody: 2D FR template + hotspots → Ab-FT RFdiffusion (frames) → ProteinMPNN CDR → RF2 filter. Не схлопывать template и diffusion в одну likelihood. [PAPER]"),
        ),
        S(
            "9. Training procedure",
            P(r"Hsu: CATH 4.3 topology 80/10/10; 12M AF2 UniRef50 с исключением Gene3D HMM val/test topologies. Mixing predicted/experimental structures. [PAPER]"),
            P(r"AntiFold: 2074 SAbDab + 147458 OAS/ABodyBuilder2; 90% concatenated-CDR identity; 3:1 CDR vs FR CE; layer-wise LR \(\alpha=0.85\). [PAPER]"),
            P(r"Jing CPD/MQA: CATH 4.2 / CASP 11–13 candidates (structure-only MQA). Не antibody campaign. [PAPER]"),
            P("RFantibody FT: predominantly antibody complexes; framework as invariant template during train so inference can specify FR without locking dock. Mix weights — SI NR this pass. [PAPER]"),
            P(r"Нет единого split «для инвариантности». Data augmentation случайными вращениями — запасной путь, если архитектура не constrains \(f(Rx+t)=f(x)\); в catalog IF/GVP это не основной механизм."),
        ),
        S(
            "10. Inference and generation",
            P(r"Чистый invariant model не семплирует позы. Inference — один (или AR) forward: sequence logits, scores, pair features."),
            P(r"ESM-IF1: AR N→C (complexes: 10 mask tokens; target chain first). Hsu recovery \(T=10^{-6}\). AntiFold default \(T=0.20\) на IMGT CDR. [PAPER]+[CODE AntiFold]"),
            P(r"RFantibody: template задаёт FR; reverse frame diffusion семплирует CDR+orientation; затем MPNN. Это generation другого класса, conditioned on invariant 2D. [PAPER]"),
            P(r"Попытка «сгенерировать coords из distogram» (MDS, RF template recapitulation) — реконструкция внутренней геометрии с точностью до SE(3), не замена <a href=\"/architectures/coordinate-diffusion.html\">coordinate</a> / frame diffusion."),
        ),
        S(
            "11. Conditioning",
            P(r"Invariant conditioner: 2D distances/dihedrals framework (RFantibody); pair distogram/template track (RF family); hotspot one-hot (не invariant geometry, а метка epitope). [PAPER]"),
            P(r"Fixed backbone coords для IF — вход \(x\); сеть должна быть invariant к тому, в каком кадре этот \(x\) подан. Partial masks (Hsu span ≤30 AA, 15% coords). Dual-state PDBFlex (Hsu Fig. 7) — два conformation, не ELISA. [PAPER]"),
            P("Нет ELISA labels. Нет UCB. Target 3D в RFantibody не заменяется одним distogram: paper отдельно держит unnoised target structure."),
        ),
        S(
            "12. Вычислительная сложность",
            P(r"Полный pairwise distogram / RF template: \(O(L^2)\) pair features (как Evoformer). kNN distances (ProteinMPNN \(k=48\), ESM-IF1 GVP \(k=30\)): \(O(Lk)\) edges, затем у Hsu ещё \(O(L^2)\) Transformer. Global invariant pool (Jing MQA) — дёшевый readout после GNN."),
            P(r"Инвариантность сама по себе не гарантирует меньший wall-clock, чем equivariant net: Hsu 142M TF дороже Jing 1M GVP-GNN. Оракул (SPR, yeast, cryo-EM) доминирует claims of function."),
        ),
        S(
            "13. Преимущества",
            U(
                r"Не нужно учить все ориентации лабораторной системы: Hsu \(p(Y\mid TX)=p(Y\mid X)\). [PAPER]",
                r"GVP-Transformer + AF2 data: 51.6% native recovery на CATH topology-held-out vs 38.3% CATH-only; buried 72%, surface 39%. [PAPER] Hsu",
                r"Jing: GVP scalars+vectors бьют scalars-only на CPD (40.2% vs 32.4% recovery) и дают competitive structure-only MQA (CASP 13 global 0.888). [PAPER]",
                r"RFantibody: invariant FR template позволяет семплировать rigid-body dock и CDR, не пересобирая framework sequence/structure. Prospective yeast/SPR/cryo-EM — evidence workflow, не proof что «2D template предсказывает \(K_D\)». [PAPER] Bennett",
                r"ProteinMPNN distance edges: 52.4% recovery vs Rosetta 32.9%; wet-lab rescue на GNN page. [PAPER] Dauparas",
                "Angle/torsion parameterization (RamaNet, FoldingDiff family) даёт SE(3)-invariant state без equivariant stack — страница AR structure / torsion diffusion.",
            ),
            P("Recovery / MQA correlation / in silico recapitulation of template ≠ fold in vitro и ≠ affinity. Hsu явно: recovery does not guarantee structural similarity. [PAPER]"),
        ),
        S(
            "14. Ограничения",
            U(
                "Математика: unsigned distances не фиксируют chirality и глобальную позу; MDS неоднозначен без extra constraints.",
                r"Представление: ESM-IF1 backbone-only; RFantibody 2D FR не дизайн framework; ProteinMPNN residue graph misses clashes until packer.",
                "Физика: invariant score ≠ potential of mean force; нет explicit solvent/entropy.",
                "Данные: PDB/AF2 memory; AntiFold OAS predicted Fv; RFantibody Ab-complex FT mix NR this pass.",
                "Обобщение: IF encoder не de novo topology; 2D template не заменяет epitope holo conformation.",
                "Deployment: ESM-IF1 MIT, commit NR; RFantibody MIT + inspected commit on tool page, template code не re-audited here; Jing gvp code drorlab/gvp не catalog tool.",
            ),
        ),
        S(
            "15. Failure modes",
            U(
                "Считать этот класс генератором backbone (это свойство map / conditioner).",
                "Смешать invariance и equivariance: «сеть SE(3)-invariant, значит она двигает координаты правильно».",
                "Питать pose generator только invariant scalars без frames/vectors (Jing only-scalars ablation; mixed-handed helices у distance-only EGNN).",
                "Подать framework RFantibody как 3D coords в кадре антигена и удивиться, что dock не сэмплируется.",
                r"Считать IF \(\Delta\log p\), distogram CE, pLDDT или Rosetta ddG измеренным \(K_D\).",
                "Считать ProteinMPNN / ESM-IF1 одним и тем же «invariant Transformer».",
                "Реконструировать 3D из distogram и назвать это sample RFdiffusion.",
                r"Игнорировать reflection: GVP \(s'\) O(3)-invariant без chiral features.",
                r"Сравнивать AntiFold AAR, Jing CASP correlation и RFantibody yeast hit rate как одну \(f\).",
            ),
        ),
        S(
            "16. Реализации в инструментах",
            T(
                ["Tool / method", "Generic architecture", "Tool-specific implementation", "Important difference"],
                [
                    [r'<a href=\"/tools/esm-if1.html\">ESM-IF1</a>', "invariant GVP encoder + AR TF", "4 GVP, k=30, 8+8 TF, 142M; 12M AF2", "ICML 2022; no primary wet-lab; commit NR"],
                    [r'<a href=\"/tools/antifold.html\">AntiFold</a>', "тот же encoder, Ab FT", "SAbDab+OAS; CDR weight; T=0.20", "verified IF page; rotation/translation invariant [PAPER]+[CODE]"],
                    [r'<a href=\"/tools/rfantibody.html\">RFantibody</a>', "invariant 2D FR template + frame diffusion", "distances+dihedrals in RF template track", "generator is diffusion; template is conditioner"],
                    [r'<a href=\"/tools/proteinmpnn.html\">ProteinMPNN</a>', "invariant distance edges on residue GNN", "N/Cα/C/O/Cβ distances; random AR", "канон: graph-neural-networks"],
                    [r'<a href=\"/tools/dymean.html\">dyMEAN</a>', "invariant sequence head + E(3) coords", "shadow paratope exchanges only h_i", "канон: GNN; Theorem 4.1"],
                    [r'<a href=\"/tools/tfold.html\">tFold</a>', "distogram/IPA predictor heads", "MSA-free Ab/Ag", "не generator этой страницы"],
                    ["Jing GVP-GNN MQA/CPD", "invariant readout after equivariant vectors", "3 encoder (+3 decoder CPD)", "не catalog tool; ICLR 2021"],
                    ["RFdiffusion motif (vanilla)", "не 2D-only", "motif as 3D coords", "Watson 2023; contrast Bennett template"],
                ],
            ),
        ),
        S(
            "17. Где применимо и где не применимо",
            P(r"Применимо: sequence/score на фиксированной геометрии (<a href=\"/tools/esm-if1.html\">ESM-IF1</a>, <a href=\"/tools/antifold.html\">AntiFold</a>, <a href=\"/workflows/antibody-inverse-folding.html\">antibody IF</a>); invariant conditioner, когда нужно сохранить внутренний fold, но сэмплировать позу (<a href=\"/tools/rfantibody.html\">RFantibody</a> FR template); energy/MQA-подобные скаляры; torsion state, если генератор живёт в углах."),
            P(r"Не применимо как de novo backbone sampler (<a href=\"/architectures/frame-diffusion.html\">frame diffusion</a>, <a href=\"/architectures/coordinate-diffusion.html\">coordinate diffusion</a>) и как few-shot ELISA AL. Не сравнивать Jing CASP GDT correlation, Hsu recovery, AntiFold AAR и RFantibody experimental hit rate как одно качество «invariant models»."),
        ),
        S(
            "18. Методологические источники",
            C(
                ref("Jing et al., Learning from Protein Structure with Geometric Vector Perceptrons, ICLR 2021.", "https://openreview.net/forum?id=1YLJDvSx6J4"),
                ref("Hsu et al., Learning inverse folding from millions of predicted structures, ICML 2022, PMLR 162:8946–8970.", "https://proceedings.mlr.press/v162/hsu22a.html"),
                ref("Hsu et al. bioRxiv 10.1101/2022.04.10.487779.", "https://doi.org/10.1101/2022.04.10.487779"),
                ref("Høie et al., AntiFold, Bioinformatics Advances 2025, 10.1093/bioadv/vbae202.", "https://doi.org/10.1093/bioadv/vbae202"),
                ref("Bennett et al., Atomically accurate de novo design of antibodies with RFdiffusion, Nature 2025, 10.1038/s41586-025-09721-5.", "https://doi.org/10.1038/s41586-025-09721-5"),
                ref("Watson et al., De novo design of protein structure and function with RFdiffusion, Nature 2023, 10.1038/s41586-023-06415-8 (motif as 3D coords).", "https://doi.org/10.1038/s41586-023-06415-8"),
                ref("Dauparas et al., ProteinMPNN, Science 2022, 10.1126/science.add2187 (invariant distance edges).", "https://doi.org/10.1126/science.add2187"),
                ref("Kong, Huang, Liu, dyMEAN, ICML 2023 (invariant sequence head).", "https://proceedings.mlr.press/v202/kong23c.html"),
                ref("Satorras, Hoogeboom, Welling, E(n) Equivariant Graph Neural Networks, ICML 2021 (invariant messages, equivariant coords).", "https://arxiv.org/abs/2102.09844"),
                ref("Trippe et al., Diffusing protein structure (ProtDiff), ICML 2023 (chirality failure of distance-only EGNN).", "https://arxiv.org/abs/2206.04119"),
                ref("Villar et al., Scalars are universal: equivariant machine learning structured like classical physics, 2021 (theory; proofs NR this pass).", "https://arxiv.org/abs/2010.13856"),
                ref("Architecture SE(3) equivariant models", "/architectures/se3-equivariant-models.html"),
                ref("Architecture geometric transformers", "/architectures/geometric-transformers.html"),
                ref("Architecture graph neural networks", "/architectures/graph-neural-networks.html"),
                ref("Architecture frame diffusion", "/architectures/frame-diffusion.html"),
                ref("Architecture inverse folding", "/architectures/inverse-folding.html"),
                ref("Tool ESM-IF1", "/tools/esm-if1.html"),
                ref("Tool AntiFold", "/tools/antifold.html"),
                ref("Tool RFantibody", "/tools/rfantibody.html"),
            ),
        ),
    ],
)
