# SVC-001 — Service-to-Customer (Card)

**Slice:** SVC-001 | **Lane:** Service-to-Customer | **Status:** umgesetzt (Kernpfad Serviceanfragen + Rueckmeldung + Abschluss; Field-Service P4 erledigt)
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-31

---

## 1. Zweck

End-to-End Analyse der Service-to-Customer Lane: Serviceanfrage, Disposition, Field-Service-Einsatz,
Rückmeldung und Kundenabschluss. Prüfung aller vorhandenen Masken auf API-Korrektheit,
CRUD-Vollständigkeit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/service/anfragen.tsx` — Liste
- `packages/frontend-web/src/pages/service/anfrage-detail.tsx` — GET/PUT, Tabs, Workflow-Banner
- `packages/frontend-web/src/pages/service/anfrage-neu.tsx` — POST neue Anfrage
- `packages/frontend-web/src/pages/service/rueckmeldung.tsx` — POST Rueckmeldung (report-Node)
- `packages/frontend-web/src/pages/service/abschluss.tsx` — POST Abschluss (closure-Node)
- `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx` — `apiClient` + `useQuery` / `useMutation`, Invalidation nach Delete/Cancel

## 3. API-Endpoints (kanonisch `/api/v1/service/...`)

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/service/anfragen` | GET/POST | Liste / Anlegen |
| `/api/v1/service/anfragen/{id}` | GET/PUT/DELETE | Detail / Update / Loeschen |
| `/api/v1/service/rueckmeldungen` | POST | Rueckmeldung |
| `/api/v1/service/abschluss` | POST | Fall abschliessen |
| `/api/v1/agribusiness/field-service-tasks` | GET | Field-Service-Liste (CRM-Cases gemappt; Demo-Daten `fst-seed-*` bei CRM-Ausfall) |
| `/api/v1/agribusiness/field-service-tasks/{id}` | DELETE | Aufgabe loeschen (CRM; Seeds stub) |
| `/api/v1/agribusiness/field-service-tasks/{id}/cancel` | POST | Storno (CRM `update_case`; Seeds stub) |

Backend Servicefall: `app/api/v1/endpoints/service_anfragen.py` (In-Memory-Store, tenant-isoliert).

Backend Field-Service: `app/api/v1/endpoints/compat.py` (Compat-Router unter `/api/v1`).

## 4. Client-Hinweise

- `anfragen.tsx` nutzt `useServiceAnfragen()` aus `@/lib/api/betrieb`
- Detail/Neu/Rueckmeldung/Abschluss nutzen `@/lib/api-client`
- Field-Service: `@/lib/api-client` + TanStack Query (`useMutation` fuer Delete/Cancel)

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| ~~SVC-001-P4~~ | ~~Field-Service: `fetch()` → apiClient + React Query~~ | erledigt (2026-03-31) |
| SVC-001-P5 | Field-Service: Create/Edit Navigation aktivieren | Mittel |
| — | P1–P3, P4, P6–P10 (Kernpfad inkl. Field-Service API) | erledigt (siehe Workflow) |

## 6. Tests (manuell)

1. Flow-Spine → Servicefall → `/service/anfragen?workflowInstanceId=...`
2. Neue Anfrage → POST → Liste
3. Detail → PUT → speichern
4. Rueckmeldung / Abschluss mit Query `anfrage_id` wo relevant
5. Field-Service: Liste/CRM-Fallback, Delete/Cancel (P4 erledigt); Create/Edit weiterhin P5

---

*Aktualisiert 2026-03-31 — Workflow: `docs/workflows/svc-001-service-to-customer.md`*
