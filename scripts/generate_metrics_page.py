#!/usr/bin/env python3
"""Generiert docs/agent-ops/engineering-metrics.md aus metrics.json.

Aufruf (normalerweise via CI):
  python scripts/generate_metrics_page.py --input /tmp/metrics.json --output docs/agent-ops/engineering-metrics.md
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _bar(value: float, max_val: float, width: int = 20) -> str:
    if max_val <= 0:
        return ""
    filled = int(round(value / max_val * width))
    return "█" * filled + "░" * (width - filled)


def generate(metrics: dict) -> str:
    gen = metrics.get("generated_at", "")[:10]
    since = metrics.get("since", "alle")
    total = metrics.get("total_slices", 0)
    completed = metrics.get("completed_slices", 0)
    ext_gates = metrics.get("slices_with_external_gates", 0)
    no_doc = metrics.get("slices_without_doc_files", 0)
    median_ct = metrics.get("median_cycle_time_hours")
    p90_ct = metrics.get("p90_cycle_time_hours")
    rework = metrics.get("overall_rework_rate", 0)
    agent_counts: dict[str, int] = metrics.get("agent_commit_counts", {})
    details: list[dict] = metrics.get("slice_details", [])

    completion_pct = round(completed / total * 100) if total else 0
    rework_pct = round(rework * 100, 1)
    median_str = f"{median_ct:.1f} h" if median_ct is not None else "n/a"
    p90_str = f"{p90_ct:.1f} h" if p90_ct is not None else "n/a"

    # Top-Rework-Slices
    rework_slices = sorted(
        [d for d in details if d.get("rework_commits", 0) > 0],
        key=lambda d: -d["rework_commits"]
    )[:5]

    # Langläufer (>= P90)
    longrunners = []
    if p90_ct:
        longrunners = sorted(
            [d for d in details if (d.get("cycle_time_hours") or 0) >= p90_ct],
            key=lambda d: -(d.get("cycle_time_hours") or 0)
        )[:5]

    # Agent-Tabelle
    max_count = max(agent_counts.values()) if agent_counts else 1
    agent_rows = "\n".join(
        f"| {owner} | {count} | `{_bar(count, max_count)}` |"
        for owner, count in agent_counts.items()
    )

    rework_rows = "\n".join(
        f"| `{d['slice_id']}` | {d['rework_commits']} | {d.get('owner', '—')} |"
        for d in rework_slices
    ) or "| — | — | — |"

    longrunner_rows = "\n".join(
        f"| `{d['slice_id']}` | {d.get('cycle_time_hours', 0):.1f} h | {d.get('owner', '—')} |"
        for d in longrunners
    ) or "| — | — | — |"

    slices_without_ct = sum(1 for d in details if d.get("cycle_time_hours") is None)

    return f"""---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: {gen}
version: 3.0.0
generated: {gen}
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `{since}` · Stand: `{gen}`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **{total}** |
| Slices abgeschlossen | **{completed}** ({completion_pct} %) |
| Mit externen Gates | {ext_gates} |
| Ohne Doku-Dateien | {no_doc} |
| Slices ohne Cycle-Time (kein Claim-Commit) | {slices_without_ct} |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **{median_str}** |
| P90 | **{p90_str}** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**{rework_pct} %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
{rework_rows}

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
{longrunner_rows}

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
{agent_rows}

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Pfad zu metrics.json")
    parser.add_argument("--output", required=True, help="Pfad zur Ausgabe-Markdown-Datei")
    args = parser.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    page = generate(metrics)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(page, encoding="utf-8")
    print(f"Seite geschrieben: {args.output}")


if __name__ == "__main__":
    main()
