from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graph import build_index
from load import load_catalog
from schema import is_nr
from validate import validate_catalog


def test_catalog_validates():
    catalog = load_catalog()
    index = build_index(catalog)
    errors = validate_catalog(catalog, index)
    assert errors == [], "\n".join(errors)


def test_reverse_links():
    catalog = load_catalog()
    index = build_index(catalog)
    antifold = index.tools_by_id["antifold"]
    assert "inverse-folding" in antifold.classification.task_ids
    assert "antifold" in index.tools_for_task["inverse-folding"]
    assert "antifold" in index.tools_for_architecture["inverse-folding"]


def test_predictors_are_not_generators():
    catalog = load_catalog()
    for dep in catalog.dependencies:
        assert dep.is_generator is False
    names = {t.identity.name.lower() for t in catalog.tools}
    assert "alphafold2 / colabfold" not in names
    assert "alphafold3" not in names


def test_papers_have_links():
    catalog = load_catalog()
    for paper in catalog.papers:
        assert not (is_nr(paper.doi) and is_nr(paper.url)), paper.id


def test_three_detailed_architecture_pages():
    catalog = load_catalog()
    detailed = [t for t in catalog.tools if t.detailed_architecture]
    slugs = {t.identity.id for t in detailed}
    assert {"antifold", "rfantibody", "diffab"} <= slugs
    for t in detailed:
        assert t.detailed_architecture.get("generation_mechanism") or t.architecture.generation_mechanism


def test_generated_object_present():
    catalog = load_catalog()
    for t in catalog.tools:
        assert t.generation.exact_generated_object
        assert t.classification.task_ids
