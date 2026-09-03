from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from graph import ReverseIndex, build_index  # noqa: E402
from analysis_render import (  # noqa: E402
    architecture_fallback,
    paper_fallback,
    render_analysis,
    tool_fallback,
)
from htmlutil import (  # noqa: E402
    badge,
    card_grid,
    doi_link,
    esc,
    github_link,
    h,
    headings_toc,
    link_or_nr,
    nr,
    p,
    pub_badges,
    src_badge,
    table,
    ul,
)
from load import load_catalog  # noqa: E402
from schema import Catalog, display, is_nr  # noqa: E402
from validate import assert_valid  # noqa: E402


DIST = ROOT / "dist"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"


def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )


def load_entry() -> dict:
    return yaml.safe_load((ROOT / "content" / "meta" / "entry.yaml").read_text(encoding="utf-8"))


def relroot(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


_ROOT_HREF = re.compile(
    r'href="/(tools|tasks|workflows|architectures|papers|glossary|compare|about|evidence)(/[^"]*)"'
)
_ROOT_INDEX = re.compile(r'href="/index\.html"')


def rewrite_root_hrefs(html: str, root: str) -> str:
    """Turn catalog `/tools/…` links into depth-relative hrefs so GitHub Pages project sites work."""
    html = _ROOT_HREF.sub(lambda m: f'href="{root}{m.group(1)}{m.group(2)}"', html)
    return _ROOT_INDEX.sub(f'href="{root}index.html"', html)


def nav_context(catalog: Catalog) -> dict:
    groups = defaultdict(list)
    group_slugs = {}
    for task in catalog.tasks:
        groups[task.group].append(task)
        group_slugs[task.group] = task.group.lower().replace(" ", "-")
    nav_tasks = [((g, group_slugs[g]), items) for g, items in groups.items()]
    return {
        "nav_tasks": nav_tasks,
        "nav_workflows": catalog.workflows,
        "nav_tools": catalog.tools,
        "nav_architectures": catalog.architectures,
    }


def render_page(jinja: Environment, catalog: Catalog, *, title: str, body: str, breadcrumbs: list, depth: int, path: Path, pager=None):
    toc = headings_toc(body)
    html = jinja.get_template("base.html").render(
        title=title,
        body=body,
        toc=toc,
        breadcrumbs=breadcrumbs,
        root=relroot(depth),
        pager=pager,
        **nav_context(catalog),
    )
    html = rewrite_root_hrefs(html, relroot(depth))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def tool_href(slug: str, depth: int) -> str:
    return f"{relroot(depth)}tools/{slug}.html"


def task_href(slug: str, depth: int) -> str:
    return f"{relroot(depth)}tasks/{slug}.html"


def wf_href(slug: str, depth: int) -> str:
    return f"{relroot(depth)}workflows/{slug}.html"


def arch_href(slug: str, depth: int) -> str:
    return f"{relroot(depth)}architectures/{slug}.html"


def paper_href(slug: str, depth: int) -> str:
    return f"{relroot(depth)}papers/{slug}.html"


def named_links(ids: list[str], lookup: dict, href_fn, depth: int, name_attr="name") -> str:
    if not ids:
        return '<span class="nr">NR</span>'
    bits = []
    for ident in ids:
        obj = lookup.get(ident)
        if not obj:
            bits.append(f'<span class="nr">{ident}</span>')
            continue
        if hasattr(obj, "identity"):
            name = obj.identity.name
            slug = obj.identity.slug
        else:
            name = getattr(obj, name_attr, None) or getattr(obj, "title", None) or getattr(obj, "term", None) or ident
            slug = getattr(obj, "slug", ident)
        bits.append(f'<a href="{href_fn(slug, depth)}">{name}</a>')
    return ", ".join(bits)


def pager_for(items, current_id, href_builder, depth, name_fn):
    ids = [name_fn(x)[0] for x in items]
    slugs_names = [name_fn(x) for x in items]
    try:
        i = ids.index(current_id)
    except ValueError:
        return None
    prev = slugs_names[i - 1] if i > 0 else None
    nxt = slugs_names[i + 1] if i < len(ids) - 1 else None
    return {
        "prev": {"href": href_builder(prev[1], depth), "label": prev[2]} if prev else None,
        "next": {"href": href_builder(nxt[1], depth), "label": nxt[2]} if nxt else None,
    }


def homepage(catalog: Catalog, index: ReverseIndex, entry: dict, jinja: Environment):
    depth = 0
    options = []
    for opt in entry["decision_options"]:
        tasks = ", ".join(
            f'<a href="{task_href(s, depth)}">{index.tasks_by_id[s].name}</a>'
            for s in opt["recommends"]["tasks"]
            if s in index.tasks_by_id
        )
        wfs = ", ".join(
            f'<a href="{wf_href(s, depth)}">{index.workflows_by_id[s].name}</a>'
            for s in opt["recommends"]["workflows"]
            if s in index.workflows_by_id
        )
        options.append([opt["label"], tasks, wfs])
    inc_rows = [[a, b, c] for a, b, c in entry["incomparable"]]
    body = (
        h(1, "ML-генераторы белков, антител и antibody-like форматов")
        + p("Документация по <strong>генеративным</strong> ML-инструментам. Навигация — по биологической задаче и практическому workflow, а не по названию архитектуры. Architecture — сквозной слой: от задачи можно спуститься к устройству модели и primary papers.")
        + '<div class="note">Predictor, docking, MD и developability scores не считаются generators. Internal confidence / likelihood / pLDDT / docking score <strong>не равны</strong> experimentally demonstrated affinity.</div>'
        + h(2, "С чего начать: какие данные у вас есть")
        + p("Селектор рекомендует страницы задач и workflows, а не «лучший инструмент вообще».")
        + table(["Исходные данные", "Задачи", "Workflows"], options)
        + h(2, "Три входа")
        + card_grid(
            [
                (f"{relroot(depth)}tasks/index.html", "Какую задачу решать?", "Таксономия design tasks и сравнение архитектурных стратегий."),
                (f"{relroot(depth)}workflows/index.html", "Какой workflow собрать?", "Входы, стадии generator vs evaluator, hardware, validation."),
                (f"{relroot(depth)}architectures/index.html", "Как модель устроена?", "Architecture Guide: diffusion, inverse folding, PLM, flow matching."),
            ]
        )
        + h(2, "Категории, которые нельзя сравнивать напрямую")
        + table(["Класс A", "Класс B", "Почему"], inc_rows)
        + h(2, "Состав каталога")
        + ul(
            [
                f'Инструменты: {len(catalog.tools)}',
                f'Задачи: {len(catalog.tasks)}',
                f'Workflows: {len(catalog.workflows)}',
                f'Architecture pages: {len(catalog.architectures)}',
                f'Papers: {len(catalog.papers)}',
            ]
        )
        + p(src_badge("Author-reported") + " Матрица источников: 13.08.2026. Поля без подтверждения — NR.")
    )
    render_page(
        jinja, catalog, title="Главная", body=body,
        breadcrumbs=[{"href": "index.html", "label": "Главная"}],
        depth=0, path=DIST / "index.html",
    )


def tasks_index(catalog: Catalog, jinja: Environment):
    groups = defaultdict(list)
    for task in catalog.tasks:
        groups[task.group].append(task)
    parts = [h(1, "Задачи"), p("Основная навигация. Downstream engineering отделён визуально и не смешивается с de novo generation.")]
    for group, items in groups.items():
        ident = group.lower().replace(" ", "-")
        parts.append(f'<h2 id="{ident}">{group}</h2>')
        rows = []
        for t in items:
            kind = "downstream" if t.downstream else "generative task"
            rows.append(
                [
                    f'<a href="{t.slug}.html">{t.name}</a>',
                    t.definition,
                    badge(kind, "warn" if t.downstream else "peer"),
                ]
            )
        parts.append(table(["Задача", "Определение", "Класс"], rows))
    render_page(
        jinja, catalog, title="Задачи", body="".join(parts),
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Задачи"}],
        depth=1, path=DIST / "tasks" / "index.html",
    )


def task_page(catalog: Catalog, index: ReverseIndex, task, jinja: Environment):
    depth = 1
    tools = [index.tools_by_id[i] for i in index.tools_for_task.get(task.id, []) if i in index.tools_by_id]
    wfs = [index.workflows_by_id[i] for i in index.workflows_for_task.get(task.id, []) if i in index.workflows_by_id]
    strat_rows = [
        [
            s.name,
            s.generates,
            s.representation,
            named_links(s.examples, index.tools_by_id, tool_href, depth),
            s.limitation,
            nr(s.sampling),
            nr(s.novel_topology),
            nr(s.integrated_scoring),
            nr(s.complexity_drivers),
        ]
        for s in task.strategies
    ]
    cons_rows = [[c.decision, c.consequence] for c in task.consequences]
    tool_rows = [
        [
            f'<a href="{tool_href(t.identity.slug, depth)}">{t.identity.name}</a>',
            nr(t.generation.exact_generated_object),
            pub_badges(t.identity.publication_status, t.evidence.preprint_flag),
            nr(t.evidence.evidence_level),
        ]
        for t in tools
    ]
    body = (
        h(1, task.name)
        + p(task.definition)
        + (badge("Downstream, не generation", "warn") if task.downstream else badge("Generative task", "peer"))
        + h(2, "Биологическая и инженерная цель")
        + p(task.objective)
        + h(2, "Возможные исходные данные")
        + ul(task.starting_inputs)
        + h(2, "Что именно генерируется")
        + ul(task.generated_objects)
        + h(2, "Классы генераторов")
        + ul(task.generator_classes)
        + h(2, "Какие архитектурные подходы используются")
        + (table(
            ["Стратегия", "Что генерирует", "Представление", "Примеры", "Ограничение", "Sampling", "Novel topology", "Integrated scoring", "Complexity"],
            strat_rows,
        ) if strat_rows else p("Для downstream-задач генеративных стратегий нет."))
        + h(2, "Architecture-to-workflow consequences")
        + (table(["Архитектурное решение", "Практическое следствие"], cons_rows) if cons_rows else p('<span class="nr">NR</span>'))
        + h(2, "Compute и deployment")
        + ul(task.compute_consequences)
        + h(2, "Доступные инструменты")
        + (table(["Инструмент", "Generated object", "Публикация", "Evidence"], tool_rows) if tool_rows else p("В текущем каталоге нет привязанных generators."))
        + h(2, "Типовые workflows")
        + (ul([f'<a href="{wf_href(w.slug, depth)}">{w.name}</a>' for w in wfs]) if wfs else p('<span class="nr">NR</span>'))
        + h(2, "Evidence summary")
        + p(nr(task.evidence_summary))
        + h(2, "Что нельзя сравнивать напрямую")
        + ul(task.incomparable)
        + h(2, "Как выбирать")
        + ul(task.selection_guidance)
        + h(2, "Связанные архитектурные концепции")
        + named_links(task.architecture_ids, index.architectures_by_id, arch_href, depth)
        + h(2, "Primary references")
        + (named_links(sorted({pid for t in tools for pid in t.relations.paper_ids}), index.papers_by_id, paper_href, depth) if tools else p('<span class="nr">NR</span>'))
        + (h(2, "Source-grounded notes") + render_analysis(task.analysis, kind="task") if task.analysis else "")
    )
    items = catalog.tasks
    render_page(
        jinja, catalog, title=task.name, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Задачи"},
            {"href": f"{task.slug}.html", "label": task.name},
        ],
        depth=1, path=DIST / "tasks" / f"{task.slug}.html",
        pager=pager_for(items, task.id, task_href, 1, lambda t: (t.id, t.slug, t.name)),
    )


def workflows_index(catalog: Catalog, jinja: Environment):
    rows = []
    for w in catalog.workflows:
        rows.append([
            f'<a href="{w.slug}.html">{w.name}</a>',
            w.use_case,
            nr(w.evidence_level),
        ])
    body = h(1, "Практические workflows") + p("Каждый workflow показывает место generator, integrated scorer и external validation.") + table(["Workflow", "Сценарий", "Evidence"], rows)
    render_page(
        jinja, catalog, title="Workflows", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Workflows"}],
        depth=1, path=DIST / "workflows" / "index.html",
    )


def workflow_page(catalog: Catalog, index: ReverseIndex, wf, jinja: Environment):
    depth = 1
    stage_rows = [
        [
            s.name,
            nr(s.architecture_class),
            s.what_happens,
            s.generation_or_evaluation,
            (f'<a href="{tool_href(s.generator, depth)}">{s.generator}</a>' if s.generator and s.generator in index.tools_by_id else nr(s.generator)),
            nr(s.intermediate_object),
            named_links(s.alternatives, {**index.tools_by_id, **index.deps_by_id}, lambda slug, d: (
                tool_href(slug, d) if slug in index.tools_by_id else f"{relroot(d)}about/index.html#{slug}"
            ), depth) if s.alternatives else '<span class="nr">NR</span>',
        ]
        for s in wf.stages
    ]
    flow = '<div class="flow">'
    for i, s in enumerate(wf.stages):
        if i:
            flow += '<span class="arrow">→</span>'
        flow += f'<div class="node">{s.name}</div>'
    flow += "</div>"
    mermaid = f'<details class="math-box"><summary>Mermaid diagram</summary><pre class="math">{wf.mermaid or "NR"}</pre></details>'
    body = (
        h(1, wf.name)
        + h(2, "Практический сценарий") + p(wf.use_case)
        + h(2, "Вход") + ul(wf.required_input)
        + h(2, "Pipeline diagram") + flow + mermaid
        + h(2, "Стадии pipeline")
        + table(["Стадия", "Архитектурный класс", "Что происходит", "Генерация или оценка", "Generator", "Промежуточный объект", "Альтернативы"], stage_rows)
        + h(2, "Hardware и runtime") + p(nr(wf.hardware_runtime))
        + h(2, "Evidence level") + p(nr(wf.evidence_level))
        + h(2, "Точки отказа") + ul(wf.failure_points)
        + h(2, "Критерии решения") + ul(wf.decision_criteria)
        + h(2, "Связанные задачи") + named_links(wf.task_ids, index.tasks_by_id, task_href, depth)
        + h(2, "Связанные инструменты") + named_links(wf.tool_ids, index.tools_by_id, tool_href, depth)
        + h(2, "Архитектуры") + named_links(wf.architecture_ids, index.architectures_by_id, arch_href, depth)
        + h(2, "Papers") + named_links(wf.paper_ids, index.papers_by_id, paper_href, depth)
        + (h(2, "Source-grounded notes") + render_analysis(wf.analysis, kind="workflow") if wf.analysis else "")
    )
    render_page(
        jinja, catalog, title=wf.name, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Workflows"},
            {"href": f"{wf.slug}.html", "label": wf.name},
        ],
        depth=1, path=DIST / "workflows" / f"{wf.slug}.html",
        pager=pager_for(catalog.workflows, wf.id, wf_href, 1, lambda w: (w.id, w.slug, w.name)),
    )


def tools_index(catalog: Catalog, jinja: Environment):
    rows = []
    for t in catalog.tools:
        ident = t.identity
        rows.append(
            f'<tr class="tool-row" data-mod="{" ".join(t.classification.output_modalities)}" '
            f'data-kind="{(t.classification.de_novo_or_optimization or "").lower()}" '
            f'data-ab="{1 if t.evidence.direct_antibody_flag else 0}" '
            f'data-vhh="{(t.classification.vhh_relevance or "").lower()}" '
            f'data-ev="{1 if t.evidence.prospective_flag else 0}" '
            f'data-open="{1 if ident.official_repository else 0}" '
            f'data-pre="{1 if t.evidence.preprint_flag else 0}" '
            f'data-group="{t.classification.compatibility_group or ""}">'
            f'<td><a href="{ident.slug}.html">{ident.name}</a></td>'
            f'<td>{nr(t.generation.exact_generated_object)}</td>'
            f'<td>{nr(t.classification.generator_classes)}</td>'
            f'<td>{pub_badges(ident.publication_status, t.evidence.preprint_flag)}</td>'
            f'<td>{nr(t.evidence.evidence_level)}</td>'
            f'<td>{github_link(ident.official_repository) if ident.official_repository else (link_or_nr(ident.official_service) if ident.official_service else nr(None))}</td>'
            "</tr>"
        )
    filters = """
    <div class="filters" id="tool-filters">
      <label><input type="checkbox" data-f="mod" value="sequence"> sequence</label>
      <label><input type="checkbox" data-f="mod" value="structure"> structure</label>
      <label><input type="checkbox" data-f="mod" value="joint"> joint</label>
      <label><input type="checkbox" data-f="ab" value="1"> antibody evidence</label>
      <label><input type="checkbox" data-f="ev" value="1"> prospective flag</label>
      <label><input type="checkbox" data-f="open" value="1"> GitHub/repo</label>
      <label><input type="checkbox" data-f="pre" value="0"> только peer-reviewed / не preprint filter</label>
    </div>
    """
    body = (
        h(1, "Каталог generative tools")
        + p("Фильтры работают локально, без сервера. Canonical description каждого инструмента — на его странице, без дублей.")
        + filters
        + '<div class="table-wrap"><table id="tool-table"><thead><tr>'
        + "<th>Инструмент</th><th>Что генерирует</th><th>Класс</th><th>Публикация</th><th>Evidence</th><th>Repo / service</th>"
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )
    render_page(
        jinja, catalog, title="Инструменты", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Инструменты"}],
        depth=1, path=DIST / "tools" / "index.html",
    )


def kv_table(pairs: list[tuple[str, str]]) -> str:
    return table(["Поле", "Значение"], [[k, v] for k, v in pairs])


def tool_page(catalog: Catalog, index: ReverseIndex, tool, jinja: Environment):
    depth = 1
    ident = tool.identity
    ev = tool.evidence
    arch = tool.architecture
    gen = tool.generation
    det = tool.detailed_architecture or {}
    summary = det.get("summary_card") or {
        "Base architecture": display(arch.base_model),
        "Model type": display(arch.model_type),
        "Representation": display(arch.input_representation),
        "Generation unit": display(gen.exact_generated_object),
        "Conditioning": display(arch.conditioning_mechanism),
        "Output": display(arch.output),
        "Sampling": display(arch.sampling_procedure),
        "Internal scorer": display(arch.internal_scorer),
        "Structure generation": display(arch.structure_generation),
    }
    br_rows = [
        [
            c.name,
            c.role,
            nr(c.architecture_class),
            c.integrated_or_external,
            c.required_or_optional,
            c.influences_generation_or_post_hoc,
            c.runtime_included_or_excluded,
        ]
        for c in tool.workflow_components.breakdown
    ]
    lim_rows = [[x.get("feature", ""), x.get("limitation", "")] for x in det.get("architectural_limitations", [])]
    body = (
        h(1, ident.name)
        + p(" ".join(ident.aliases) if ident.aliases else "")
        + pub_badges(ident.publication_status, ev.preprint_flag)
        + (" " + badge("Prospective flag", "peer") if ev.prospective_flag else "")
        + (" " + badge("Direct antibody flag", "src") if ev.direct_antibody_flag else "")
        + h(2, "Summary card")
        + kv_table(
            [
                ("Год / version", f"{nr(ident.release_year)} / {nr(ident.version)}"),
                ("Last verified", nr(ident.last_verified)),
                ("Что генерирует", nr(gen.exact_generated_object)),
                ("Форматы", nr(tool.classification.supported_formats)),
                ("De novo или optimization", nr(tool.classification.de_novo_or_optimization)),
                ("DOI", doi_link(index.papers_by_id[tool.relations.paper_ids[0]].doi if tool.relations.paper_ids else None)),
                ("Paper", link_or_nr(index.papers_by_id[tool.relations.paper_ids[0]].url if tool.relations.paper_ids else None)),
                ("GitHub / repo", github_link(ident.official_repository)),
                ("Service / docs", link_or_nr(ident.official_service or ident.official_documentation)),
                ("Лицензия", nr(ident.license)),
                ("Доступность / commercial-use", nr(ident.commercial_use_status)),
            ]
        )
        + h(2, "Задача и generated object")
        + p("<strong>Used in these tasks:</strong> " + named_links(tool.classification.task_ids, index.tasks_by_id, task_href, depth))
        + p("<strong>Part of these workflows:</strong> " + named_links(tool.classification.workflow_ids, index.workflows_by_id, wf_href, depth))
        + kv_table(
            [
                ("Required input", nr(gen.required_input)),
                ("Conditioning", nr(gen.conditioning)),
                ("Fixed", nr(gen.fixed_components)),
                ("Editable", nr(gen.editable_components)),
                ("Generated", nr(gen.generated_components)),
                ("Single mutations", nr(gen.support_for_single_mutations)),
                ("Combinatorial mutations", nr(gen.support_for_combinatorial_mutations)),
                ("Multi-objective", nr(gen.support_for_multi_objective_optimization)),
            ]
        )
        + h(2, "Architecture and operating principle")
        + src_badge(arch.source_label or "Author-reported (matrix)")
        + kv_table([[k, nr(v)] for k, v in summary.items()])
        + h(3, "Input representation")
        + p(nr(det.get("input_representation") or arch.input_representation))
        + kv_table(
            [
                ("Node features", nr(arch.node_features)),
                ("Edge / pair features", nr(arch.edge_or_pair_features)),
            ]
        )
        + h(3, "Encoder и decoder")
        + p(nr(det.get("encoder") or arch.encoder))
        + kv_table([("Encoder", nr(arch.encoder)), ("Decoder", nr(arch.decoder))])
        + h(3, "Latent or generative state")
        + p(nr(det.get("latent_or_generative_state") or arch.latent_or_generative_state))
        + h(3, "Conditioning mechanism")
        + p(nr(det.get("conditioning_mechanism") or arch.conditioning_mechanism))
        + h(3, "Generation mechanism")
        + p(nr(det.get("generation_mechanism") or arch.generation_mechanism))
        + p("Sampling: " + nr(arch.sampling_procedure))
        + h(3, "Training objectives")
        + p(nr(det.get("training_objectives") or arch.training_objectives))
        + p("Losses: " + nr(arch.losses))
        + (f'<details class="math-box"><summary>Mathematical details</summary><pre class="math">{arch.mathematical_details}</pre></details>' if arch.mathematical_details else p("Mathematical details: " + nr(None)))
        + h(3, "Integrated evaluation")
        + p(nr(det.get("integrated_evaluation") or arch.internal_scorer))
        + h(3, "Architectural limitations")
        + (table(["Архитектурная особенность", "Возможное ограничение"], lim_rows) if lim_rows else ul(tool.limitations.architectural_limitations or tool.limitations.scientific_limitations))
        + p("Uses these architecture components: " + named_links(tool.classification.architecture_ids, index.architectures_by_id, arch_href, depth))
        + h(2, "Generator versus evaluation")
        + table(
            ["Component", "Role", "Architecture class", "Integrated or external", "Required or optional", "Influences generation or post hoc", "Runtime included or excluded"],
            br_rows or [["NR", "NR", "NR", "NR", "NR", "NR", "NR"]],
        )
        + h(2, "Training data и biases")
        + kv_table(
            [
                ("Training data", nr(tool.training.training_data)),
                ("Preprocessing", nr(tool.training.preprocessing)),
                ("Negative examples", nr(tool.training.negative_examples)),
                ("Fine-tuning", nr(tool.training.fine_tuning)),
                ("Label requirements", nr(tool.training.label_requirements)),
                ("Training hardware", nr(tool.training.reported_training_hardware)),
                ("Training time", nr(tool.training.reported_training_time)),
            ]
        )
        + h(2, "Inference hardware и runtime")
        + kv_table(
            [
                ("Candidate count", nr(tool.inference.candidate_count)),
                ("Batch size", nr(tool.inference.batch_size)),
                ("Generation steps", nr(tool.inference.generation_steps)),
                ("Recycles", nr(tool.inference.recycles)),
                ("Size", nr(tool.inference.sequence_or_complex_size)),
                ("Reported runtime", nr(tool.inference.reported_runtime)),
                ("Runtime boundary", nr(tool.inference.runtime_boundary)),
                ("CPU", nr(tool.inference.CPU)),
                ("GPU", nr(tool.inference.GPU)),
                ("VRAM", nr(tool.inference.VRAM)),
                ("RAM", nr(tool.inference.RAM)),
                ("Disk", nr(tool.inference.disk)),
                ("Databases", nr(tool.inference.database_requirements)),
            ]
        )
        + h(2, "Experimental evidence")
        + kv_table(
            [
                ("Evidence class", nr(ev.evidence_level)),
                ("Retrospective", nr(ev.retrospective_validation)),
                ("Prospective binding", nr(ev.prospective_binding_validation)),
                ("Prospective function", nr(ev.prospective_functional_validation)),
                ("Developability", nr(ev.developability_validation)),
                ("Tested design count", nr(ev.tested_design_count)),
                ("Success criterion", nr(ev.success_criterion)),
                ("Independent validation", nr(ev.independent_validation)),
                ("Summary", nr(ev.evidence_summary)),
            ]
        )
        + h(2, "Limitations and failure modes")
        + ul(tool.limitations.scientific_limitations)
        + p("Deployment: " + nr(tool.limitations.deployment_limitations))
        + h(2, "Reproducibility, license, commercial use")
        + kv_table(
            [
                ("Repo", github_link(ident.official_repository)),
                ("License", nr(ident.license)),
                ("Commercial-use status", nr(ident.commercial_use_status)),
            ]
        )
        + h(2, "Related tools")
        + p("Alternative tools: " + named_links(tool.relations.alternatives, index.tools_by_id, tool_href, depth))
        + p("Complementary: " + named_links(tool.relations.complementary_tools, index.tools_by_id, tool_href, depth))
        + p("Related: " + named_links(tool.relations.related_tools, index.tools_by_id, tool_href, depth))
        + h(2, "Not directly comparable with")
        + named_links(tool.relations.incompatible_comparisons, index.tools_by_id, tool_href, depth)
        + '<div class="warn">Сравнение допустимо только внутри совместимых категорий. Runtime и quality AntiFold vs RFantibody нельзя читать как одну шкалу: разные starting points и generated objects.</div>'
        + h(2, "Depends on these external modules")
        + (ul([index.deps_by_id[d].name if d in index.deps_by_id else d for d in tool.relations.dependency_ids]) if tool.relations.dependency_ids else p('<span class="nr">NR</span>'))
        + h(2, "Related glossary terms")
        + named_links(tool.relations.glossary_ids, index.glossary_by_id, lambda slug, d: f"{relroot(d)}glossary/{slug}.html", depth, name_attr="term")
        + h(2, "Primary paper и полный список источников")
        + named_links(tool.relations.paper_ids, index.papers_by_id, paper_href, depth)
        + p("Source matrix: landscape xlsx, last verified 2026-08-13.")
        + (h(2, "Review queue") + ul(tool.review_queue) if tool.review_queue else "")
        + h(2, "Детальный source-grounded разбор")
        + render_analysis(tool.analysis or tool_fallback(tool), kind="tool")
    )
    render_page(
        jinja, catalog, title=ident.name, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Инструменты"},
            {"href": f"{ident.slug}.html", "label": ident.name},
        ],
        depth=1, path=DIST / "tools" / f"{ident.slug}.html",
        pager=pager_for(catalog.tools, ident.id, tool_href, 1, lambda t: (t.identity.id, t.identity.slug, t.identity.name)),
    )


def architectures_index(catalog: Catalog, index: ReverseIndex, jinja: Environment):
    rows = [
        [
            f'<a href="{a.slug}.html">{a.name}</a>',
            a.name_ru,
            ", ".join(f'<a href="../tools/{tid}.html">{index.tools_by_id[tid].identity.name}</a>' for tid in index.tools_for_architecture.get(a.id, []) if tid in index.tools_by_id) or '<span class="nr">NR</span>',
        ]
        for a in catalog.architectures
    ]
    body = h(1, "Architecture Guide") + p("Общие объяснения живут здесь и переиспользуются через ссылки. На странице инструмента — только tool-specific implementation.") + table(["Концепция", "По-русски", "Инструменты"], rows)
    render_page(
        jinja, catalog, title="Architecture Guide", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Architecture Guide"}],
        depth=1, path=DIST / "architectures" / "index.html",
    )


def architecture_page(catalog: Catalog, index: ReverseIndex, arch, jinja: Environment):
    depth = 1
    tools = index.tools_for_architecture.get(arch.id, [])
    analysis = arch.analysis or architecture_fallback(arch)
    body = (
        h(1, arch.name)
        + p(f"{arch.name_ru}. Established English term: <strong>{esc(arch.name)}</strong>.")
        + render_analysis(analysis, kind="architecture")
        + h(2, "Инструменты, использующие подход")
        + named_links(tools, index.tools_by_id, tool_href, depth)
        + h(2, "Где применимо")
        + named_links(arch.applicable_task_ids, index.tasks_by_id, task_href, depth)
        + h(2, "Где не стоит использовать")
        + named_links(arch.not_for_task_ids, index.tasks_by_id, task_href, depth)
        + h(2, "Papers каталога")
        + named_links(arch.paper_ids, index.papers_by_id, paper_href, depth)
        + (h(2, "Подтипы класса") + ul(arch.subtypes) if arch.subtypes else "")
    )
    render_page(
        jinja, catalog, title=arch.name, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Architecture Guide"},
            {"href": f"{arch.slug}.html", "label": arch.name},
        ],
        depth=1, path=DIST / "architectures" / f"{arch.slug}.html",
        pager=pager_for(catalog.architectures, arch.id, arch_href, 1, lambda a: (a.id, a.slug, a.name)),
    )


def papers_index(catalog: Catalog, jinja: Environment):
    rows = []
    for ppr in catalog.papers:
        rows.append([
            f'<a href="{ppr.slug}.html">{nr(ppr.title)}</a>',
            nr(ppr.year),
            pub_badges(ppr.publication_status, "preprint" in (ppr.publication_status or "").lower()),
            doi_link(ppr.doi),
            named_links(ppr.tool_ids, {t.identity.id: t for t in catalog.tools}, tool_href, 1),
        ])
    body = h(1, "Papers") + p("Primary peer-reviewed paper, preprint или technical report — с явной меткой статуса. DOI и GitHub вынесены на страницы инструментов.") + table(["Title", "Год", "Статус", "DOI", "Tools"], rows)
    render_page(
        jinja, catalog, title="Papers", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Papers"}],
        depth=1, path=DIST / "papers" / "index.html",
    )


KIND_LABEL = {
    "author-reported": "Author-reported",
    "repository-documented": "Repository-documented",
    "interpretation": "Interpretation",
    "implementation-derived": "Implementation-derived interpretation",
    "missing": "NR",
}


def paper_page(catalog: Catalog, index: ReverseIndex, paper, jinja: Environment):
    depth = 1
    claims = table(
        ["Утверждение", "Тип", "Локатор"],
        [[c.text, KIND_LABEL.get(c.kind, c.kind), nr(c.locator)] for c in paper.claims] or [["NR", "NR", "NR"]],
    )
    body = (
        h(1, paper.title or paper.id)
        + pub_badges(paper.publication_status, "preprint" in (paper.publication_status or "").lower())
        + kv_table(
            [
                ("Authors", nr(paper.authors)),
                ("Year", nr(paper.year)),
                ("Venue / status", nr(paper.venue)),
                ("DOI", doi_link(paper.doi)),
                ("URL", link_or_nr(paper.url)),
                ("Preprint URL", link_or_nr(paper.preprint_url)),
                ("Tools", named_links(paper.tool_ids, index.tools_by_id, tool_href, depth)),
            ]
        )
        + h(2, "Задача и claimed novelty")
        + kv_table([("Main biological task", nr(paper.main_task)), ("Claimed novelty", nr(paper.claimed_novelty))])
        + h(2, "Архитектура")
        + kv_table(
            [
                ("Model architecture", nr(paper.model_architecture)),
                ("Input representation", nr(paper.input_representation)),
                ("Encoder / decoder", nr(paper.encoder_decoder)),
                ("Generative state", nr(paper.generative_state)),
                ("Conditioning", nr(paper.conditioning)),
                ("Sampling", nr(paper.sampling)),
            ]
        )
        + h(2, "Training")
        + kv_table(
            [
                ("Objectives / losses", nr(paper.training_objectives)),
                ("Dataset", nr(paper.training_dataset)),
                ("Preprocessing", nr(paper.preprocessing)),
            ]
        )
        + h(2, "Inference") + p(nr(paper.inference))
        + h(2, "Baselines и retrospective benchmarks")
        + kv_table([("Baselines", nr(paper.baselines)), ("Retrospective", nr(paper.retrospective_benchmarks))])
        + h(2, "Prospective experimental validation")
        + kv_table(
            [
                ("Prospective", nr(paper.prospective_experimental_validation)),
                ("Tested designs", nr(paper.tested_designs)),
                ("Success criterion", nr(paper.success_criterion)),
                ("Main results", nr(paper.main_results)),
            ]
        )
        + h(2, "Limitations") + p(nr(paper.limitations))
        + h(2, "Что статья показывает") + ul(paper.demonstrates)
        + h(2, "Чего статья не показывает") + ul(paper.does_not_demonstrate)
        + h(2, "Размеченные утверждения") + claims
        + (h(2, "Review queue") + ul(paper.review_queue) if paper.review_queue else "")
        + h(2, "Source-grounded разбор статьи")
        + render_analysis(paper.analysis or paper_fallback(paper), kind="paper")
    )
    render_page(
        jinja, catalog, title=paper.title or paper.id, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Papers"},
            {"href": f"{paper.slug}.html", "label": paper.title or paper.id},
        ],
        depth=1, path=DIST / "papers" / f"{paper.slug}.html",
        pager=pager_for(catalog.papers, paper.id, paper_href, 1, lambda p: (p.id, p.slug, p.title or p.id)),
    )


def glossary_index(catalog: Catalog, jinja: Environment):
    rows = [[f'<a href="{g.slug}.html">{g.term}</a>', nr(g.term_ru), g.definition] for g in catalog.glossary]
    body = h(1, "Glossary") + table(["Term", "По-русски", "Определение"], rows)
    render_page(
        jinja, catalog, title="Glossary", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Glossary"}],
        depth=1, path=DIST / "glossary" / "index.html",
    )


def glossary_page(catalog: Catalog, index: ReverseIndex, term, jinja: Environment):
    pages = index.glossary_pages.get(term.id, [])
    links = []
    for kind, ident in pages:
        if kind == "tool" and ident in index.tools_by_id:
            t = index.tools_by_id[ident]
            links.append(f'<a href="../tools/{t.identity.slug}.html">{t.identity.name}</a>')
        if kind == "task" and ident in index.tasks_by_id:
            t = index.tasks_by_id[ident]
            links.append(f'<a href="../tasks/{t.slug}.html">{t.name}</a>')
        if kind == "architecture" and ident in index.architectures_by_id:
            t = index.architectures_by_id[ident]
            links.append(f'<a href="../architectures/{t.slug}.html">{t.name}</a>')
    body = h(1, term.term) + p(nr(term.term_ru)) + p(term.definition) + h(2, "Где встречается") + (ul(links) if links else p('<span class="nr">NR</span>'))
    render_page(
        jinja, catalog, title=term.term, body=body,
        breadcrumbs=[
            {"href": "../index.html", "label": "Главная"},
            {"href": "index.html", "label": "Glossary"},
            {"href": f"{term.slug}.html", "label": term.term},
        ],
        depth=1, path=DIST / "glossary" / f"{term.slug}.html",
    )


def evidence_page(catalog: Catalog, entry: dict, jinja: Environment):
    rows = [[e["level"], e["name"]] for e in entry["evidence_scale"]]
    body = (
        h(1, "Evidence, reproducibility, benchmarks")
        + p("Правила интерпретации взяты из листа «Методика» матрицы и не смягчаются маркетинговыми формулировками.")
        + h(2, "Шкала evidence")
        + table(["Класс", "Смысл"], rows)
        + h(2, "Жёсткие правила")
        + ul(
            [
                "Preprint и workshop paper не помечаются как peer-reviewed main-track.",
                "pLDDT, PAE, ipTM, docking score, likelihood и developability score ≠ experimental affinity.",
                "Predictor, docking, MD не классифицируются как generative design.",
                "Reported Kd после phage display нельзя автоматически приписать одному generator.",
                "NR лучше, чем выдуманная полнота.",
            ]
        )
        + h(2, "Как добавлять новую evidence")
        + p("См. README: сначала primary paper, затем SI, repo, independent validation. Источник должен быть проставлен до поля.")
    )
    render_page(
        jinja, catalog, title="Evidence", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Evidence"}],
        depth=1, path=DIST / "evidence" / "index.html",
    )


def about_page(catalog: Catalog, jinja: Environment):
    dep_rows = [
        [d.name, d.role, nr(d.input_output), d.interpretation_boundary, link_or_nr(d.source)]
        for d in catalog.dependencies
    ]
    body = (
        h(1, "Scope, inclusion rules, limitations")
        + p("Сайт описывает genuinely generative ML tools для белков, антител и antibody-like therapeutics.")
        + h(2, "Что входит")
        + ul(["sequence generators", "inverse folding", "backbone / all-atom generators", "joint sequence–structure", "CDR/framework generators", "mutation/humanization workflows"])
        + h(2, "Что не входит как generator")
        + ul(["обычный structure prediction", "docking", "MD", "affinity prediction", "developability prediction — только как dependency"])
        + h(2, "Политика обновления")
        + p("Last verified матрицы: 2026-08-13. Новые инструменты добавляются YAML-файлом и проходят validate.py.")
        + h(2, "Валидаторы и внешние модули")
        + table(["Модуль", "Роль", "Input → output", "Граница интерпретации", "Source"], dep_rows)
    )
    render_page(
        jinja, catalog, title="About", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "About"}],
        depth=1, path=DIST / "about" / "index.html",
    )


def compare_page(catalog: Catalog, entry: dict, jinja: Environment):
    checks = []
    for t in catalog.tools:
        checks.append(
            f'<label><input type="checkbox" class="cmp" value="{t.identity.id}" data-group="{t.classification.compatibility_group or ""}"> {t.identity.name}</label>'
        )
    fields = [
        "id", "name", "task", "start", "generated", "modality", "family", "repr",
        "equiv", "cond", "sampling", "labels", "topology", "ab", "vhh", "mutation",
        "eval", "extval", "prospective", "license", "local", "hardware", "runtime",
    ]
    payload = []
    for t in catalog.tools:
        payload.append({
            "id": t.identity.id,
            "name": t.identity.name,
            "group": t.classification.compatibility_group,
            "task": ", ".join(t.classification.task_ids),
            "start": t.generation.required_input,
            "generated": t.generation.exact_generated_object,
            "modality": ", ".join(t.classification.output_modalities),
            "family": t.architecture.model_family,
            "repr": t.architecture.input_representation,
            "equiv": t.architecture.equivariance,
            "cond": t.architecture.conditioning_mechanism,
            "sampling": t.architecture.sampling_procedure or t.architecture.generation_mechanism,
            "labels": t.training.label_requirements,
            "topology": "yes" if t.classification.compatibility_group in {"backbone-generator", "joint-sequence-structure", "general-binder"} else "limited/no",
            "ab": "yes" if t.evidence.direct_antibody_flag else "no/transfer",
            "vhh": t.classification.vhh_relevance,
            "mutation": t.generation.support_for_single_mutations,
            "eval": t.architecture.internal_scorer,
            "extval": ", ".join(t.workflow_components.mandatory_external_dependencies),
            "prospective": "yes" if t.evidence.prospective_flag else "no",
            "license": t.identity.license,
            "local": "yes" if t.identity.official_repository else "service/NR",
            "hardware": t.inference.GPU,
            "runtime": t.inference.reported_runtime,
        })
    inc = table(["A", "B", "Почему нельзя"], [[a, b, c] for a, b, c in entry["incomparable"]])
    body = (
        h(1, "Сравнение инструментов и архитектур")
        + '<div class="warn compat-warn" id="compat-warn">Выбранные инструменты принадлежат разным compatibility groups. Их runtime и output quality нельзя сравнивать напрямую.</div>'
        + inc
        + h(2, "Выбор инструментов")
        + f'<div class="compare-list">{"".join(checks)}</div>'
        + '<div class="table-wrap"><table id="cmp-table"></table></div>'
        + f'<script>window.COMPARE_DATA = {json.dumps(payload, ensure_ascii=False)}; window.COMPARE_FIELDS = {json.dumps(fields)};</script>'
    )
    render_page(
        jinja, catalog, title="Сравнение", body=body,
        breadcrumbs=[{"href": "../index.html", "label": "Главная"}, {"href": "index.html", "label": "Сравнение"}],
        depth=1, path=DIST / "compare" / "index.html",
    )


def write_search_index(catalog: Catalog):
    items = []
    def add(kind, name, slug, href, extra=""):
        items.append({"kind": kind, "name": name, "slug": slug, "href": href, "text": f"{name} {extra}"})
    for t in catalog.tools:
        add("tool", t.identity.name, t.identity.slug, f"tools/{t.identity.slug}.html", " ".join(t.identity.aliases + [t.generation.exact_generated_object or ""]))
    for t in catalog.tasks:
        add("task", t.name, t.slug, f"tasks/{t.slug}.html", t.definition)
    for w in catalog.workflows:
        add("workflow", w.name, w.slug, f"workflows/{w.slug}.html", w.use_case)
    for a in catalog.architectures:
        add("architecture", a.name, a.slug, f"architectures/{a.slug}.html", a.name_ru)
    for ppr in catalog.papers:
        add("paper", ppr.title or ppr.id, ppr.slug, f"papers/{ppr.slug}.html", ppr.doi or "")
    for g in catalog.glossary:
        add("glossary", g.term, g.slug, f"glossary/{g.slug}.html", g.definition)
    (DIST / "static").mkdir(parents=True, exist_ok=True)
    (DIST / "static" / "search-index.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(items, ensure_ascii=False) + ";",
        encoding="utf-8",
    )


def build() -> None:
    catalog = load_catalog()
    index = build_index(catalog)
    assert_valid(catalog, index)
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copytree(STATIC, DIST / "static")
    jinja = env()
    entry = load_entry()
    homepage(catalog, index, entry, jinja)
    tasks_index(catalog, jinja)
    for task in catalog.tasks:
        task_page(catalog, index, task, jinja)
    workflows_index(catalog, jinja)
    for wf in catalog.workflows:
        workflow_page(catalog, index, wf, jinja)
    tools_index(catalog, jinja)
    for tool in catalog.tools:
        tool_page(catalog, index, tool, jinja)
    architectures_index(catalog, index, jinja)
    for arch in catalog.architectures:
        architecture_page(catalog, index, arch, jinja)
    papers_index(catalog, jinja)
    for paper in catalog.papers:
        paper_page(catalog, index, paper, jinja)
    glossary_index(catalog, jinja)
    for term in catalog.glossary:
        glossary_page(catalog, index, term, jinja)
    evidence_page(catalog, entry, jinja)
    about_page(catalog, jinja)
    compare_page(catalog, entry, jinja)
    write_search_index(catalog)
    print("built", DIST)


if __name__ == "__main__":
    build()
