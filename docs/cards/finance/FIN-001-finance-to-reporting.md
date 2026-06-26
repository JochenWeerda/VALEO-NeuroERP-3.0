---
card_id: FIN-001
chain: finance-to-close
chain_step: 0
card_type: overview
flow_spine: flow-spine-finance-to-close
workflow_doc: docs/workflows/fin-001-finance-to-reporting.md
---
# Card: FIN-001 — Finance-to-Reporting

| Feld | Wert |
|------|------|
| **Card-ID** | FIN-001 |
| **Name** | Finance-to-Reporting (Finanzbuchhaltung bis Abschluss) |
| **Flow-Spine** | `flow-spine-finance-to-close` |
| **Status** | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| FIN-002 | Kontenplan-Pfad korrigiert (/finance/chart-of-accounts) | **umgesetzt** |
| FIN-003 | Finance-Followup Router in api.py registriert | **umgesetzt** |

## Offene Gaps

| Gap | Stand 2026-06-25 |
|-----|------------------|
| Abschluss-Aktionen (calculate/lock/run) sind Backend-Stubs | **offen** — Fachlogik Folge-Slice |
| Journal-Pfad-Abweichung in reports.tsx | **offen** — Pfad vereinheitlichen |
| ~~reporting_api.py nicht registriert~~ | **behoben** — `api_router.include_router(reporting_api.router)` |
| ~~Finance-Followup Router~~ | **behoben** — `finance_followup` registriert (FIN-003) |

## Workflow-Dokumentation

Siehe: [docs/workflows/fin-001-finance-to-reporting.md](../../workflows/fin-001-finance-to-reporting.md)
