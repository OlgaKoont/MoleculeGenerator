from __future__ import annotations

import html
import re
from typing import Any

from architecture_primer import canonical_section_id, primer_paragraphs, section_overview
from htmlutil import badge, esc, nr, p, table, ul


STATUS_LABEL = {
    "verified": ("verified", "peer"),
    "partially_verified": ("partially verified", "warn"),
    "paper_read": ("paper read", "src"),
    "code_inspected": ("code inspected", "src"),
    "sources_identified": ("sources identified", "src"),
    "drafted": ("drafted", "warn"),
    "not_started": ("not started", "nr"),
    "blocked": ("blocked", "warn"),
}

SOURCE_KIND = {
    "PAPER": ("[PAPER]", "paper"),
    "SI": ("[SI]", "si"),
    "CODE": ("[CODE]", "code"),
    "DOC": ("[DOC]", "doc"),
    "INDEPENDENT": ("[INDEPENDENT]", "ind"),
    "INTERPRETATION": ("[INTERPRETATION]", "interp"),
    "NR": ("NR", "nr"),
    "MATRIX": ("[MATRIX]", "nr"),
}

EVIDENCE_TYPE_RU = {
    "1": "1. только architectural rationale",
    "2": "2. retrospective benchmark",
    "3": "3. ablation evidence",
    "4": "4. prospective binding validation",
    "5": "5. prospective functional validation",
    "6": "6. developability / manufacturability",
    "7": "7. independent validation",
    "architectural rationale only": "1. только architectural rationale",
    "retrospective benchmark": "2. retrospective benchmark",
    "ablation evidence": "3. ablation evidence",
    "prospective binding validation": "4. prospective binding validation",
    "prospective functional validation": "5. prospective functional validation",
    "developability/manufacturability evidence": "6. developability / manufacturability",
    "independent validation": "7. independent validation",
}


def source_badge(kind: str | None) -> str:
    if not kind:
        return ""
    key = str(kind).strip().upper().replace("[", "").replace("]", "")
    label, css = SOURCE_KIND.get(key, (kind, "src"))
    return badge(label, css)


def research_banner(analysis: dict[str, Any] | None) -> str:
    if not analysis:
        return (
            '<div class="note research-banner">'
            + badge("not started", "nr")
            + " Глубокая верификация по primary paper / SI / code для этой страницы ещё не завершена. "
            "Короткие поля ниже могут происходить из landscape-матрицы. Неизвестное помечено как NR."
            "</div>"
        )
    status = analysis.get("research_status") or "not_started"
    label, css = STATUS_LABEL.get(status, (status, "nr"))
    date = analysis.get("last_source_check") or "NR"
    bits = [
        f'<div class="note research-banner">{badge(label, css)} '
        f"Последняя сверка источников: {esc(date)}."
    ]
    if analysis.get("status_note"):
        bits.append(" " + rich(analysis["status_note"]))
    bits.append("</div>")
    inaccessible = analysis.get("inaccessible") or []
    if inaccessible:
        rows = []
        for item in inaccessible:
            if isinstance(item, str):
                rows.append([esc(item), "", ""])
            else:
                rows.append(
                    [
                        esc(item.get("source") or "NR"),
                        esc(item.get("reason") or "NR"),
                        esc(item.get("workaround") or "NR"),
                    ]
                )
        bits.append(
            "<p><strong>Недоступные или неполные источники</strong></p>"
            + table(["Источник", "Почему недоступен", "Что использовано вместо"], rows)
        )
    return "".join(bits)


def rich(text: Any) -> str:
    """Escape text, then restore $math$, markdown links, bold, code, and root-relative HTML links."""
    if text is None:
        return '<span class="nr">NR</span>'
    s = str(text)
    if not s.strip():
        return '<span class="nr">NR</span>'
    math_slots: list[str] = []

    def hold_math(m: re.Match) -> str:
        math_slots.append(m.group(0))
        return f"@@MATH{len(math_slots) - 1}@@"

    s = re.sub(r"\$\$[\s\S]+?\$\$", hold_math, s)
    s = re.sub(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", hold_math, s)
    s = html.escape(s, quote=False)
    s = re.sub(
        r"\[([^\]]+)\]\(((\.\./|/|https?://|mailto:)[^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        s,
    )
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = s.replace("\n\n", "</p><p>")
    s = s.replace("\n", "<br>")
    for i, chunk in enumerate(math_slots):
        s = s.replace(f"@@MATH{i}@@", chunk)
    return s


def paragraph(item: Any) -> str:
    if item is None:
        return p('<span class="nr">NR</span>')
    if isinstance(item, str):
        return p(rich(item))
    text = item.get("text") or item.get("html")
    if item.get("html") and not item.get("text"):
        inner = str(item["html"])
    else:
        inner = rich(text)
    src = source_badge(item.get("source"))
    loc = f' <span class="locator">{esc(item["locator"])}</span>' if item.get("locator") else ""
    note = f' <span class="muted">{rich(item["note"])}</span>' if item.get("note") else ""
    return f"<p>{src}{inner}{loc}{note}</p>"


def render_equation(eq: dict[str, Any]) -> str:
    latex = eq.get("latex") or ""
    if latex and not latex.strip().startswith("$"):
        latex = f"$${latex}$$"
    caption = rich(eq.get("caption") or "")
    src = source_badge(eq.get("source"))
    kind = esc(eq.get("generic_or_specific") or "NR")
    symbols = eq.get("symbols") or []
    sym_html = ""
    if symbols:
        rows = []
        for s in symbols:
            if isinstance(s, dict):
                rows.append(
                    [
                        f"${esc(s.get('sym') or s.get('symbol') or '')}$",
                        esc(s.get("type") or "NR"),
                        rich(s.get("meaning") or s.get("definition") or "NR"),
                    ]
                )
            else:
                rows.append([esc(s), "", ""])
        sym_html = table(["Символ", "Тип", "Определение"], rows)
    meaning = f"<p>{rich(eq['meaning'])}</p>" if eq.get("meaning") else ""
    physical = f"<p>{rich(eq['physical'])}</p>" if eq.get("physical") else ""
    return (
        '<figure class="equation">'
        f'<div class="math">{latex}</div>'
        f"<figcaption>{src} {kind}. {caption}</figcaption>"
        f"{sym_html}{meaning}{physical}"
        "</figure>"
    )


def render_mermaid(block: dict[str, Any] | str) -> str:
    if isinstance(block, str):
        code, caption, source_note = block, "", ""
    else:
        code = block.get("code") or block.get("mermaid") or ""
        caption = block.get("caption") or ""
        source_note = block.get("source_note") or block.get("source") or ""
    if not code:
        return p('<span class="nr">NR</span>')
    return (
        '<figure class="diagram">'
        f'<pre class="mermaid">{html.escape(code)}</pre>'
        f"<figcaption>{rich(caption)}"
        + (f" <span class='muted'>Источник схемы: {esc(source_note)}</span>" if source_note else "")
        + "</figcaption></figure>"
    )


def render_simple_table(tbl: dict[str, Any]) -> str:
    headers = tbl.get("headers") or []
    rows = []
    for row in tbl.get("rows") or []:
        if isinstance(row, dict):
            rows.append([rich(row.get(h, "NR")) for h in headers])
        else:
            rows.append([rich(c) for c in row])
    caption = f"<p><em>{rich(tbl['caption'])}</em></p>" if tbl.get("caption") else ""
    src = source_badge(tbl.get("source")) if tbl.get("source") else ""
    return src + caption + table([esc(h) for h in headers], rows)


def render_physchem(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return p('<span class="nr">NR</span>')
    out = []
    for r in rows:
        out.append(
            [
                rich(r.get("feature") or r.get("operation") or "NR"),
                rich(r.get("interpretation") or "NR"),
                rich(r.get("encoded") or "NR"),
                rich(r.get("limitation") or "NR"),
            ]
        )
    return table(
        [
            "Признак или операция модели",
            "Физико-химическая интерпретация",
            "Прямо / косвенно / внешне",
            "Важное ограничение",
        ],
        out,
    )


def render_claim_evidence(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return p("Матрица claim–evidence не заполнена: <span class='nr'>NR</span>.")
    out = []
    for r in rows:
        et = r.get("evidence_type") or "NR"
        et_disp = EVIDENCE_TYPE_RU.get(str(et).strip().lower(), EVIDENCE_TYPE_RU.get(str(et).strip(), str(et)))
        out.append(
            [
                rich(r.get("claim") or "NR"),
                rich(r.get("mechanism") or r.get("proposed_mechanism") or "NR"),
                esc(et_disp),
                rich(r.get("dataset") or r.get("experiment") or "NR"),
                rich(r.get("comparator") or "NR"),
                rich(r.get("metric") or r.get("result") or "NR"),
                f"{source_badge(r.get('source'))} {esc(r.get('locator') or '')}".strip(),
                rich(r.get("caveat") or "NR"),
            ]
        )
    return table(
        [
            "Утверждение",
            "Предполагаемый механизм",
            "Тип evidence",
            "Датасет / эксперимент",
            "Comparator",
            "Метрика / результат",
            "Источник",
            "Оговорка",
        ],
        out,
        extra_class="claim-evidence",
    )


def render_modules(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return p('<span class="nr">NR</span>')
    out = [
        [
            rich(r.get("module") or "NR"),
            rich(r.get("model_class") or "NR"),
            rich(r.get("input") or "NR"),
            rich(r.get("output") or "NR"),
            rich(r.get("trained_or_frozen") or "NR"),
            rich(r.get("generator_or_evaluator") or "NR"),
        ]
        for r in rows
    ]
    return table(
        ["Модуль", "Класс модели", "Вход", "Выход", "Обучается или frozen", "Generator или evaluator"],
        out,
    )


def render_gen_vs_eval(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return p('<span class="nr">NR</span>')
    out = [
        [
            rich(r.get("component") or "NR"),
            rich(r.get("role") or "NR"),
            rich(r.get("integrated_or_external") or "NR"),
            rich(r.get("required_or_optional") or "NR"),
            rich(r.get("influences") or r.get("influences_generation_or_post_hoc") or "NR"),
        ]
        for r in rows
    ]
    return table(
        [
            "Компонент",
            "Роль",
            "Integrated или external",
            "Required или optional",
            "Влияет на generation или только ранжирует после",
        ],
        out,
    )


def render_paper_vs_code(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    out = [
        [
            rich(r.get("paper_version") or "NR"),
            rich(r.get("repo_commit") or "NR"),
            rich(r.get("model_version") or "NR"),
            rich(r.get("file") or "NR"),
            rich(r.get("difference") or "NR"),
            rich(r.get("consequence") or "NR"),
        ]
        for r in rows
    ]
    return (
        '<h3 id="paper-vs-code">Различия между статьёй и реализацией</h3>'
        + table(
            [
                "Версия статьи",
                "Commit репозитория",
                "Checkpoint / model",
                "Файл",
                "Различие",
                "Практическое следствие",
            ],
            out,
        )
    )


def render_citations(items: list[dict[str, Any]]) -> str:
    if not items:
        return p('<span class="nr">NR</span>')
    lis = []
    for i, c in enumerate(items, 1):
        ident = c.get("id") or i
        text = rich(c.get("text") or c.get("citation") or "NR")
        url = c.get("url")
        doi = c.get("doi")
        links = []
        if doi:
            href = doi if str(doi).startswith("http") else f"https://doi.org/{doi}"
            links.append(f'<a href="{esc(href)}" rel="noopener">DOI</a>')
        if url:
            links.append(f'<a href="{esc(url)}" rel="noopener">источник</a>')
        extra = (" · " + " · ".join(links)) if links else ""
        lis.append(f"<li id=\"ref-{esc(ident)}\">[{esc(ident)}] {text}{extra}</li>")
    return "<ol class='refs'>" + "".join(lis) + "</ol>"


def _class_overview_text(section: dict[str, Any], arch: Any) -> str | None:
    """YAML class_overview / overview overrides the auto class blurb; False disables it."""
    if not arch:
        return None
    if "class_overview" in section:
        raw = section["class_overview"]
        if raw is False or raw is None:
            return None
        if isinstance(raw, dict):
            text = raw.get("text") or ""
            return text.strip() or None
        text = str(raw).strip()
        return text or None
    if section.get("overview"):
        ov = section["overview"]
        if isinstance(ov, dict):
            return (ov.get("text") or "").strip() or None
        text = str(ov).strip()
        return text or None
    return section_overview(arch, canonical_section_id(section) or "")


def render_section(
    section: dict[str, Any],
    *,
    arch: Any = None,
    inject_class_overview: bool = False,
) -> str:
    title = section.get("title") or section.get("id") or "Раздел"
    ident = section.get("id") or re.sub(r"[^a-z0-9а-яё]+", "-", title.lower())[:80]
    try:
        level = int(section.get("level") or 2)
    except (TypeError, ValueError):
        level = 2
    level = min(max(level, 2), 4)
    parts = [f'<h{level} id="{esc(ident)}">{esc(title)}</h{level}>']
    if inject_class_overview:
        overview = _class_overview_text(section, arch)
        if overview:
            parts.append(
                '<div class="class-overview">'
                '<p class="class-overview-label">Общее для класса</p>'
                f"<p>{rich(overview)}</p>"
                "</div>"
            )
    if section.get("lede"):
        parts.append(paragraph(section["lede"]))
    for para in section.get("paragraphs") or []:
        parts.append(paragraph(para))
    for eq in section.get("equations") or []:
        parts.append(render_equation(eq))
    for tbl in section.get("tables") or []:
        parts.append(render_simple_table(tbl))
    for diag in section.get("diagrams") or []:
        parts.append(render_mermaid(diag))
    if section.get("mermaid"):
        parts.append(render_mermaid({"code": section["mermaid"], "caption": section.get("mermaid_caption"), "source_note": section.get("mermaid_source")}))
    if section.get("physchem"):
        parts.append(render_physchem(section["physchem"]))
    if section.get("modules"):
        parts.append(render_modules(section["modules"]))
    if section.get("claim_evidence"):
        parts.append(render_claim_evidence(section["claim_evidence"]))
    if section.get("gen_vs_eval"):
        parts.append(render_gen_vs_eval(section["gen_vs_eval"]))
    if section.get("items"):
        parts.append(ul([rich(x) for x in section["items"]]))
    if section.get("nr_fields"):
        parts.append(
            "<p>Поля NR: "
            + ", ".join(f"<code>{esc(x)}</code>" for x in section["nr_fields"])
            + "</p>"
        )
    for nested in section.get("sections") or []:
        parts.append(render_section(nested, arch=arch, inject_class_overview=False))
    return "".join(parts)


def render_sources_block(analysis: dict[str, Any]) -> str:
    sources = analysis.get("sources") or []
    repo = analysis.get("repo") or {}
    parts = []
    if sources:
        rows = []
        for s in sources:
            rows.append(
                [
                    source_badge(s.get("kind") or s.get("source")),
                    rich(s.get("citation") or s.get("text") or "NR"),
                    (
                        f'<a href="{esc(s["url"])}" rel="noopener">{esc(s.get("url_label") or s["url"])}</a>'
                        if s.get("url")
                        else '<span class="nr">NR</span>'
                    ),
                    rich(s.get("note") or ""),
                ]
            )
        parts.append(table(["Метка", "Источник", "Ссылка", "Примечание"], rows))
    if repo:
        files = repo.get("files") or []
        file_html = ul([f"<code>{esc(f)}</code>" for f in files]) if files else p('<span class="nr">NR</span>')
        parts.append(
            table(
                ["Поле", "Значение"],
                [
                    ["Репозиторий", f'<a href="{esc(repo.get("url") or "")}" rel="noopener">{esc(repo.get("url") or "NR")}</a>' if repo.get("url") else nr(None)],
                    ["Commit", f"<code>{esc(repo.get('commit') or 'NR')}</code>"],
                    ["Ветка / tag", esc(repo.get("ref") or "NR")],
                    ["Лицензия", esc(repo.get("license") or "NR")],
                ],
            )
        )
        parts.append("<p>Проверенные файлы реализации:</p>" + file_html)
    return "".join(parts)


def _analysis_extra_blocks(analysis: dict[str, Any], *, include_paper_vs_code: bool = True) -> str:
    parts: list[str] = []
    if analysis.get("physchem_table"):
        parts.append('<h2 id="physchem">Физико-химический смысл</h2>')
        parts.append(render_physchem(analysis["physchem_table"]))
    if analysis.get("modules"):
        parts.append('<h2 id="modules">Модульная схема</h2>')
        parts.append(render_modules(analysis["modules"]))
    if analysis.get("gen_vs_eval"):
        parts.append('<h2 id="gen-vs-eval">Generator versus evaluator</h2>')
        parts.append(render_gen_vs_eval(analysis["gen_vs_eval"]))
    if analysis.get("claim_evidence"):
        parts.append('<h2 id="claim-evidence">Claim–evidence matrix</h2>')
        parts.append(render_claim_evidence(analysis["claim_evidence"]))
    if include_paper_vs_code and analysis.get("paper_vs_code"):
        parts.append(render_paper_vs_code(analysis["paper_vs_code"]))
    if analysis.get("diagrams"):
        parts.append('<h2 id="diagrams">Схемы information flow</h2>')
        for d in analysis["diagrams"]:
            parts.append(render_mermaid(d))
    return "".join(parts)


def _primer_texts(arch: Any, analysis: dict[str, Any] | None) -> list[str]:
    raw = (analysis or {}).get("primer")
    texts: list[str] = []
    if isinstance(raw, str) and raw.strip():
        texts.append(raw.strip())
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str) and item.strip():
                texts.append(item.strip())
            elif isinstance(item, dict) and (item.get("text") or "").strip():
                texts.append(item["text"].strip())
    if texts:
        return texts
    return primer_paragraphs(arch) if arch else []


def render_architecture_primer(arch: Any, analysis: dict[str, Any] | None) -> str:
    texts = _primer_texts(arch, analysis)
    if not texts:
        return ""
    parts = [
        '<section class="primer" id="primer">',
        "<h2>Что это за класс</h2>",
        '<p class="muted">Определение класса — общее для всех papers и tools с этим architecture_id. '
        "Это не карточка одной нейросети. После каждого нумерованного заголовка сначала идёт блок "
        "«Общее для класса», затем разбор конкретных статей, как раньше.</p>",
    ]
    for text in texts:
        parts.append(f"<p>{rich(text)}</p>")
    parts.append("</section>")
    return "".join(parts)


def render_architecture_main(analysis: dict[str, Any] | None, arch: Any) -> str:
    """Class primer + 18 sections. Research status / provenance live in the appendix."""
    if not analysis:
        analysis = architecture_fallback(arch) if arch else {}
    parts = [render_architecture_primer(arch, analysis)]
    if analysis.get("lede"):
        parts.append('<div class="arch-lede">' + p(rich(analysis["lede"])) + "</div>")
    for section in analysis.get("sections") or []:
        parts.append(render_section(section, arch=arch, inject_class_overview=True))
    parts.append(_analysis_extra_blocks(analysis, include_paper_vs_code=False))
    return "".join(parts)


def render_architecture_appendix(analysis: dict[str, Any] | None) -> str:
    """Status banner, paywall/inaccessible table, source provenance — end of the architecture page."""
    parts = [
        '<section class="research-appendix" id="research-status">',
        "<h2>Статус сверки источников</h2>",
        research_banner(analysis),
    ]
    if analysis and (analysis.get("sources") or analysis.get("repo")):
        parts.append('<h2 id="provenance">Происхождение источников</h2>')
        parts.append(render_sources_block(analysis))
    if analysis and analysis.get("paper_vs_code"):
        parts.append(render_paper_vs_code(analysis["paper_vs_code"]))
    if analysis and analysis.get("citations"):
        parts.append('<h2 id="refs">Методологические источники</h2>')
        parts.append(render_citations(analysis["citations"]))
    unresolved = (analysis or {}).get("unresolved") or []
    if unresolved:
        parts.append('<h2 id="unresolved">Нерешённые научные вопросы</h2>')
        parts.append(ul([rich(x) for x in unresolved]))
    parts.append("</section>")
    return "".join(parts)


def render_analysis(analysis: dict[str, Any] | None, *, kind: str = "page", arch: Any = None) -> str:
    if kind == "architecture":
        return render_architecture_main(analysis, arch) + render_architecture_appendix(analysis)
    if not analysis:
        return research_banner(None)
    parts = [research_banner(analysis)]
    if analysis.get("lede"):
        parts.append(p(rich(analysis["lede"])))
    if analysis.get("sources") or analysis.get("repo"):
        parts.append('<h2 id="provenance">Происхождение источников</h2>')
        parts.append(render_sources_block(analysis))
    for section in analysis.get("sections") or []:
        parts.append(render_section(section))
    parts.append(_analysis_extra_blocks(analysis))
    if analysis.get("citations"):
        parts.append('<h2 id="refs">Источники</h2>')
        parts.append(render_citations(analysis["citations"]))
    unresolved = analysis.get("unresolved") or []
    if unresolved:
        parts.append('<h2 id="unresolved">Нерешённые научные вопросы</h2>')
        parts.append(ul([rich(x) for x in unresolved]))
    return "".join(parts)


def architecture_fallback(arch) -> dict[str, Any]:
    """Honest 18-section skeleton from existing short fields. Not a claim of paper reading."""
    return {
        "research_status": "not_started",
        "last_source_check": "2026-08-27",
        "status_note": (
            "Классовое описание собрано из канонических коротких полей сайта. "
            "Primary papers, SI и реализации инструментов для этой страницы ещё не прочитаны "
            "в режиме выпуска 10. Уравнения ниже — **родовые** для класса, не tool-specific, "
            "пока не указано иное."
        ),
        "lede": f"**{arch.name}** / {arch.name_ru}.",
        "sections": [
            {
                "id": "domain",
                "title": "1. Область определения",
                "paragraphs": [
                    {
                        "text": arch.intuition,
                        "source": "MATRIX",
                        "locator": "seed architecture YAML",
                    },
                    {
                        "text": (
                            "Это страница **класса методов**, а не одного нейросетевого checkpoint. "
                            "Конкретный инструмент может реализовать только подмножество механизма."
                        ),
                        "source": "INTERPRETATION",
                    },
                ],
            },
            {
                "id": "intuition",
                "title": "2. Интуитивный принцип",
                "paragraphs": [{"text": arch.intuition, "source": "MATRIX"}],
            },
            {
                "id": "math",
                "title": "3. Формальная математическая постановка",
                "paragraphs": [
                    {
                        "text": (
                            "Формула ниже взята из seed-описания класса. Она **не** должна читаться "
                            "как уравнение конкретного инструмента, пока страница не помечена verified."
                        ),
                        "source": "INTERPRETATION",
                    }
                ],
                "equations": (
                    [
                        {
                            "latex": arch.mathematical_formulation,
                            "caption": "Родовая запись класса (seed).",
                            "generic_or_specific": "generic",
                            "source": "MATRIX",
                        }
                    ]
                    if arch.mathematical_formulation
                    else []
                ),
                "nr_fields": ["tool-specific update equations"] if not arch.mathematical_formulation else [],
            },
            {
                "id": "data-repr",
                "title": "4. Представление данных",
                "paragraphs": [{"text": arch.input_representation or "NR", "source": "MATRIX"}],
            },
            {
                "id": "physical-repr",
                "title": "5. Физическое представление",
                "paragraphs": [
                    {
                        "text": (
                            f"Generated state в seed: {arch.generated_state or 'NR'}. "
                            "Координаты, frames или embeddings **не** равны энергии взаимодействия."
                        ),
                        "source": "INTERPRETATION",
                    }
                ],
            },
            {
                "id": "physchem",
                "title": "6. Физико-химический смысл",
                "paragraphs": [
                    {
                        "text": (
                            "Пока primary paper не разобран, таблица не заполняется вымышленными "
                            "тензорными размерностями и не утверждает, что модель «считает химию»."
                        ),
                        "source": "NR",
                    }
                ],
            },
            {
                "id": "learned",
                "title": "7. Что обучается",
                "paragraphs": [{"text": arch.training_objective or "NR", "source": "MATRIX"}],
            },
            {
                "id": "forward",
                "title": "8. Прямой проход и information flow",
                "paragraphs": [
                    {
                        "text": "Детальный forward pass для этого класса будет добавлен после чтения implementation files.",
                        "source": "NR",
                    }
                ],
            },
            {
                "id": "training",
                "title": "9. Training procedure",
                "paragraphs": [{"text": arch.training_objective or "NR", "source": "MATRIX"}],
                "nr_fields": ["split", "filtering", "augmentation", "leakage audit"],
            },
            {
                "id": "inference",
                "title": "10. Inference and generation",
                "paragraphs": [{"text": arch.inference or "NR", "source": "MATRIX"}],
            },
            {
                "id": "conditioning",
                "title": "11. Conditioning",
                "paragraphs": [{"text": arch.conditioning or "NR", "source": "MATRIX"}],
            },
            {
                "id": "complexity",
                "title": "12. Вычислительная сложность",
                "items": arch.complexity_drivers or ["NR"],
            },
            {
                "id": "strengths",
                "title": "13. Преимущества",
                "paragraphs": [
                    {
                        "text": "Преимущества seed-списка нужно привязывать к механизму после чтения papers. Пока это авторские/обзорные формулировки матрицы, не ablation.",
                        "source": "INTERPRETATION",
                    }
                ],
                "items": arch.strengths or ["NR"],
            },
            {
                "id": "limits",
                "title": "14. Ограничения",
                "items": arch.limitations or ["NR"],
            },
            {
                "id": "failures",
                "title": "15. Failure modes",
                "items": arch.failure_modes or ["NR"],
            },
            {
                "id": "tools",
                "title": "16. Реализации в инструментах",
                "paragraphs": [
                    {
                        "text": "Список инструментов рендерится из reverse index каталога. Различие generic vs tool-specific — на страницах инструментов.",
                        "source": "INTERPRETATION",
                    }
                ],
            },
            {
                "id": "applicability",
                "title": "17. Где применимо и где не применимо",
                "paragraphs": [
                    {
                        "text": "См. блоки задач ниже на этой странице (ссылки из YAML).",
                        "source": "MATRIX",
                    }
                ],
            },
            {
                "id": "method-sources",
                "title": "18. Методологические источники",
                "paragraphs": [
                    {
                        "text": "Связанные papers каталога перечислены внизу страницы. Пока статус not_started, эти ссылки — идентификаторы, а не отчёт о полном чтении.",
                        "source": "NR",
                    }
                ],
            },
        ],
    }


def tool_fallback(tool) -> dict[str, Any]:
    gen = tool.generation
    arch = tool.architecture
    ev = tool.evidence
    return {
        "research_status": "sources_identified" if tool.relations.paper_ids else "not_started",
        "last_source_check": "2026-08-27",
        "status_note": (
            "Ниже — каркас обязательных разделов, заполненный из канонического YAML инструмента. "
            "Это **не** замена чтения primary paper / SI / model files. Поля без первоисточника помечены NR или MATRIX."
        ),
        "sections": [
            {
                "id": "what",
                "title": "1. Что именно делает инструмент",
                "paragraphs": [
                    {"text": f"**Вход:** {gen.required_input or 'NR'}", "source": "MATRIX"},
                    {"text": f"**Generated object:** {gen.exact_generated_object}", "source": "MATRIX"},
                    {"text": f"**Фиксируется:** {gen.fixed_components or 'NR'}. **Изменяется:** {gen.editable_components or 'NR'}.", "source": "MATRIX"},
                    {"text": f"**De novo или parent-based:** {tool.classification.de_novo_or_optimization or 'NR'}.", "source": "MATRIX"},
                ],
            },
            {
                "id": "arch-para",
                "title": "2. Архитектура в одном абзаце",
                "paragraphs": [
                    {
                        "text": arch.generation_mechanism or arch.model_family or arch.base_model or "NR",
                        "source": "MATRIX",
                    }
                ],
            },
            {
                "id": "math-model",
                "title": "4. Математическая модель",
                "paragraphs": [
                    {
                        "text": "Точные уравнения, losses и sampling solver будут внесены после чтения paper/code. Не подставляйте родовой UCB/transformer/diffusion, если он не подтверждён для этого инструмента.",
                        "source": "NR",
                    }
                ],
                "nr_fields": ["conditional probability", "update equations", "sampling algorithm"],
            },
            {
                "id": "physical-state",
                "title": "5. Физическое устройство состояния",
                "paragraphs": [
                    {
                        "text": f"Seed generated state / output: {arch.output or gen.exact_generated_object}. Structure generation: {arch.structure_generation or 'NR'}.",
                        "source": "MATRIX",
                    }
                ],
            },
            {
                "id": "physchem",
                "title": "6. Физико-химическая интерпретация",
                "paragraphs": [
                    {
                        "text": "Координаты, frames, PLM embeddings или residue tokens **не** являются расчётом ΔG, электростатики или растворителя, пока это не сделано внешней energy function. Likelihood / pLDDT / docking score ≠ экспериментальный binding.",
                        "source": "INTERPRETATION",
                    }
                ],
            },
            {
                "id": "training",
                "title": "7. Training",
                "paragraphs": [
                    {"text": f"Данные: {tool.training.training_data or 'NR'}. Fine-tuning: {tool.training.fine_tuning or 'NR'}. Negative examples: {tool.training.negative_examples or 'NR'}.", "source": "MATRIX"}
                ],
            },
            {
                "id": "inference-sec",
                "title": "8. Inference",
                "paragraphs": [
                    {"text": f"Sampling: {arch.sampling_procedure or 'NR'}. Generation steps: {tool.inference.generation_steps or 'NR'}. Runtime boundary: {tool.inference.runtime_boundary or 'NR'}.", "source": "MATRIX"}
                ],
            },
            {
                "id": "why",
                "title": "10. Почему, по мнению авторов, метод эффективен",
                "paragraphs": [
                    {"text": f"**Author-reported summary (матрица):** {ev.evidence_summary or 'NR'}", "source": "MATRIX"},
                    {
                        "text": "Causal support не классифицирован, пока не прочитаны ablation и experimental sections.",
                        "source": "NR",
                    },
                ],
            },
            {
                "id": "ablation",
                "title": "12. Ablation analysis",
                "paragraphs": [{"text": "Ablation в этом выпуске не разобрана.", "source": "NR"}],
            },
            {
                "id": "absent",
                "title": "13. What the model does not represent",
                "items": [
                    "Явный растворитель и ионная сила — обычно отсутствуют в генераторе.",
                    "Протонирование, гликозилирование, кофакторы — обычно отсутствуют, если не оговорено.",
                    "Конформационная энтропия и долгая динамика — не моделируются одним forward pass.",
                    "Экспрессия, агрегация, иммуногенность — не равны likelihood генератора.",
                    "Истинная binding free energy — не равна internal score.",
                ],
            },
            {
                "id": "evidence-lim",
                "title": "14. Evidence and limitations",
                "paragraphs": [
                    {"text": f"Evidence class (матрица): {ev.evidence_level or 'NR'}. Prospective binding: {ev.prospective_binding_validation or 'NR'}. Function: {ev.prospective_functional_validation or 'NR'}. Developability: {ev.developability_validation or 'NR'}.", "source": "MATRIX"}
                ],
                "items": tool.limitations.scientific_limitations or ["NR"],
            },
            {
                "id": "repro",
                "title": "15. Reproducibility",
                "paragraphs": [
                    {"text": f"Репозиторий: {tool.identity.official_repository or 'NR'}. Лицензия: {tool.identity.license or 'NR'}. Commit: NR, пока страница не имеет отдельного analysis YAML.", "source": "NR"}
                ],
            },
        ],
        "modules": [
            {
                "module": c.name,
                "model_class": c.architecture_class or "NR",
                "input": "NR",
                "output": "NR",
                "trained_or_frozen": "NR",
                "generator_or_evaluator": c.role,
            }
            for c in tool.workflow_components.breakdown
        ],
        "gen_vs_eval": [
            {
                "component": c.name,
                "role": c.role,
                "integrated_or_external": c.integrated_or_external,
                "required_or_optional": c.required_or_optional,
                "influences": c.influences_generation_or_post_hoc,
            }
            for c in tool.workflow_components.breakdown
        ],
        "claim_evidence": [
            {
                "claim": ev.evidence_summary or "NR",
                "mechanism": arch.generation_mechanism or "NR",
                "evidence_type": "retrospective benchmark" if not ev.prospective_flag else "prospective functional validation",
                "dataset": ev.tested_design_count or "NR",
                "comparator": "NR",
                "metric": ev.success_criterion or "NR",
                "source": "MATRIX",
                "locator": "landscape matrix 2026-08-13",
                "caveat": "Не читать как полный разбор primary paper.",
            }
        ],
    }


def paper_fallback(paper) -> dict[str, Any]:
    return {
        "research_status": "sources_identified" if paper.doi or paper.url else "not_started",
        "last_source_check": "2026-08-27",
        "status_note": (
            "Библиографические поля заполнены из каталога. Полный текст / SI для этой статьи "
            "не отмечен как прочитанный, если нет отдельного analysis YAML."
        ),
        "sections": [
            {
                "id": "question",
                "title": "Исследовательский вопрос",
                "paragraphs": [{"text": paper.main_task or "NR", "source": "MATRIX"}],
            },
            {
                "id": "claims-support",
                "title": "Утверждения и поддержка evidence",
                "paragraphs": [
                    {"text": f"**Claimed novelty:** {paper.claimed_novelty or 'NR'}", "source": "MATRIX"},
                    {"text": "Статья не «доказывает» общее преимущество метода вне своего экспериментального дизайна.", "source": "INTERPRETATION"},
                ],
            },
            {
                "id": "unsupported",
                "title": "Что представленный evidence не поддерживает",
                "items": paper.does_not_demonstrate or ["NR"],
            },
            {
                "id": "author-limits",
                "title": "Ограничения, признанные авторами",
                "paragraphs": [{"text": paper.limitations or "NR", "source": "MATRIX"}],
            },
            {
                "id": "extra-limits",
                "title": "Дополнительные ограничения интерпретации",
                "paragraphs": [
                    {
                        "text": "Пока Methods/SI не прочитаны, нельзя утверждать split leakage, точные гиперпараметры и полноту ablation.",
                        "source": "NR",
                    }
                ],
            },
        ],
    }


_TAG_RE = re.compile(r"</?(strong|em|a |code|span|ul|li|br)", re.I)
_SRC_RE = re.compile(r"\[(PAPER|SI|CODE|DOC|INDEPENDENT|INTERPRETATION|NR|MATRIX)\]")


def _para_from_text(text: str, source: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {}
    raw = text or ""
    if _TAG_RE.search(raw):
        item["html"] = raw
    else:
        item["text"] = raw
    found = _SRC_RE.search(raw)
    if found:
        item["source"] = found.group(1)
    elif source:
        item["source"] = source
    return item


def _convert_research_section(sec: dict[str, Any]) -> dict[str, Any]:
    title = sec.get("title") or sec.get("id") or "Раздел"
    ident = sec.get("id") or re.sub(r"[^a-z0-9а-яё]+", "-", str(title).lower())[:80]
    out: dict[str, Any] = {
        "id": ident,
        "title": title,
        "level": sec.get("level") or 2,
        "paragraphs": [],
        "equations": [],
        "tables": [],
        "items": [],
        "sections": [],
        "diagrams": [],
    }
    for block in sec.get("blocks") or []:
        if not isinstance(block, dict):
            continue
        typ = block.get("type")
        if typ == "p":
            out["paragraphs"].append(_para_from_text(block.get("text") or "", block.get("source")))
        elif typ == "warn":
            out["paragraphs"].append(
                _para_from_text(block.get("text") or "", block.get("source") or "INTERPRETATION")
            )
        elif typ == "math":
            out["equations"].append(
                {
                    "latex": block.get("latex") or "",
                    "caption": block.get("caption") or "",
                    "source": block.get("source"),
                    "generic_or_specific": block.get("generic_or_specific") or "generic",
                    "meaning": block.get("meaning"),
                }
            )
        elif typ == "ul":
            out["items"].extend(block.get("items") or [])
        elif typ == "table":
            out["tables"].append(
                {
                    "headers": block.get("headers") or [],
                    "rows": block.get("rows") or [],
                    "caption": block.get("caption"),
                    "source": block.get("source"),
                }
            )
        elif typ in {"mermaid", "diagram"} or block.get("mermaid"):
            out["diagrams"].append(
                {
                    "code": block.get("code") or block.get("mermaid") or "",
                    "caption": block.get("caption") or "",
                    "source_note": block.get("source") or block.get("source_note") or "",
                }
            )
        elif "title" in block and "blocks" in block:
            out["sections"].append(_convert_research_section(block))
    return out


def convert_research(data: dict[str, Any] | None) -> dict[str, Any]:
    """Map content/research block YAML onto the analysis schema used by render_analysis."""
    if not data:
        return {}
    if data.get("research_status") or data.get("lede") or data.get("claim_evidence") or data.get("physchem_table"):
        sections = data.get("sections") or []
        if sections and isinstance(sections[0], dict) and "blocks" not in sections[0]:
            return data
    out: dict[str, Any] = {
        "research_status": data.get("status") or data.get("research_status") or "not_started",
        "last_source_check": data.get("last_reviewed") or data.get("last_source_check"),
        "status_note": data.get("status_note")
        or "Текст перенесён из `content/research` (block YAML). Provenance-метки в абзацах сохранены, если они были в исходнике.",
        "inaccessible": data.get("inaccessible") or [],
        "sources": data.get("sources") or [],
        "repo": data.get("repo") or {},
        "sections": [_convert_research_section(sec) for sec in (data.get("sections") or []) if isinstance(sec, dict)],
        "citations": data.get("citations") or data.get("refs") or [],
        "unresolved": data.get("unresolved") or [],
    }
    for key in (
        "physchem_table",
        "modules",
        "gen_vs_eval",
        "claim_evidence",
        "paper_vs_code",
        "diagrams",
        "lede",
    ):
        if data.get(key):
            out[key] = data[key]
    return out


def is_substantive_research(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    status = str(data.get("status") or data.get("research_status") or "").lower()
    if status in {"verified", "partially_verified", "paper_read", "code_inspected", "drafted"}:
        return True
    sections = data.get("sections") or []
    return len(sections) >= 5
