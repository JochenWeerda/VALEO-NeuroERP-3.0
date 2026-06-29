---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-29
version: 3.0.0
generated: 2026-06-29
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-03-31` · Stand: `2026-06-29`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **18** |
| Slices abgeschlossen | **17** (94 %) |
| Mit externen Gates | 3 |
| Ohne Doku-Dateien | 12 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 18 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **n/a** |
| P90 | **n/a** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**64.7 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

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
| Cursor | 15 | `████████████████████` |
| Codex | 2 | `███░░░░░░░░░░░░░░░░░` |
| offen | 1 | `█░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
