---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-08-22
version: 3.0.0
generated: 2026-08-22
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-05-24` · Stand: `2026-08-22`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **123** |
| Slices abgeschlossen | **102** (83 %) |
| Mit externen Gates | 81 |
| Ohne Doku-Dateien | 32 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 91 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.2 h** |
| P90 | **2.1 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**61.7 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

### Top Rework-Slices

| Slice | fix-Commits | Owner |
|---|---|---|
| `DESIGN-GAPS-SWEEP-002` | 1 | Claude |

## Langläufer (≥ P90)

| Slice | Cycle Time | Owner |
|---|---|---|
| `FEED-EDITOR-023` | 13.4 h | Claude |
| `FEED-AI-046` | 3.9 h | claude-feed-chain |
| `FEED-INT-036` | 2.2 h | Codex |
| `FEED-ADVICE-ROLES-013` | 2.1 h | Claude |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Codex | 55 | `████████████████████` |
| Claude | 42 | `███████████████░░░░░` |
| Cursor | 15 | `█████░░░░░░░░░░░░░░░` |
| offen | 6 | `██░░░░░░░░░░░░░░░░░░` |
| claude-feed-chain | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Codex -> Claude (Uebernahme nach Codex-Token-Stopp auf ausdruecklichen Auftrag) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Claude (Fortfuehrung der Kette nach Codex-Token-Stopp) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| unclaimed | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Claude Code | 1 | `░░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
