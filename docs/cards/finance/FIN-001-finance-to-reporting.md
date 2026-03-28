# Card: FIN-001 — Finance-to-Reporting

| Feld | Wert |
|------|------|
| **Card-ID** | FIN-001 |
| **Name** | Finance-to-Reporting (Finanzbuchhaltung bis Abschluss) |
| **Flow-Spine** | `flow-spine-finance-to-close` |
| **Status** | P1-Fixes umgesetzt |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| FIN-002 | Kontenplan-Pfad korrigiert (/finance/chart-of-accounts) | **umgesetzt** |
| FIN-003 | Finance-Followup Router in api.py registriert | **umgesetzt** |

## Offene Gaps

- Abschluss-Aktionen (calculate/lock/run) sind Backend-Stubs
- Journal-Pfad-Abweichung in reports.tsx
- reporting_api.py nicht registriert

## Workflow-Dokumentation

Siehe: [docs/workflows/fin-001-finance-to-reporting.md](../../workflows/fin-001-finance-to-reporting.md)
