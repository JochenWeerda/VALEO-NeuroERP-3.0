---
card_id: FIN-001
chain: finance-to-close
chain_step: 0
card_type: overview
flow_spine: flow-spine-finance-to-close
workflow_doc: docs/workflows/fin-001-finance-to-reporting.md
---
# Card: FIN-001 - Finance-to-Reporting

| Feld | Wert |
|------|------|
| **Card-ID** | FIN-001 |
| **Name** | Finance-to-Reporting (Finanzbuchhaltung bis Abschluss) |
| **Flow-Spine** | `flow-spine-finance-to-close` |
| **Status** | P1/P2-Gaps repo-seitig geschlossen; externe FiBu-/Steuerberater-Abnahme bleibt Gate |
| **Erstellt** | 2026-03-28 |
| **Letzte Konsolidierung** | 2026-06-26 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| FIN-002 | Kontenplan-Pfad korrigiert (`/finance/chart-of-accounts`) | **umgesetzt** |
| FIN-003 | Finance-Followup Router in `api.py` registriert | **umgesetzt** |
| FIN-004 | Abschluss-Aktionen `calculate` / `lock` / `run` mit Fachlogik | **umgesetzt** |
| FIN-005 | Journal-Pfad in Reports vereinheitlicht | **umgesetzt** |
| FIN-006 | `reporting_api.py` registriert | **umgesetzt** |

## Geschlossene Gaps

| Gap | Stand 2026-06-26 | Quellen |
|-----|------------------|---------|
| ~~Abschluss-Aktionen sind Backend-Stubs~~ | **behoben** | `app/services/finance_closing_service.py`, `app/api/v1/endpoints/finance_actions.py`, `tests/test_finance_closing_service.py` |
| ~~Journal-Pfad-Abweichung in reports.tsx~~ | **behoben** | `docs/workflows/fin-001-finance-to-reporting.md` FIN-005 |
| ~~reporting_api.py nicht registriert~~ | **behoben** | `api_router.include_router(reporting_api.router)` |
| ~~Finance-Followup Router~~ | **behoben** | `finance_followup` registriert (FIN-003) |

## Verbleibende Gates

- Externe FiBu-/Steuerberater-Abnahme fuer reale Periodenabschlusslogik.
- Produktive DATEV-/ELSTER-Cutover bleiben in `open-gaps-and-known-issues.md`
  als externe Production-Readiness-Gates gefuehrt.

## Reverse-Pflege

Bei Aenderungen an `finance_closing_service.py`, `finance_actions.py`,
`tests/test_finance_closing_service.py` oder dem Workflow-Dokument muss diese
Card gemeinsam mit `open-gaps-and-known-issues.md` und
`FIN-ABSCHLUSS-STUBS-001.yaml` neu geprueft werden.

## Workflow-Dokumentation

Siehe: [docs/workflows/fin-001-finance-to-reporting.md](../../workflows/fin-001-finance-to-reporting.md)
