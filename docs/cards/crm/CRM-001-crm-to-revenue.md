# Card: CRM-001 — CRM-to-Revenue

| Feld | Wert |
|------|------|
| **Card-ID** | CRM-001 |
| **Name** | CRM-to-Revenue (Kundenmanagement bis Umsatz) |
| **Flow-Spine** | Kein eigener; CRM-Einstieg ueber `order-to-cash` |
| **Status** | P1-Fixes umgesetzt |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| CRM-002 | Kundenumsatz von statischen Demo-Daten auf API umgestellt | **umgesetzt** |

## Offene Gaps

- Opportunities Kanban: /stages Endpoint fehlt
- Opportunities Forecast: /forecast Endpoint fehlt
- crm-service.ts Format-Mismatch (data vs. items)
- Legacy-Pfade /api/crm/ vs. /api/v1/crm/

## Workflow-Dokumentation

Siehe: [docs/workflows/crm-001-crm-to-revenue.md](../../workflows/crm-001-crm-to-revenue.md)
