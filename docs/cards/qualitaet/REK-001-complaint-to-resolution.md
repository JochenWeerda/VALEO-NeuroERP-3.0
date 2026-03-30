# REK-001 — Complaint-to-Resolution (Card)

**Slice:** REK-001 | **Lane:** Complaint-to-Resolution | **Status:** umgesetzt (Detail + Kern-Flow)
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-30

---

## 1. Zweck

End-to-End Analyse der Complaint-to-Resolution Lane: Reklamationserfassung, Triage,
Untersuchung (Labor, DMS), Lösungsgenehmigung und Abschluss. Prüfung aller 5 Frontend-Masken
und des Backend-Reklamations-API auf CRUD-Vollständigkeit, API-Korrektheit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/qualitaet/reklamationen.tsx` — Liste + Neuanlage
- `packages/frontend-web/src/pages/qualitaet/reklamation-detail.tsx` — Detail mit Tabs (Uebersicht, CRM, Dokumente, Audit), Transitions, Workflow-Banner
- `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx` — `@/lib/api-client`, GET mit `.data`
- `packages/frontend-web/src/pages/qualitaet/labor-auftrag.tsx` — Create
- `packages/frontend-web/src/pages/qualitaet/labor-liste.tsx` — Liste
- `packages/frontend-web/src/pages/qualitaet/labor-detail.tsx` — Labor-Auftrag Detail
- `app/api/v1/endpoints/reklamation_api.py` — Full CRUD + CRM + DMS + Audit

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/qualitaet/reklamationen` | GET | Reklamationsliste |
| `/api/v1/reklamationen` | POST | Reklamation anlegen |
| `/api/v1/reklamationen/{id}` | GET | Reklamation Detail |
| `/api/v1/reklamationen/{id}/transition` | POST | Status-Transition |
| `/api/v1/reklamationen/{id}/crm-reference` | POST | CRM-Fall verknüpfen |
| `/api/v1/reklamationen/{id}/dms-referenzen` | POST | DMS-Dokumente anhängen |
| `/api/v1/reklamationen/{id}/audit` | GET | Audit-Trail |
| `/api/v1/reklamationen/{id}/e2e` | GET | E2E-Übersicht |
| `/api/v1/qualitaet/labor-auftraege` | GET/POST | Laboraufträge |
| `/api/v1/operations/exceptions` | GET | Ausnahmen-Register |

## 4. Client-Hinweise

- `reklamationen.tsx` nutzt `useReklamationen()` aus `@/lib/api/misc-modules`
- `ausnahmen.tsx` nutzt `@/lib/api-client` mit korrekter `.data`-Extraktion
- `reklamation-detail.tsx` nutzt `@/lib/api-client`; Flow-Spine: `readWorkflowEntryContext`, best-effort Transition nach Statuswechsel

## 5. Offene Punkte

Keine aus dieser Card — siehe `docs/workflows/rek-001-complaint-to-resolution.md` fuer Historie.

## 6. Tests (manuell)

1. Reklamationen → Liste laden
2. Reklamation → Detail öffnen → Transition, CRM, DMS, Audit prüfen
3. Ausnahmen → Liste laden
4. Laborauftrag / Labor-Liste wie bisher

---

*Aktualisiert 2026-03-30 — Workflow: `docs/workflows/rek-001-complaint-to-resolution.md`*
