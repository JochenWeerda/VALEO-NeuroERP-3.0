# REK-001 — Complaint-to-Resolution (Card)

**Slice:** REK-001 | **Lane:** Complaint-to-Resolution | **Status:** abgeschlossen
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

End-to-End Analyse der Complaint-to-Resolution Lane: Reklamationserfassung, Triage,
Untersuchung (Labor, DMS), Lösungsgenehmigung und Abschluss. Prüfung aller 5 Frontend-Masken
und des Backend-Reklamations-API auf CRUD-Vollständigkeit, API-Korrektheit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/qualitaet/reklamationen.tsx` — Liste + Neuanlage (ok)
- `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx` — Legacy apiClient, `.data`-Bug
- `packages/frontend-web/src/pages/qualitaet/labor-auftrag.tsx` — Create (ok)
- `packages/frontend-web/src/pages/qualitaet/labor-liste.tsx` — Liste (ok)
- `app/api/v1/endpoints/reklamation_api.py` — Full CRUD + CRM + DMS + Audit (Backend ok)

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

## 4. Client-Warnung

- `reklamationen.tsx` nutzt `useReklamationen()` aus `@/lib/api/misc-modules` — korrekt
- `ausnahmen.tsx` nutzt `@/lib/axios` — `.data`-Bug in Zeile 38
- `labor-auftrag.tsx` nutzt `@/lib/api-client` — korrekt
- `labor-liste.tsx` nutzt `useLaborAuftraege()` aus `@/lib/api/betrieb` — korrekt

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| REK-001-P1 | Detail-Seite `/qualitaet/reklamation/{id}` erstellen | Hoch |
| REK-001-P2 | Transition-Buttons (erfassung → bewertung → ... → abschluss) | Hoch |
| REK-001-P3 | CRM-Verknüpfung in Detail-Seite | Mittel |
| REK-001-P4 | DMS-Dokumentanhang in Detail-Seite | Mittel |
| REK-001-P5 | Audit-Trail Tab in Detail-Seite | Mittel |
| REK-001-P6 | Labor Detail-Seite erstellen | Niedrig |
| REK-001-P7 | ausnahmen.tsx: `.data`-Bug + apiClient-Import | Mittel |
| REK-001-P8 | Reklamation-Create → Flow-Spine Instance auto-create | Hoch |
| REK-001-P9 | Backend-Transition → Flow-Spine Node synchronisieren | Hoch |
| REK-001-P10 | `workflowInstanceId` in alle Masken durchreichen | Mittel |

## 6. Tests (manuell)

1. Reklamationen → Liste laden (3+ Einträge aus API)
2. Reklamation → Neuanlage → POST erfolgreich
3. Laborauftrag → Anlegen → POST erfolgreich
4. Labor-Liste → Aufträge sichtbar
5. Ausnahmen → Liste laden (ggf. `.data`-Fehler sichtbar)

---

*Erstellt von Claude Opus 4.6 — Slice REK-001 — 2026-03-27*
