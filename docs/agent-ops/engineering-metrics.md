---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
generated: 2026-06-27
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-03-29` · Stand: `2026-06-27`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **159** |
| Slices abgeschlossen | **145** (91 %) |
| Mit externen Gates | 88 |
| Ohne Doku-Dateien | 33 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 144 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.1 h** |
| P90 | **0.8 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**61.2 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| `ALEMBIC-MERGE-001` | 1 | unknown |
| `BULK-REPAIR-001` | 1 | unknown |
| `COM-REGISTER-CAMELCASE-001` | 1 | Claude Code |
| `DOC-MIGRATION-007` | 1 | Cursor |
| `EINKAUF-LS-REPAIR-001` | 1 | unknown |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| `MCP-ERP-TOOLS-001` | 70.0 h | Claude Code |
| `DOM-CONTROLLING-004` | 0.8 h | Claude Code |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Claude Code | 55 | `████████████████████` |
| Cursor | 36 | `█████████████░░░░░░░` |
| Codex | 23 | `████████░░░░░░░░░░░░` |
| Claude Sonnet 4.6 | 14 | `█████░░░░░░░░░░░░░░░` |
| unknown | 8 | `███░░░░░░░░░░░░░░░░░` |
| claude-sonnet-4-6 | 7 | `███░░░░░░░░░░░░░░░░░` |
| ai | 6 | `██░░░░░░░░░░░░░░░░░░` |
| — | 5 | `██░░░░░░░░░░░░░░░░░░` |
| Claude | 2 | `█░░░░░░░░░░░░░░░░░░░` |
| dev | 2 | `█░░░░░░░░░░░░░░░░░░░` |
| Claude Sonnet 4.6 + Cursor Backend | 1 | `░░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
