# Card: CRM-001 — CRM-to-Revenue

| Feld | Wert |
|------|------|
| **Card-ID** | CRM-001 |
| **Name** | CRM-to-Revenue (Kundenmanagement bis Umsatz) |
| **Flow-Spine** | Kein eigener; CRM-Einstieg ueber `order-to-cash` |
| **Status** | P1-Fixes umgesetzt; Gap-Audit 2026-06-25 |
| **Erstellt** | 2026-03-28 |

## Fixes

| Slice-ID | Thema | Status |
|----------|-------|--------|
| CRM-002 | Kundenumsatz von statischen Demo-Daten auf API umgestellt | **umgesetzt** |

## Offene Gaps

| Gap | Stand 2026-06-25 |
|-----|------------------|
| ~~Opportunities Kanban: /stages Endpoint fehlt~~ | **behoben** — `app/api/v1/endpoints/opportunities.py` (`GET /stages`) |
| ~~Opportunities Forecast: /forecast Endpoint fehlt~~ | **behoben** — `GET /forecast` |
| ~~crm-service.ts Format-Mismatch (data vs. items)~~ | **behoben** — `crm-service.ts` akzeptiert `items` und `data` |
| Legacy-Pfade `/api/crm/` vs. `/api/v1/crm/` | **teilweise offen** — einzelne Masken noch auf Legacy; schrittweise Migration |

## Verbleibende Folgearbeit

- Vollständige Umstellung aller CRM-Frontend-Pfade auf `/api/v1/crm/` (kein Blocker für Kernflows).

## Workflow-Dokumentation

Siehe: [docs/workflows/crm-001-crm-to-revenue.md](../../workflows/crm-001-crm-to-revenue.md)
