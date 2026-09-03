from __future__ import annotations

import html
import re
from typing import Any

from schema import display, is_nr


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def nr(value: Any) -> str:
    if is_nr(value):
        return '<span class="nr">NR</span>'
    if isinstance(value, list):
        if not value:
            return '<span class="nr">NR</span>'
        return "; ".join(nr(v) for v in value)
    return esc(value)


def badge(text: str, kind: str) -> str:
    return f'<span class="badge badge-{kind}">{esc(text)}</span>'


def pub_badges(status: str | None, preprint: bool = False) -> str:
    bits = []
    st = status or ""
    low = st.lower()
    if preprint or "preprint" in low:
        bits.append(badge("Preprint", "preprint"))
    if "peer-reviewed" in low or "peer reviewed" in low:
        bits.append(badge("Peer-reviewed", "peer"))
    if "workshop" in low:
        bits.append(badge("Workshop — не main track", "warn"))
    if "technical report" in low:
        bits.append(badge("Technical report", "warn"))
    if not bits:
        bits.append(badge("Publication: NR" if not st else st[:48], "nr"))
    return " ".join(bits)


def src_badge(label: str) -> str:
    return badge(label, "src")


def link_or_nr(url: str | None, label: str | None = None) -> str:
    if is_nr(url):
        return '<span class="nr">NR</span>'
    text = label or url
    return f'<a href="{esc(url)}" rel="noopener">{esc(text)}</a>'


def doi_link(doi: str | None) -> str:
    if is_nr(doi):
        return '<span class="nr">NR</span>'
    if str(doi).startswith("http"):
        return link_or_nr(doi, doi)
    return f'<a href="https://doi.org/{esc(doi)}" rel="noopener">{esc(doi)}</a>'


def github_link(url: str | None) -> str:
    if is_nr(url):
        return '<span class="nr">NR</span>'
    return link_or_nr(url, url)


def table(headers: list[str], rows: list[list[str]], extra_class: str = "") -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
    cls = f' class="{extra_class}"' if extra_class else ""
    return (
        f'<div class="table-wrap"><table{cls}><thead><tr>{head}</tr></thead>'
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


def slugify_heading(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9а-яё]+", "-", s, flags=re.I)
    return s.strip("-")[:80]


def headings_toc(html_body: str) -> str:
    items = []
    for m in re.finditer(r"<h([2-4]) id=\"([^\"]+)\">([^<]+)</h", html_body):
        level, ident, text = m.group(1), m.group(2), m.group(3)
        pad = "" if level == "2" else (" padding-left:12px;" if level == "3" else " padding-left:20px;")
        items.append(f'<a style="{pad}" href="#{ident}">{text}</a>')
    return "".join(items) if items else "<p class='nr'>Нет подразделов</p>"


def h(level: int, text: str) -> str:
    ident = slugify_heading(text)
    return f'<h{level} id="{ident}">{esc(text)}</h{level}>'


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    if not items:
        return '<p class="nr">NR</p>'
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def card_grid(cards: list[tuple[str, str, str]]) -> str:
    parts = []
    for href, title, body in cards:
        parts.append(
            f'<a class="card" href="{href}"><h3>{esc(title)}</h3><p>{esc(body)}</p></a>'
        )
    return '<div class="grid-cards">' + "".join(parts) + "</div>"
