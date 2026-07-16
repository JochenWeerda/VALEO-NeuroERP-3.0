---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-16
version: 3.0.0
generated: 2026-07-16
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-04-17` · Stand: `2026-07-16`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **94** |
| Slices abgeschlossen | **75** (80 %) |
| Mit externen Gates | 74 |
| Ohne Doku-Dateien | 30 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 77 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.1 h** |
| P90 | **0.9 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**62.8 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| `DESIGN-GAPS-SWEEP-002` | 1 | Claude |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| `FEED-ADVICE-ROLES-013` | 2.1 h | Claude |
| `FEED-CORE-019` | 0.9 h | Codex -> Claude (Uebernahme nach Codex-Token-Stopp auf ausdruecklichen Auftrag) |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Codex | 46 | `████████████████████` |
| Claude | 23 | `██████████░░░░░░░░░░` |
| Cursor | 15 | `███████░░░░░░░░░░░░░` |
| offen | 6 | `███░░░░░░░░░░░░░░░░░` |
| Codex -> Claude (Uebernahme nach Codex-Token-Stopp auf ausdruecklichen Auftrag) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Claude (Fortfuehrung der Kette nach Codex-Token-Stopp) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| unclaimed | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Claude Code | 1 | `░░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
