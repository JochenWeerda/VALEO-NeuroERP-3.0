---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 3.0.0
generated: 2026-06-28
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-03-30` · Stand: `2026-06-28`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **1** |
| Slices abgeschlossen | **0** (0 %) |
| Mit externen Gates | 1 |
| Ohne Doku-Dateien | 0 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 1 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **n/a** |
| P90 | **n/a** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**63.6 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| — | — | — |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| — | — | — |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Codex | 1 | `████████████████████` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
