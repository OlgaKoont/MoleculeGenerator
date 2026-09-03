from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from schema import Catalog


@dataclass
class ReverseIndex:
    tools_by_id: dict
    tasks_by_id: dict
    workflows_by_id: dict
    architectures_by_id: dict
    papers_by_id: dict
    glossary_by_id: dict
    deps_by_id: dict
    tools_for_task: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    workflows_for_task: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    tools_for_workflow: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    tools_for_architecture: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    tools_for_paper: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    papers_for_tool: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    architectures_for_tool: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    tasks_for_tool: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    workflows_for_tool: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    glossary_pages: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))


def build_index(catalog: Catalog) -> ReverseIndex:
    idx = ReverseIndex(
        tools_by_id={t.identity.id: t for t in catalog.tools},
        tasks_by_id={t.id: t for t in catalog.tasks},
        workflows_by_id={w.id: w for w in catalog.workflows},
        architectures_by_id={a.id: a for a in catalog.architectures},
        papers_by_id={p.id: p for p in catalog.papers},
        glossary_by_id={g.id: g for g in catalog.glossary},
        deps_by_id={d.id: d for d in catalog.dependencies},
    )
    for tool in catalog.tools:
        tid = tool.identity.id
        for task_id in tool.classification.task_ids:
            idx.tools_for_task[task_id].append(tid)
            idx.tasks_for_tool[tid].append(task_id)
        for wf_id in tool.classification.workflow_ids:
            idx.tools_for_workflow[wf_id].append(tid)
            idx.workflows_for_tool[tid].append(wf_id)
        for arch_id in tool.classification.architecture_ids:
            idx.tools_for_architecture[arch_id].append(tid)
            idx.architectures_for_tool[tid].append(arch_id)
        for paper_id in tool.relations.paper_ids:
            idx.tools_for_paper[paper_id].append(tid)
            idx.papers_for_tool[tid].append(paper_id)
        for gid in tool.relations.glossary_ids:
            idx.glossary_pages[gid].append(("tool", tid))
    for task in catalog.tasks:
        for wf_id in task.workflow_ids:
            if task.id not in idx.workflows_for_task[wf_id]:
                idx.workflows_for_task[task.id].append(wf_id)
        for gid in task.glossary_ids:
            idx.glossary_pages[gid].append(("task", task.id))
    for wf in catalog.workflows:
        for task_id in wf.task_ids:
            if wf.id not in idx.workflows_for_task[task_id]:
                idx.workflows_for_task[task_id].append(wf.id)
        for tool_id in wf.tool_ids:
            if tool_id not in idx.tools_for_workflow[wf.id]:
                idx.tools_for_workflow[wf.id].append(tool_id)
            if wf.id not in idx.workflows_for_tool[tool_id]:
                idx.workflows_for_tool[tool_id].append(wf.id)
        for arch_id in wf.architecture_ids:
            if wf.id not in [x for x in idx.tools_for_architecture[arch_id]]:
                pass
        for gid in []:
            pass
    for arch in catalog.architectures:
        for gid in arch.glossary_ids:
            idx.glossary_pages[gid].append(("architecture", arch.id))
    return idx
