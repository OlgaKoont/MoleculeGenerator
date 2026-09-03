from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from analysis_render import convert_research, is_substantive_research
from mappings import PREDICTOR_DEPENDENCIES
from schema import (
    ArchitecturePage,
    Catalog,
    Dependency,
    GlossaryTerm,
    Paper,
    Task,
    Tool,
    Workflow,
)


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def _read_yaml_dir(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items = []
    for file in sorted(path.glob("*.yaml")):
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        if data:
            items.append(data)
    return items


def _read_yaml_file(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else None


def lookup_sidecar(kind: str, *keys: str) -> dict[str, Any] | None:
    """Prefer content/analysis YAML; else convert a substantive content/research file."""
    seen: set[str] = set()
    for key in keys:
        if not key or key in seen:
            continue
        seen.add(key)
        data = _read_yaml_file(CONTENT / "analysis" / kind / f"{key}.yaml")
        if data:
            return data
    seen.clear()
    for key in keys:
        if not key or key in seen:
            continue
        seen.add(key)
        data = _read_yaml_file(CONTENT / "research" / kind / f"{key}.yaml")
        if data and is_substantive_research(data):
            return convert_research(data)
    return None


def _attach_analysis(catalog: Catalog) -> None:
    for tool in catalog.tools:
        tool.analysis = lookup_sidecar("tools", tool.identity.slug, tool.identity.id)
    for task in catalog.tasks:
        task.analysis = lookup_sidecar("tasks", task.slug, task.id)
    for wf in catalog.workflows:
        wf.analysis = lookup_sidecar("workflows", wf.slug, wf.id)
    for arch in catalog.architectures:
        arch.analysis = lookup_sidecar("architectures", arch.slug, arch.id)
    for paper in catalog.papers:
        paper.analysis = lookup_sidecar(
            "papers",
            paper.slug,
            paper.id,
            f"paper-{paper.slug}",
            paper.id.replace("paper-", "") if paper.id.startswith("paper-") else "",
        )


def load_catalog() -> Catalog:
    tools = [Tool.model_validate(x) for x in _read_yaml_dir(CONTENT / "tools")]
    tasks = [Task.model_validate(x) for x in _read_yaml_dir(CONTENT / "tasks")]
    workflows = [Workflow.model_validate(x) for x in _read_yaml_dir(CONTENT / "workflows")]
    architectures = [ArchitecturePage.model_validate(x) for x in _read_yaml_dir(CONTENT / "architectures")]
    papers = [Paper.model_validate(x) for x in _read_yaml_dir(CONTENT / "papers")]
    glossary = [GlossaryTerm.model_validate(x) for x in _read_yaml_dir(CONTENT / "glossary")]
    dependencies = [Dependency.model_validate(x) for x in PREDICTOR_DEPENDENCIES]
    catalog = Catalog(
        tools=tools,
        tasks=tasks,
        workflows=workflows,
        architectures=architectures,
        papers=papers,
        glossary=glossary,
        dependencies=dependencies,
    )
    _attach_analysis(catalog)
    return catalog
