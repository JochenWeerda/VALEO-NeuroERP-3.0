---
title: AI Engineering Metrics
type: reference
audience: [entwickler, ki-agent, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-08-27
version: 3.0.0
generated: 2026-08-27
---

# AI Engineering Metrics

> **Automatisch generiert** · Daten seit: `2026-05-29` · Stand: `2026-08-27`

## Überblick

| Kennzahl | Wert |
|---|---|
| Slices gesamt | **158** |
| Slices abgeschlossen | **137** (87 %) |
| Mit externen Gates | 85 |
| Ohne Doku-Dateien | 46 |
| Slices ohne Cycle-Time (kein Claim-Commit) | 111 |

## Cycle Time

| Metrik | Wert |
|---|---|
| Median | **0.2 h** |
| P90 | **1.6 h** |

!!! info "Interpretation"
    Cycle Time = Zeit zwischen `chore: claim <SLICE-ID>` und dem ersten `feat(…): <SLICE-ID>`-Commit.
    Slices ohne Claim-Commit werden nicht gezählt (häufig bei älteren Slices ohne Claim-Konvention).

## Rework-Rate

**55.9 %** der Feature-Commits werden von mindestens einem `fix`/`revert`-Commit gefolgt.

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
| `FEED-ACT-030` | 1.6 h | Codex |

## Agent-Produktivität (Slices je Owner)

| Owner | Slices | Anteil |
|---|---|---|
| Codex | 74 | `████████████████████` |
| Claude | 42 | `███████████░░░░░░░░░` |
| Cursor | 15 | `████░░░░░░░░░░░░░░░░` |
| Claude Code | 11 | `███░░░░░░░░░░░░░░░░░` |
| Cursor Agent | 6 | `██░░░░░░░░░░░░░░░░░░` |
| offen | 6 | `██░░░░░░░░░░░░░░░░░░` |
| claude-feed-chain | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Codex -> Claude (Uebernahme nach Codex-Token-Stopp auf ausdruecklichen Auftrag) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| Claude (Fortfuehrung der Kette nach Codex-Token-Stopp) | 1 | `░░░░░░░░░░░░░░░░░░░░` |
| unclaimed | 1 | `░░░░░░░░░░░░░░░░░░░░` |

---

*Generiert von `scripts/ai_engineering_metrics.py` + `scripts/generate_metrics_page.py`
via [AI Engineering Metrics Workflow](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/ai-engineering-metrics.yml).*
