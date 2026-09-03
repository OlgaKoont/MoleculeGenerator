from __future__ import annotations

from schema import Catalog, is_nr
from graph import ReverseIndex


EVALUATION_ONLY_HINTS = (
    "pLDDT",
    "affinity prediction only",
    "predictor only",
)


class ValidationError(Exception):
    pass


def validate_catalog(catalog: Catalog, index: ReverseIndex) -> list[str]:
    errors: list[str] = []

    def exists(kind: str, ident: str, where: str) -> None:
        tables = {
            "tool": index.tools_by_id,
            "task": index.tasks_by_id,
            "workflow": index.workflows_by_id,
            "architecture": index.architectures_by_id,
            "paper": index.papers_by_id,
            "glossary": index.glossary_by_id,
            "dependency": index.deps_by_id,
        }
        if ident not in tables[kind]:
            errors.append(f"{where}: missing {kind} id '{ident}'")

    for tool in catalog.tools:
        loc = f"tool:{tool.identity.id}"
        if not tool.classification.task_ids:
            errors.append(f"{loc}: no assigned task")
        if is_nr(tool.generation.exact_generated_object):
            errors.append(f"{loc}: generator has no generated object")
        if not tool.relations.paper_ids:
            errors.append(f"{loc}: missing primary paper link")
        else:
            for pid in tool.relations.paper_ids:
                exists("paper", pid, loc)
        for task_id in tool.classification.task_ids:
            exists("task", task_id, loc)
        for wf_id in tool.classification.workflow_ids:
            exists("workflow", wf_id, loc)
        for arch_id in tool.classification.architecture_ids:
            exists("architecture", arch_id, loc)
        for gid in tool.relations.glossary_ids:
            exists("glossary", gid, loc)
        for did in tool.relations.dependency_ids:
            if did in index.tools_by_id:
                continue
            exists("dependency", did, loc)
        for other in (
            tool.relations.related_tools
            + tool.relations.alternatives
            + tool.relations.complementary_tools
            + tool.relations.incompatible_comparisons
        ):
            if other == tool.identity.id:
                errors.append(f"{loc}: self-relation")
            exists("tool", other, loc)
        gen = (tool.generation.exact_generated_object or "").lower()
        if "score" in gen and "sequence" not in gen and "structure" not in gen and "mutation" not in gen:
            errors.append(f"{loc}: looks like evaluation-only output")
        if not any(
            [
                tool.identity.official_repository,
                tool.identity.official_service,
                tool.identity.official_documentation,
            ]
        ):
            # allowed if review queue records it
            if not tool.review_queue:
                errors.append(f"{loc}: no repository/service and empty review queue")

    for paper in catalog.papers:
        loc = f"paper:{paper.id}"
        if is_nr(paper.doi) and is_nr(paper.url):
            errors.append(f"{loc}: primary paper link missing")
        for tid in paper.tool_ids:
            exists("tool", tid, loc)

    for task in catalog.tasks:
        loc = f"task:{task.id}"
        for arch_id in task.architecture_ids:
            exists("architecture", arch_id, loc)
        for wf_id in task.workflow_ids:
            exists("workflow", wf_id, loc)
        for gid in task.glossary_ids:
            exists("glossary", gid, loc)

    for wf in catalog.workflows:
        loc = f"workflow:{wf.id}"
        for tid in wf.tool_ids:
            exists("tool", tid, loc)
        for task_id in wf.task_ids:
            exists("task", task_id, loc)
        for arch_id in wf.architecture_ids:
            exists("architecture", arch_id, loc)
        for pid in wf.paper_ids:
            exists("paper", pid, loc)

    for dep in catalog.dependencies:
        if dep.is_generator:
            errors.append(f"dependency:{dep.id}: predictor marked as generator")

    return errors


def assert_valid(catalog: Catalog, index: ReverseIndex) -> None:
    errors = validate_catalog(catalog, index)
    if errors:
        raise ValidationError("\n".join(errors))
