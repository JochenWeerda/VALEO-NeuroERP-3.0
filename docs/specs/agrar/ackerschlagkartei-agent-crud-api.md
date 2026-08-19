# Portal Ackerschlagkartei — Agent-CRUD-API

Stand: 2026-07-16
Base: `/api/v1/portal`
Auth: Bearer / Dev-Token; Tenant via Middleware; `customer_id` aus JWT oder Query (`?customer_id=`)

## Operation IDs (OpenAPI / Tool-Binding)

| Methode | Pfad | operation_id |
|---|---|---|
| GET | `/feldbuch/schlaege` | `portal_feldbuch_list_schlaege` |
| POST | `/feldbuch/schlaege` | `portal_feldbuch_create_schlag` |
| GET | `/feldbuch/schlaege/{schlag_id}` | `portal_feldbuch_get_schlag` |
| PUT | `/feldbuch/schlaege/{schlag_id}` | `portal_feldbuch_update_schlag` |
| DELETE | `/feldbuch/schlaege/{schlag_id}` | `portal_feldbuch_delete_schlag` |
| GET | `/feldbuch/massnahmen` | `portal_feldbuch_list_massnahmen` |
| POST | `/feldbuch/massnahmen` | `portal_feldbuch_create_massnahme` |
| GET | `/feldbuch/massnahmen/{massnahme_id}` | `portal_feldbuch_get_massnahme` |
| PUT | `/feldbuch/massnahmen/{massnahme_id}` | `portal_feldbuch_update_massnahme` |
| DELETE | `/feldbuch/massnahmen/{massnahme_id}` | `portal_feldbuch_delete_massnahme` |

Frontend-Imperativ-Client: `portalFeldbuchAgentApi` in `packages/frontend-web/src/lib/api/portal.ts`.

## Regeln für Agenten

- `client_ref` bei Create-Maßnahmen für Idempotenz (Offline/Retry)
- VALEO-Dienst-Maßnahmen (`quelle=erp_*`): Update/Delete → **403**
- Schlag-Delete mit ERP-Maßnahmen → **409**
- Register-Typen: `aussaat` (sorte), `beregnung` (wassermenge_mm), `aum` (aum_code), `psm` (Sachkunde)

## Nachweis

- Contract-Test: `tests/test_portal_feldbuch_crud_agent_contract.py`
- Browser-Praxis: `packages/frontend-web/tests/e2e/portal-feldbuch-crud-praxis.spec.ts` (CRUD, Sammel, Export, CSV-Import, Jahreswechsel, PSM-Sachkunde; Screenshots → `docs/benutzerhandbuch/img/portal__feldbuch*.png`)
- Letztes Protokoll: `artifacts/portal-feldbuch-crud-praxis.json`
