---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-12
version: 3.0.0
generated: 2026-07-12
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-04-13` · Stand: `2026-07-12`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **63** |
| Slices abgeschlossen | **44** (70 %) |
| Mit externen Gates | 47 |
| Ohne Doku-Dateien | 28 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 58 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.1 h** |
| P90 | **0.1 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**65.8 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| — | — | — |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| `RATIONS-UX-INTENT-002` | 0.1 h | Codex |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Codex | 29 | `████████████████████` |
| Cursor | 15 | `██████████░░░░░░░░░░` |
| Claude | 11 | `████████░░░░░░░░░░░░` |
| offen | 6 | `████░░░░░░░░░░░░░░░░` |
| unclaimed | 1 | `█░░░░░░░░░░░░░░░░░░░` |
| Claude Code | 1 | `█░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
