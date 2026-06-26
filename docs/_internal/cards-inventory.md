---
title: Cards-Inventar (intern)
type: reference
audience: [entwickler, product, docs]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Cards-Inventar (intern)

Konsolidierter Stand der Workflow-Cards unter `docs/cards/`.
Ketten-Referenz: [`workflow-chains.md`](workflow-chains.md).

**Generiert:** 2026-06-26 via `scripts/cards-inventory-audit.py`

## Kennzahlen

| Metrik | Wert |
|--------|------|
| Cards gesamt | 147 |
| Status abgeschlossen/umgesetzt | 147 |
| Review empfohlen | 7 |
| Ohne Ketten-Zuordnung (Registry) | 0 |
| Prozess-Cards ohne YAML-Frontmatter | 26 |

## Ketten (Card-Anzahl)

| Kette | Cards |
|-------|-------|
| `(querschnitt/plattform)` | 118 |
| `harvest-to-settlement` | 12 |
| `procure-to-pay` | 4 |
| `order-to-cash` | 3 |
| `compliance-to-report` | 2 |
| `contract-to-settlement` | 2 |
| `finance-to-close` | 2 |
| `inventory-to-settlement` | 2 |
| `complaint-to-resolution` | 1 |
| `service-to-customer` | 1 |

## Status-Verteilung

| Status | Anzahl |
|--------|--------|
| `abgeschlossen` | 96 |
| `umgesetzt` | 31 |
| `erledigt` | 6 |
| `P1-Fixes umgesetzt; Gap-Audit 2026-06-25` | 3 |
| `Erstanalyse abgeschlossen` | 1 |
| `abgeschlossen (Kernkette VK-011/VK-018/VK-010-standardmaske; Rest siehe Abschnitt 13)` | 1 |
| `abgeschlossen (Kernpfad; Follow-up: Inline-Fehler pro Wizard-Schritt)` | 1 |
| `alle Slices umgesetzt` | 1 |
| `umgesetzt (A1-A5)` | 1 |
| `umgesetzt (C1-C3)` | 1 |
| `umgesetzt (Detail + Kern-Flow)` | 1 |
| `umgesetzt (E1-E2, E3-E5 via NC-006)` | 1 |
| `umgesetzt (F1–F5; NC-F5 Copilot-Pipeline abgeschlossen)` | 1 |
| `umgesetzt (G1, G4-G5)` | 1 |
| `umgesetzt (Kernpfad + Field-Service P4/P5)` | 1 |

## Ohne Ketten-Zuordnung

Process-Cards ohne Eintrag in `CHAIN_REGISTRY` / Frontmatter `chain`.

| Card | Typ |
|------|-----|
| *(keine)* | — |

## Review-Queue

| Card | Status | Offene Abschnitte | Kette |
|------|--------|-------------------|-------|
| `COM-001-compliance-to-audit` | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 | Offene Gaps | compliance-to-report |
| `CRM-001-crm-to-revenue` | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 | Offene Gaps | order-to-cash |
| `FIN-001-finance-to-reporting` | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 | Offene Gaps | finance-to-close |
| `NC-A6-neuro-tool-broker` | umgesetzt | Offene Folgearbeit | — |
| `NC-A7-broker-openapi-execution` | umgesetzt | Offene Folgearbeit | — |
| `NC-A8-verification-policy-wave2` | umgesetzt | Offene Folgearbeit | — |
| `NC-A9-intent-llm-fallback` | umgesetzt | Offene Folgearbeit | — |

## Pflege

- Registry: `docs/_internal/workflow-chains.md` + `CHAIN_REGISTRY` im Script
- Frontmatter-Vorlage: `docs/cards/card-template.md`
- Offene Fixes: `docs/agent-ops/active-workboard.md` (CARD-AUDIT-Follow-up)

