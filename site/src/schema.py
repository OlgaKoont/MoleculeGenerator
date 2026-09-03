from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


NR = "NR"


def is_nr(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in {"", NR, "nr", "N/A", "n/a"}:
        return True
    if isinstance(value, (list, dict)) and not value:
        return True
    return False


def display(value: Any, empty: str = NR) -> str:
    if is_nr(value):
        return empty
    if isinstance(value, bool):
        return "да" if value else "нет"
    if isinstance(value, list):
        return "; ".join(display(v, empty) for v in value)
    return str(value)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class Identity(StrictModel):
    id: str
    name: str
    slug: str
    aliases: list[str] = Field(default_factory=list)
    version: str | None = None
    release_year: str | None = None
    last_verified: str | None = None
    official_repository: str | None = None
    official_documentation: str | None = None
    official_service: str | None = None
    license: str | None = None
    commercial_use_status: str | None = None
    publication_status: str | None = None


class Classification(StrictModel):
    task_ids: list[str] = Field(default_factory=list)
    workflow_ids: list[str] = Field(default_factory=list)
    architecture_ids: list[str] = Field(default_factory=list)
    generator_classes: list[str] = Field(default_factory=list)
    output_modalities: list[str] = Field(default_factory=list)
    supported_formats: str | None = None
    de_novo_or_optimization: str | None = None
    general_protein_relevance: str | None = None
    antibody_relevance: str | None = None
    vhh_relevance: str | None = Field(default=None, alias="VHH_relevance")
    mutation_relevance: str | None = None
    compatibility_group: str | None = None


class Generation(StrictModel):
    exact_generated_object: str
    required_input: str | None = None
    conditioning: str | None = None
    fixed_components: str | None = None
    editable_components: str | None = None
    generated_components: str | None = None
    support_for_single_mutations: str | None = None
    support_for_combinatorial_mutations: str | None = None
    support_for_multi_objective_optimization: str | None = None
    candidate_generation_mechanism: str | None = None


class ArchitectureBlock(StrictModel):
    base_model: str | None = None
    model_family: str | None = None
    model_type: str | None = None
    input_representation: str | None = None
    node_features: str | None = None
    edge_or_pair_features: str | None = None
    encoder: str | None = None
    decoder: str | None = None
    latent_or_generative_state: str | None = None
    equivariance: str | None = None
    conditioning_mechanism: str | None = None
    generation_mechanism: str | None = None
    sampling_procedure: str | None = None
    training_objectives: str | None = None
    losses: str | None = None
    architectural_modifications: str | None = None
    computational_complexity_drivers: str | None = None
    output: str | None = None
    internal_scorer: str | None = None
    structure_generation: str | None = None
    summary_notes: list[str] = Field(default_factory=list)
    mathematical_details: str | None = None
    source_label: str | None = None


class WorkflowComponent(StrictModel):
    name: str
    role: Literal[
        "primary_generator",
        "integrated_generator",
        "integrated_scorer",
        "integrated_structure_predictor",
        "integrated_complex_predictor",
        "integrated_relaxation",
        "mandatory_external_dependency",
        "optional_external_dependency",
        "experimental_validation",
    ]
    architecture_class: str | None = None
    integrated_or_external: Literal["integrated", "external"] = "external"
    required_or_optional: Literal["required", "optional"] = "optional"
    influences_generation_or_post_hoc: Literal[
        "generation", "post_hoc", "both", "unknown"
    ] = "unknown"
    runtime_included_or_excluded: Literal["included", "excluded", "unknown"] = "unknown"
    notes: str | None = None


class WorkflowComponents(StrictModel):
    primary_generator: str | None = None
    integrated_generators: list[str] = Field(default_factory=list)
    integrated_scorers: list[str] = Field(default_factory=list)
    integrated_structure_predictor: str | None = None
    integrated_complex_predictor: str | None = None
    integrated_relaxation: str | None = None
    mandatory_external_dependencies: list[str] = Field(default_factory=list)
    optional_external_dependencies: list[str] = Field(default_factory=list)
    breakdown: list[WorkflowComponent] = Field(default_factory=list)


class Training(StrictModel):
    training_data: str | None = None
    preprocessing: str | None = None
    negative_examples: str | None = None
    fine_tuning: str | None = None
    label_requirements: str | None = None
    reported_training_hardware: str | None = None
    reported_training_time: str | None = None


class Inference(StrictModel):
    candidate_count: str | None = None
    batch_size: str | None = None
    generation_steps: str | None = None
    recycles: str | None = None
    sequence_or_complex_size: str | None = None
    reported_runtime: str | None = None
    runtime_boundary: str | None = None
    CPU: str | None = None
    GPU: str | None = None
    VRAM: str | None = None
    RAM: str | None = None
    disk: str | None = None
    database_requirements: str | None = None


class Evidence(StrictModel):
    evidence_level: str | None = None
    retrospective_validation: str | None = None
    prospective_binding_validation: str | None = None
    prospective_functional_validation: str | None = None
    developability_validation: str | None = None
    tested_design_count: str | None = None
    success_criterion: str | None = None
    independent_validation: str | None = None
    evidence_summary: str | None = None
    prospective_flag: bool = False
    direct_antibody_flag: bool = False
    preprint_flag: bool = False


class Limitations(StrictModel):
    scientific_limitations: list[str] = Field(default_factory=list)
    architectural_limitations: list[str] = Field(default_factory=list)
    dataset_biases: list[str] = Field(default_factory=list)
    likely_failure_modes: list[str] = Field(default_factory=list)
    reproducibility_limitations: list[str] = Field(default_factory=list)
    deployment_limitations: list[str] = Field(default_factory=list)


class Relations(StrictModel):
    related_tools: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    complementary_tools: list[str] = Field(default_factory=list)
    incompatible_comparisons: list[str] = Field(default_factory=list)
    paper_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    dependency_ids: list[str] = Field(default_factory=list)
    glossary_ids: list[str] = Field(default_factory=list)


class Tool(StrictModel):
    identity: Identity
    classification: Classification
    generation: Generation
    architecture: ArchitectureBlock
    workflow_components: WorkflowComponents
    training: Training
    inference: Inference
    evidence: Evidence
    limitations: Limitations
    relations: Relations
    detailed_architecture: dict[str, Any] = Field(default_factory=dict)
    review_queue: list[str] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None

    @field_validator("generation")
    @classmethod
    def generated_object_required(cls, value: Generation) -> Generation:
        if is_nr(value.exact_generated_object):
            raise ValueError("generator must declare exact_generated_object")
        return value


class TaskStrategy(StrictModel):
    name: str
    generates: str
    representation: str
    examples: list[str] = Field(default_factory=list)
    limitation: str
    sampling: str | None = None
    novel_topology: str | None = None
    integrated_scoring: str | None = None
    complexity_drivers: str | None = None


class Consequence(StrictModel):
    decision: str
    consequence: str


class Task(StrictModel):
    id: str
    slug: str
    name: str
    group: str
    definition: str
    objective: str
    starting_inputs: list[str] = Field(default_factory=list)
    generated_objects: list[str] = Field(default_factory=list)
    generator_classes: list[str] = Field(default_factory=list)
    strategies: list[TaskStrategy] = Field(default_factory=list)
    consequences: list[Consequence] = Field(default_factory=list)
    compute_consequences: list[str] = Field(default_factory=list)
    evidence_summary: str | None = None
    incomparable: list[str] = Field(default_factory=list)
    selection_guidance: list[str] = Field(default_factory=list)
    architecture_ids: list[str] = Field(default_factory=list)
    workflow_ids: list[str] = Field(default_factory=list)
    paper_ids: list[str] = Field(default_factory=list)
    glossary_ids: list[str] = Field(default_factory=list)
    downstream: bool = False
    analysis: dict[str, Any] | None = None


class WorkflowStage(StrictModel):
    name: str
    architecture_class: str | None = None
    what_happens: str
    generation_or_evaluation: Literal["generation", "evaluation", "external_evaluation", "experiment"]
    generator: str | None = None
    intermediate_object: str | None = None
    alternatives: list[str] = Field(default_factory=list)
    node_links: list[str] = Field(default_factory=list)


class Workflow(StrictModel):
    id: str
    slug: str
    name: str
    use_case: str
    required_input: list[str] = Field(default_factory=list)
    stages: list[WorkflowStage] = Field(default_factory=list)
    hardware_runtime: str | None = None
    evidence_level: str | None = None
    failure_points: list[str] = Field(default_factory=list)
    decision_criteria: list[str] = Field(default_factory=list)
    task_ids: list[str] = Field(default_factory=list)
    tool_ids: list[str] = Field(default_factory=list)
    architecture_ids: list[str] = Field(default_factory=list)
    paper_ids: list[str] = Field(default_factory=list)
    mermaid: str | None = None
    analysis: dict[str, Any] | None = None


class ArchitecturePage(StrictModel):
    id: str
    slug: str
    name: str
    name_ru: str
    intuition: str
    mathematical_formulation: str | None = None
    input_representation: str | None = None
    generated_state: str | None = None
    training_objective: str | None = None
    inference: str | None = None
    conditioning: str | None = None
    complexity_drivers: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    applicable_task_ids: list[str] = Field(default_factory=list)
    not_for_task_ids: list[str] = Field(default_factory=list)
    paper_ids: list[str] = Field(default_factory=list)
    subtypes: list[str] = Field(default_factory=list)
    glossary_ids: list[str] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None


class PaperClaim(StrictModel):
    text: str
    kind: Literal[
        "author-reported",
        "repository-documented",
        "interpretation",
        "implementation-derived",
        "missing",
    ] = "author-reported"
    locator: str | None = None


class Paper(StrictModel):
    id: str
    slug: str
    title: str | None = None
    authors: str | None = None
    year: str | None = None
    venue: str | None = None
    publication_status: str | None = None
    doi: str | None = None
    url: str | None = None
    preprint_url: str | None = None
    tool_ids: list[str] = Field(default_factory=list)
    main_task: str | None = None
    claimed_novelty: str | None = None
    model_architecture: str | None = None
    input_representation: str | None = None
    encoder_decoder: str | None = None
    generative_state: str | None = None
    conditioning: str | None = None
    sampling: str | None = None
    training_objectives: str | None = None
    training_dataset: str | None = None
    preprocessing: str | None = None
    inference: str | None = None
    baselines: str | None = None
    retrospective_benchmarks: str | None = None
    prospective_experimental_validation: str | None = None
    tested_designs: str | None = None
    success_criterion: str | None = None
    main_results: str | None = None
    limitations: str | None = None
    demonstrates: list[str] = Field(default_factory=list)
    does_not_demonstrate: list[str] = Field(default_factory=list)
    claims: list[PaperClaim] = Field(default_factory=list)
    review_queue: list[str] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None


class GlossaryTerm(StrictModel):
    id: str
    slug: str
    term: str
    term_ru: str | None = None
    definition: str
    related_ids: list[str] = Field(default_factory=list)


class Dependency(StrictModel):
    id: str
    slug: str
    name: str
    role: str
    input_output: str | None = None
    workflow_status: str | None = None
    interpretation_boundary: str | None = None
    source: str | None = None
    is_generator: bool = False


class Catalog(StrictModel):
    tools: list[Tool]
    tasks: list[Task]
    workflows: list[Workflow]
    architectures: list[ArchitecturePage]
    papers: list[Paper]
    glossary: list[GlossaryTerm]
    dependencies: list[Dependency] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self) -> "Catalog":
        for group_name, items in [
            ("tools", self.tools),
            ("tasks", self.tasks),
            ("workflows", self.workflows),
            ("architectures", self.architectures),
            ("papers", self.papers),
            ("glossary", self.glossary),
            ("dependencies", self.dependencies),
        ]:
            ids = []
            slugs = []
            for item in items:
                if hasattr(item, "identity"):
                    ids.append(item.identity.id)
                    slugs.append(item.identity.slug)
                else:
                    ids.append(item.id)
                    slugs.append(getattr(item, "slug", item.id))
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate ids in {group_name}")
            if slugs and len(slugs) != len(set(slugs)):
                raise ValueError(f"duplicate slugs in {group_name}")
        return self
