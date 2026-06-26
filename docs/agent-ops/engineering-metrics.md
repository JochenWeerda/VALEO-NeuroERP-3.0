---
title: AI Engineering Metrics
generated: 2026-06-26
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-06-01` · Stand: `2026-06-26`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **97** |
| Slices abgeschlossen | **85** (88 %) |
| Mit externen Gates | 54 |
| Ohne Doku-Dateien | 6 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 82 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.1 h** |
| P90 | **0.3 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**59.2 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| `COM-REGISTER-CAMELCASE-001` | 1 | — |
| `DOC-MIGRATION-007` | 1 | Cursor |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| `DOM-CONTROLLING-004` | 0.8 h | Claude Code |
| `AI-DOC-DRIFT-DASHBOARD-001` | 0.3 h | Claude Code |
| `EXTERNAL-MOCK-HARNESS-001` | 0.3 h | Claude Code |
| `MCP-ERP-TOOLS-001` | 0.3 h | Claude Code |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Cursor | 27 | `████████████████████` |
| Codex | 21 | `████████████████░░░░` |
| Claude Code | 13 | `██████████░░░░░░░░░░` |
| Claude Sonnet 4.6 | 11 | `████████░░░░░░░░░░░░` |
| — | 7 | `█████░░░░░░░░░░░░░░░` |
| claude-sonnet-4-6 | 7 | `█████░░░░░░░░░░░░░░░` |
| ai | 6 | `████░░░░░░░░░░░░░░░░` |
| Claude | 2 | `█░░░░░░░░░░░░░░░░░░░` |
| dev | 2 | `█░░░░░░░░░░░░░░░░░░░` |
| Claude Sonnet 4.6 + Cursor Backend | 1 | `█░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
