from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=96), encoding="utf-8")


ENRICHMENT = {
    "antifold": {
        "architecture": {
            "base_model": "ESM-IF1 (GVP geometric encoder + autoregressive Transformer)",
            "model_family": "Antibody-fine-tuned inverse folding",
            "model_type": "Inverse folding",
            "input_representation": "Antibody Fv/VHH backbone coordinates; residue graph; optional antigen coordinates; CDR/framework masks",
            "node_features": "Residue identity (when observed), backbone geometry features inherited from ESM-IF1",
            "edge_or_pair_features": "Geometric edges / GVP messages between neighbouring residues",
            "encoder": "GVP geometric encoder (from ESM-IF1)",
            "decoder": "Autoregressive Transformer over amino-acid tokens",
            "latent_or_generative_state": "Discrete amino-acid tokens conditioned on backbone",
            "equivariance": "Geometric encoder uses invariant/equivariant GVP features; decoder is sequence AR",
            "conditioning_mechanism": "Backbone coordinates, chain identity, residue masks, optional antigen context",
            "generation_mechanism": "Temperature-based categorical sampling / masked infilling of selected residues",
            "sampling_procedure": "Per-residue categorical sampling from conditional softmax; masks keep framework/CDR subsets fixed",
            "training_objectives": "Sequence recovery on antibody structures (fine-tuning ESM-IF1)",
            "losses": "Cross-entropy over amino-acid tokens",
            "architectural_modifications": "Fine-tuning ESM-IF1 on antibody structures rather than general proteins",
            "computational_complexity_drivers": "Fv/VHH length; presence of antigen coordinates",
            "output": "Conditional sequence distribution, sampled Fv/VHH sequences",
            "internal_scorer": "Conditional log-likelihood; zero-shot affinity correlation is only a score",
            "structure_generation": "Нет",
            "source_label": "Author-reported / Implementation-derived interpretation",
        },
        "detailed_architecture": {
            "summary_card": {
                "Base architecture": "ESM-IF1",
                "Model type": "Inverse folding",
                "Representation": "Residue graph + backbone coordinates",
                "Generation unit": "Amino-acid token",
                "Conditioning": "Backbone, chain identity, antigen context",
                "Output": "Conditional sequence distribution",
                "Sampling": "Temperature-based categorical sampling",
                "Internal scorer": "Model log-likelihood",
                "Structure generation": "Нет",
            },
            "input_representation": "На вход подаётся не «просто структура», а backbone-level residue graph: координаты тяжёлых атомов остова, маски проектируемых позиций, идентификаторы цепей и, опционально, antigen coordinates. Author-reported: Fv and VHH supported; optional antigen context.",
            "encoder": "Геометрический GVP encoder из ESM-IF1 кодирует локальные ориентации и расстояния. Implementation-derived interpretation: antibody fine-tune не меняет сам класс encoder, а адаптирует веса к SAbDab-like structures.",
            "latent_or_generative_state": "Дискретные amino-acid tokens. Геометрия не сэмплируется.",
            "conditioning_mechanism": "Coordinate conditioning через geometric edges; residue-level masks; framework можно фиксировать; antigen — optional geometric context, не sequence-only prompt.",
            "generation_mechanism": "Autoregressive decoding по residues либо masked redesign выбранных CDR/framework позиций. Backbone остаётся clamped.",
            "training_objectives": "Cross-entropy sequence recovery. Negative non-binding antigens не используются как training signal (NR / not claimed).",
            "integrated_evaluation": "Likelihood ranking is post hoc relative to geometry: it does not update backbone. No docking, no AF in-loop required. Zero-shot affinity correlation must not be read as demonstrated affinity improvement.",
            "architectural_limitations": [
                {"feature": "Fixed-backbone conditioning", "limitation": "Нельзя исследовать новую CDR topology."},
                {"feature": "Residue-level representation", "limitation": "Full-atom interactions моделируются лишь косвенно."},
                {"feature": "Training on antibody structures", "limitation": "Dataset bias и слабое покрытие редких formats возможны."},
                {"feature": "Likelihood ranker", "limitation": "Learned score может быть miscalibrated вне training distribution."},
            ],
        },
        "generation": {
            "fixed_components": "Backbone coordinates; typically most of the framework unless unmasked",
            "editable_components": "Masked CDR/framework residues",
            "generated_components": "Amino-acid identities at masked positions",
        },
        "training": {
            "training_data": "Antibody structures used to fine-tune ESM-IF1 (exact split sizes: NR here)",
            "fine_tuning": "Yes — ESM-IF1 → AntiFold",
            "negative_examples": "NR",
            "label_requirements": "Structure-derived sequences; no wet-lab affinity labels required for training",
            "reported_training_hardware": "NR",
            "reported_training_time": "NR",
        },
        "inference": {
            "GPU": "NR",
            "runtime_boundary": "Does not include downstream complex prediction or assays",
            "database_requirements": "None for inference beyond the model weights",
        },
        "relations": {
            "dependency_ids": ["alphafold3", "experimental-assays"],
            "glossary_ids": ["inverse-folding", "cdr", "framework", "likelihood", "conditioning"],
        },
    },
    "rfantibody": {
        "architecture": {
            "base_model": "Antibody-fine-tuned RFdiffusion + ProteinMPNN + fine-tuned RoseTTAFold2",
            "model_family": "SE(3) diffusion workflow, not a single network",
            "model_type": "Target-conditioned antibody backbone + sequence workflow",
            "input_representation": "Target coordinates, hotspot residues, fixed framework frames, CDR length/contig specification",
            "encoder": "RoseTTAFold-derived equivariant denoiser (antibody-fine-tuned)",
            "decoder": "Reverse diffusion over frames then MPNN sequence decoder",
            "latent_or_generative_state": "Noisy residue frames for CDRs; then discrete CDR tokens",
            "equivariance": "SE(3)-equivariant diffusion",
            "conditioning_mechanism": "Hotspot constraints, framework fixation, contig/CDR lengths, target structure",
            "generation_mechanism": "Iterative denoising of CDR frames → inverse folding → RF2 filtering",
            "sampling_procedure": "Multiple diffusion trajectories; MPNN samples per backbone; RF2/AF3 ranking",
            "training_objectives": "Diffusion denoising on antibody-like geometry (fine-tune) plus MPNN sequence recovery; RF2 is a predictor",
            "losses": "Diffusion score-matching / frame denoising (RFdiffusion family); MPNN cross-entropy; RF2 structure losses are predictor losses",
            "computational_complexity_drivers": "Trajectories × denoising steps × MPNN candidates × RF2 recycles",
            "output": "CDR backbones, CDR sequences, antibody–target complex proposals",
            "internal_scorer": "Fine-tuned RF2 self-consistency/confidence; AF3 used retrospectively in the study",
            "structure_generation": "Да, CDR/backbone geometry",
            "source_label": "Author-reported (matrix + Nature paper status)",
        },
        "detailed_architecture": {
            "summary_card": {
                "Base architecture": "RFdiffusion (Ab) + ProteinMPNN + RF2",
                "Model type": "Multi-stage generative workflow",
                "Representation": "SE(3) frames, then residue graph",
                "Generation unit": "CDR frames then amino-acid tokens",
                "Conditioning": "Target, hotspots, fixed framework, CDR lengths",
                "Output": "Sequence–structure antibody–target proposals",
                "Sampling": "Diffusion trajectories + MPNN sampling",
                "Internal scorer": "RF2 confidence / self-consistency",
                "Structure generation": "Да (CDRs/backbone)",
            },
            "input_representation": "Target structure + epitope hotspots + fixed antibody framework + CDR length contigs. Framework coordinates are clamped; CDRs are generated.",
            "encoder": "Equivariant RoseTTAFold-derived trunk as diffusion denoiser. ProteinMPNN is a separate encoder/decoder on the resulting backbone. RF2 is not a generator.",
            "latent_or_generative_state": "Continuous noisy 3D frames for designed CDR residues, then discrete sequence tokens.",
            "conditioning_mechanism": "Coordinate clamping of framework and target; hotspot residue constraints; contig specification of CDR lengths; VHH vs scFv format choice.",
            "generation_mechanism": "1) Зашумляются CDR frames. 2) Forward process — SE(3) noise as in RFdiffusion. 3) Denoiser предсказывает cleaner frames. 4) Число sampling steps — implementation/default, exact default NR here. 5) Framework и target фиксируются. 6) Sequence назначается MPNN после backbone. 7) RF2 фильтрует комплексы.",
            "training_objectives": "Antibody-fine-tuned diffusion objective on structural data; MPNN CE; RF2 trained as structure/complex predictor. Do not collapse these losses into one 'affinity loss'.",
            "integrated_evaluation": "RF2 is an integrated complex predictor/filter. AF3 is described as retrospective/recommended external filter. Neither is experimental affinity. Display/SPR remain mandatory for binding claims.",
            "architectural_limitations": [
                {"feature": "Fixed framework", "limitation": "Нет global Fv redesign."},
                {"feature": "Diffusion with many steps", "limitation": "Высокая inference cost."},
                {"feature": "Hotspot-conditioned generation", "limitation": "Ошибка epitope mapping почти фатальна."},
                {"feature": "Integrated RF2 ranking", "limitation": "Возможна miscalibration вне training distribution."},
                {"feature": "No negative antigen examples as primary objective", "limitation": "Специфичность не доказана генератором."},
            ],
        },
        "generation": {
            "fixed_components": "Antibody framework and target (except designed CDRs)",
            "editable_components": "CDR backbones and sequences",
            "generated_components": "CDR geometry, CDR sequences, complex proposals",
        },
        "training": {
            "training_data": "Antibody-fine-tuned RFdiffusion/RF2 (exact corpora: NR here)",
            "fine_tuning": "Yes, from general RFdiffusion/RF2 toward antibody geometry",
            "negative_examples": "NR as an explicit specificity-training set",
            "reported_training_hardware": "NR",
            "reported_training_time": "NR",
        },
        "inference": {
            "runtime_boundary": "Must separate diffusion, MPNN, RF2, optional AF3, and wet-lab",
            "GPU": "Required (qualitative; hours/VRAM NR)",
            "database_requirements": "No MSA database required for the diffusion stage (Author-reported workflow character); RF2 details NR",
        },
        "relations": {
            "dependency_ids": ["rf2", "alphafold3", "experimental-assays", "proteinmpnn"],
            "glossary_ids": ["diffusion", "inverse-folding", "epitope", "framework", "cdr", "plddt"],
        },
        "workflow_components": {
            "integrated_generators": ["Antibody-fine-tuned RFdiffusion", "ProteinMPNN"],
            "integrated_complex_predictor": "Fine-tuned RoseTTAFold2",
        },
    },
    "diffab": {
        "architecture": {
            "base_model": "Equivariant diffusion over residue type, Cα position and orientation",
            "model_family": "Joint sequence–structure diffusion",
            "model_type": "Antigen-conditioned CDR co-design",
            "input_representation": "Antibody–antigen complex with framework residues observed and CDR residues to be generated; residue types, Cα, orientations",
            "node_features": "Residue type (noisy), Cα, orientation frame",
            "edge_or_pair_features": "Equivariant geometric messages between residues, including antigen residues",
            "encoder": "SE(3)/E(3)-equivariant denoising network",
            "decoder": "Joint reverse diffusion of discrete type and continuous geometry",
            "latent_or_generative_state": "Noisy residue type + noisy Cα + noisy orientation",
            "equivariance": "SE(3)-equivariant",
            "conditioning_mechanism": "Fixed framework and antigen coordinates; CDR masks; complex context via geometric edges",
            "generation_mechanism": "Iterative joint denoising of type, position and orientation",
            "sampling_procedure": "Diffusion trajectories over designed CDRs while clamping context",
            "training_objectives": "Discrete + continuous denoising objectives on SAbDab-like complexes",
            "losses": "Category CE for residue type; coordinate/orientation denoising losses",
            "computational_complexity_drivers": "Designed CDR length × complex size × denoising steps × trajectories",
            "output": "CDR sequence + backbone/geometry; interface proposal",
            "internal_scorer": "Energy/structural metrics used in evaluation — not a calibrated affinity model",
            "structure_generation": "Да, CDR geometry",
            "source_label": "Author-reported (NeurIPS 2022)",
        },
        "detailed_architecture": {
            "summary_card": {
                "Base architecture": "Equivariant joint diffusion",
                "Model type": "CDR sequence–structure co-design",
                "Representation": "Residue type + Cα + orientation",
                "Generation unit": "Joint residue state",
                "Conditioning": "Antigen–antibody complex, CDR mask, fixed framework",
                "Output": "CDR sequence and geometry",
                "Sampling": "Iterative denoising",
                "Internal scorer": "Energy/structure metrics (evaluation)",
                "Structure generation": "Да",
            },
            "input_representation": "Полный complex context: antigen residues и antibody framework как observed nodes; CDR nodes зашумлены. Это не sequence-only prompt.",
            "encoder": "Equivariant GNN/transformer denoiser operating on 3D residues (Author-reported). Pairwise geometric edges to antigen provide target conditioning.",
            "latent_or_generative_state": "Joint discrete–continuous noisy state: amino-acid category, Cα coordinate, orientation frame.",
            "conditioning_mechanism": "Coordinate clamping of non-designed residues; residue masks; geometric edges to epitope; no classifier-guidance affinity head in the primary generator.",
            "generation_mechanism": "1) Зашумляются type, Cα и orientation designed residues. 2) Forward: discrete corruption + Gaussian/SO(3) noise. 3) Denoiser предсказывает cleaner type/geometry. 4) Sampling steps — paper/code default, exact number NR here. 5) Framework/antigen фиксированы. 6) Sequence и structure обновляются совместно. 7) Кандидат — decoded CDR on the given framework.",
            "training_objectives": "Combined diffusion losses. No experimental ddG labels required. Training on SAbDab-like complexes implies dataset bias.",
            "integrated_evaluation": "Primary paper is retrospective/in silico. Energy scores are evaluation, not measured affinity. Repository archived/read-only.",
            "architectural_limitations": [
                {"feature": "Requires complex structural context", "limitation": "Не стартует от одной antigen sequence."},
                {"feature": "Diffusion with many steps", "limitation": "Высокая inference cost."},
                {"feature": "SAbDab training", "limitation": "Смещение по solved complexes и обычным formats."},
                {"feature": "No prospective wet-lab in primary paper", "limitation": "Нельзя считать therapeutic generator proven."},
            ],
        },
        "generation": {
            "fixed_components": "Framework and antigen coordinates",
            "editable_components": "Masked CDRs",
            "generated_components": "CDR residue types and geometry",
        },
        "training": {
            "training_data": "Antibody–antigen complexes (SAbDab-like; exact counts NR here)",
            "negative_examples": "NR",
            "reported_training_hardware": "NR",
            "reported_training_time": "NR",
        },
        "inference": {
            "GPU": "Required (qualitative)",
            "runtime_boundary": "Evaluation energies not included as experimental time",
            "database_requirements": "None beyond weights; repository archived",
        },
        "relations": {
            "dependency_ids": ["dockq", "experimental-assays", "alphafold3"],
            "glossary_ids": ["diffusion", "equivariance", "cdr", "conditioning", "epitope"],
        },
    },
    "proteinmpnn": {
        "architecture": {
            "base_model": "Autoregressive message-passing neural network",
            "model_family": "Inverse folding GNN",
            "model_type": "Fixed-backbone sequence design",
            "input_representation": "Backbone N/Cα/C(/O) coordinates; k-nearest-neighbour residue graph; chain encodings; design masks",
            "node_features": "Backbone geometry encodings, chain index, optional residue constraints",
            "edge_or_pair_features": "Distances, relative orientations, sequence-distance features between kNN residues",
            "encoder": "Unmasked MPNN over the geometric graph",
            "decoder": "Autoregressive MPNN decoder with decoding order",
            "latent_or_generative_state": "Discrete amino-acid tokens",
            "equivariance": "Built from local geometric invariants/relative features rather than global coordinates",
            "conditioning_mechanism": "Fixed backbone, tied positions, amino-acid bias, per-position masks, multi-chain context",
            "generation_mechanism": "Autoregressive decoding over residues in a random or specified order",
            "sampling_procedure": "Temperature sampling; optional native-sequence decoding",
            "training_objectives": "Sequence recovery cross-entropy on PDB/predicted backbones",
            "losses": "Per-residue categorical CE",
            "computational_complexity_drivers": "N residues × k neighbours × decode order; number of sequences sampled",
            "output": "One or many sequences compatible with the backbone",
            "internal_scorer": "Sequence log-probability only",
            "structure_generation": "Нет",
            "source_label": "Author-reported (Science 2022)",
        },
        "detailed_architecture": {
            "summary_card": {
                "Base architecture": "MPNN",
                "Model type": "Inverse folding",
                "Representation": "Residue kNN graph + backbone coordinates",
                "Generation unit": "Amino-acid token",
                "Conditioning": "Backbone, masks, biases, tied residues",
                "Output": "Conditional sequence distribution",
                "Sampling": "Autoregressive temperature sampling",
                "Internal scorer": "Log-probability",
                "Structure generation": "Нет",
            },
            "input_representation": "Только backbone geometry, не full-atom side chains (side chains are not generated as the primary object). Ligand atoms are not native — see LigandMPNN.",
            "encoder": "Message passing on a geometric kNN graph constructed from backbone atoms.",
            "latent_or_generative_state": "Discrete sequence; coordinates remain user-supplied.",
            "conditioning_mechanism": "Masks, amino-acid composition bias, tied positions across symmetric subunits, multi-chain edges.",
            "generation_mechanism": "Random decoding order autoregression. Runtime grows with chain length, not with diffusion steps.",
            "training_objectives": "CE on native sequences given backbone. Not an affinity or ddG loss.",
            "integrated_evaluation": "No structure predictor inside. Self-consistency folding is external. Likelihood is fold compatibility, not binding.",
            "architectural_limitations": [
                {"feature": "Fixed backbone", "limitation": "Не изобретает fold/interface geometry."},
                {"feature": "General PDB prior", "limitation": "Не antibody-specialized; CDR loops may be off-distribution."},
                {"feature": "Autoregressive decoding", "limitation": "Ошибки ранних residues влияют на последующие."},
            ],
        },
        "generation": {
            "fixed_components": "Input backbone",
            "editable_components": "Positions with design mask = True",
            "generated_components": "Amino-acid sequences",
        },
        "training": {
            "training_data": "PDB and related structural sets used in the ProteinMPNN paper (exact dump version NR here)",
            "negative_examples": "Not used as binding negatives",
            "reported_training_hardware": "NR in this catalogue pass",
            "reported_training_time": "NR in this catalogue pass",
        },
        "inference": {
            "GPU": "Optional for many protein sizes (qualitative)",
            "runtime_boundary": "Excludes AF2/Rosetta/experiments",
        },
        "relations": {
            "dependency_ids": ["alphafold2", "experimental-assays"],
            "glossary_ids": ["inverse-folding", "backbone", "likelihood"],
        },
    },
    "iglm": {
        "architecture": {
            "base_model": "Autoregressive infilling language model",
            "model_family": "Antibody PLM",
            "model_type": "Sequence generator",
            "input_representation": "Heavy or light chain tokens plus species and chain-type control tokens; span masks",
            "encoder": "Transformer LM (decoder-style infilling)",
            "decoder": "Autoregressive token generation into the masked span",
            "latent_or_generative_state": "Discrete amino-acid tokens",
            "equivariance": "Нет",
            "conditioning_mechanism": "Species token, chain type, bidirectional context around the span",
            "generation_mechanism": "Infilling / full-chain ancestral sampling",
            "sampling_procedure": "Temperature categorical sampling",
            "training_objectives": "Language-modelling / infilling CE on unpaired antibody sequences",
            "losses": "Cross-entropy",
            "computational_complexity_drivers": "Sequence length; number of samples",
            "output": "VH or VL sequence, or infilled CDR span",
            "internal_scorer": "Model likelihood",
            "structure_generation": "Нет",
            "source_label": "Author-reported (Cell Systems)",
        },
        "detailed_architecture": {
            "summary_card": {
                "Base architecture": "Autoregressive infilling Transformer",
                "Model type": "Antibody sequence LM",
                "Representation": "Tokens",
                "Generation unit": "Amino-acid token",
                "Conditioning": "Species, chain type, span context",
                "Output": "Sequence",
                "Sampling": "Autoregressive",
                "Internal scorer": "Likelihood",
                "Structure generation": "Нет",
            },
            "input_representation": "Sequence tokens only. No antigen, no coordinates, no paired VH/VL tokenisation in the base generator.",
            "generation_mechanism": "Infilling uses both left and right context of a span, unlike left-to-right ProGen-style models.",
            "integrated_evaluation": "Likelihood/naturalness only. Pairing, structure, developability and binding are external.",
            "architectural_limitations": [
                {"feature": "Sequence-only generation", "limitation": "Нет прямой геометрической согласованности."},
                {"feature": "Independent chain generation", "limitation": "Не обеспечивает joint VH/VL pairing."},
                {"feature": "No antigen conditioning", "limitation": "Не target-specific generator."},
            ],
        },
        "relations": {
            "glossary_ids": ["protein-language-model", "infilling", "cdr", "likelihood"],
        },
    },
}


def deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for key, value in extra.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def main() -> None:
    tools_dir = ROOT / "content" / "tools"
    for slug, extra in ENRICHMENT.items():
        path = tools_dir / f"{slug}.yaml"
        data = load(path)
        dump(path, deep_merge(data, extra))
        print("enriched", slug)


if __name__ == "__main__":
    main()
