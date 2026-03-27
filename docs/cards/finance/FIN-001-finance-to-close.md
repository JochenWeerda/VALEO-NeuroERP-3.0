# FIN-001 — Finance-to-Close (Card)

**Slice:** FIN-001 | **Lane:** Finance-to-Close | **Status:** abgeschlossen
**Owner:** Claude Sonnet 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

End-to-End Analyse der Finance-to-Close Lane: Buchungsbeleg → Nebenbuch-Abstimmung →
UStVA/Meldewesen → Abschluss-Checkliste → Periodenabschluss. Prüfung aller 7 beteiligten
Masken auf API-Korrektheit, CRUD-Vollständigkeit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/finance/buchungserfassung.tsx` — Legacy apiClient, kein Edit
- `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx` — read-only, kein Matching
- `packages/frontend-web/src/pages/finance/periods.tsx` — kein Reopen
- `packages/frontend-web/src/pages/fibu/abschluss-cockpit.tsx` — Dashboard (ok)
- `packages/frontend-web/src/pages/fibu/abschluss-checklist-detail.tsx` — Item-Complete (ok)
- `packages/frontend-web/src/pages/finance/ustva.tsx` — Legacy apiClient, vollständiger ELSTER-Flow

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/finance/journal-entries/post` | POST | Buchung erfassen |
| `/api/v1/finance/periods/check/{period}` | GET | Periodensperre prüfen |
| `/api/v1/finance/periods` | GET/POST | Perioden auflisten/anlegen |
| `/api/v1/finance/periods/{id}` | PUT | Periode schließen |
| `/api/v1/finance/subsidiary-ledger-reconciliation/summary` | GET | Nebenbuch-Zusammenfassung |
| `/api/v1/finance/subsidiary-ledger-reconciliation/{type}` | GET | AR/AP/BANK Details |
| `/api/v1/finance/closing-checklists/cockpit/summary` | GET | Abschluss-Dashboard |
| `/api/v1/finance/closing-checklists/{id}` | GET | Checkliste laden |
| `/api/v1/finance/closing-checklists/{id}/items/{code}/complete` | POST | Item abhaken |
| `/api/v1/finance/vat-return` | GET | UStVA-Liste |
| `/api/v1/finance/vat-return/calculate` | POST | UStVA berechnen |
| `/api/v1/finance/vat-return/{id}/approve` | POST | UStVA genehmigen |
| `/api/v1/finance/vat-return/{id}/submit` | POST | ELSTER-Übermittlung |

## 4. Client-Warnung

- `buchungserfassung.tsx` nutzt `@/lib/axios` (Legacy) — inkonsistent mit übrigen Masken
- `ustva.tsx` nutzt `@/lib/axios` (Legacy) — hat Workaround `response?.data ?? response`
- `nebenbuch-abstimmung.tsx` nutzt `@/lib/api-client` — `.data`-Extraktion teils inkonsistent
- `periods.tsx`, `abschluss-cockpit.tsx`, `abschluss-checklist-detail.tsx` nutzen `@/lib/api-client` — korrekt

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| FIN-001-P1 | buchungserfassung: Import auf `@/lib/api-client` umstellen | Mittel |
| FIN-001-P2 | buchungserfassung: GET/PUT/DELETE für Journal Entries | Mittel |
| FIN-001-P3 | Nebenbuch-Abstimmung: POST Matching-Buchung | Mittel |
| FIN-001-P4 | Perioden: Reopen für Korrekturbuchungen | Mittel |
| FIN-001-P5 | ustva: Import auf `@/lib/api-client` umstellen | Mittel |
| FIN-001-P6 | Flow-Spine Redirect `/finance/abschluss` → `/fibu/abschluss-cockpit` | Hoch |
| FIN-001-P7 | `workflowInstanceId` in alle 6 Masken durchreichen | Hoch |
| FIN-001-P8 | Transition-API nach Domain-Aktionen aufrufen | Hoch |

## 6. Tests (manuell)

1. Flow-Spine → Neue Instanz "Monatsabschluss" → Redirect (aktuell 404!)
2. Buchungserfassung → Periodenprüfung → POST → Buchung angelegt
3. Nebenbuch-Abstimmung → Periode wählen → Summary + Detail korrekt
4. Perioden → Neue Periode → Close → Status CLOSED
5. Abschluss-Cockpit → Blocker sichtbar → Link zu Checkliste
6. Checkliste → Item Complete → Statuswechsel
7. UStVA → Calculate → Approve → Submit (ELSTER)

---

*Erstellt von Claude Sonnet 4.6 — Slice FIN-001 — 2026-03-27*
