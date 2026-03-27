# SVC-001 — Service-to-Customer (Card)

**Slice:** SVC-001 | **Lane:** Service-to-Customer | **Status:** abgeschlossen
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

End-to-End Analyse der Service-to-Customer Lane: Serviceanfrage, Disposition, Field-Service-Einsatz,
Rückmeldung und Kundenabschluss. Prüfung aller vorhandenen Masken auf API-Korrektheit,
CRUD-Vollständigkeit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/service/anfragen.tsx` — Liste (nur GET, kein Detail/Create)
- `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx` — fetch() statt apiClient
- (fehlt) Rückmeldung/Aktivitäten-Seite
- (fehlt) Kundenabschluss-Seite

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/service/anfragen` | GET | Serviceanfragen-Liste |
| `/api/agribusiness/field-service-tasks` | GET | Field-Service-Aufgaben |
| `/api/agribusiness/field-service-tasks/{id}/cancel` | POST | Aufgabe stornieren |
| `/api/agribusiness/field-service-tasks/{id}` | DELETE | Aufgabe löschen |
| `/api/audit/change-logs/audit-trail/{type}/{id}` | GET | Audit-Trail |

## 4. Client-Warnung

- `anfragen.tsx` nutzt `useServiceAnfragen()` aus `@/lib/api/betrieb` — korrekt (.data abstrahiert)
- `field-service-tasks.tsx` nutzt native `fetch()` — NICHT apiClient, kein Auth-Interceptor

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| SVC-001-P1 | Detail-Seite `/service/anfrage/{id}` | Hoch |
| SVC-001-P2 | Create-Seite `/service/anfrage/neu` | Hoch |
| SVC-001-P3 | CRUD-Hooks für Serviceanfragen | Hoch |
| SVC-001-P4 | Field-Service: fetch() → apiClient + React Query | Mittel |
| SVC-001-P5 | Field-Service: Create/Edit Navigation aktivieren | Mittel |
| SVC-001-P6 | Rückmeldung-Seite erstellen (Node: report) | Hoch |
| SVC-001-P7 | Kundenabschluss-Seite erstellen (Node: closure) | Hoch |
| SVC-001-P8 | Backend Service Domain anlegen | Hoch |
| SVC-001-P9 | API-Endpunkt kanonisieren (crm/cases vs service/anfragen) | Mittel |
| SVC-001-P10 | workflowInstanceId in alle Masken durchreichen | Mittel |

## 6. Tests (manuell)

1. Flow-Spine → Neuen Servicefall starten → Redirect auf `/service/anfragen`
2. Serviceanfragen → Liste laden (2+ Einträge)
3. Field-Service → Aufgaben-Liste laden
4. Field-Service → Aufgabe stornieren → Toast
5. Field-Service → Audit-Trail abrufen

---

*Erstellt von Claude Opus 4.6 — Slice SVC-001 — 2026-03-27*
