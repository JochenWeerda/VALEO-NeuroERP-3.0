# CMP-001 — Compliance-to-Report (Card)

**Slice:** CMP-001 | **Lane:** Compliance-to-Report | **Status:** abgeschlossen
**Owner:** Claude Opus 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

End-to-End Analyse der Compliance-to-Report Lane: Datensammlung aus Compliance-Registern,
Aggregation, Validierung, Freigabe (UStVA) und Reporting (PDF/ELSTER). Prüfung aller 6
beteiligten Masken auf API-Korrektheit, CRUD-Vollständigkeit und Flow-Spine-Integration.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx` — Full CRUD Connectors/Schedules (ok)
- `packages/frontend-web/src/pages/compliance/cross-compliance.tsx` — read-only Register
- `packages/frontend-web/src/pages/nachhaltigkeit/eudr-compliance.tsx` — EUDR Dashboard (ok)
- `packages/frontend-web/src/pages/finance/ustva.tsx` — Legacy apiClient, `.data`-Bug
- `packages/frontend-web/src/pages/admin/compliance-dashboard.tsx` — Admin-Übersicht (ok)

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/config/connectors` | GET/PUT/PATCH/DELETE | Meldewesen-Connectors |
| `/api/v1/config/reporting-units` | GET/PUT/PATCH/DELETE | Reporting Units |
| `/api/v1/config/schedules` | GET/PUT/PATCH/DELETE | Meldewesen-Schedules |
| `/api/v1/jobs` | GET | Job-Liste |
| `/api/v1/jobs/run` | POST | Job ausführen |
| `/api/v1/jobs/{id}/artifacts` | GET | Job-Artefakte |
| `/api/v1/compliance/cross-compliance` | GET | Cross-Compliance-Register |
| `/api/v1/compliance/eudr` | GET | EUDR-Status |
| `/api/v1/compliance/stats` | GET | Compliance-Statistiken |
| `/api/v1/compliance/sachkunde-register` | GET | Sachkunde-Register |
| `/api/v1/compliance/qs-checkliste` | GET | QS-Checkliste |
| `/api/v1/compliance/zulassungen-register` | GET | Zulassungen |
| `/api/v1/compliance/report-pdf` | GET | PDF-Report (Blob) |
| `/api/v1/finance/vat-return` | GET/POST | UStVA CRUD |
| `/api/v1/finance/vat-return/{id}/approve` | POST | UStVA genehmigen |
| `/api/v1/finance/vat-return/{id}/submit` | POST | ELSTER-Submit |

## 4. Client-Warnung

- `meldewesen-konsole.tsx` nutzt Custom Hooks aus `@/lib/api/meldewesen` — korrekt
- `cross-compliance.tsx` nutzt Hook `useCrossCompliance` aus `@/lib/api/betrieb` — korrekt
- `eudr-compliance.tsx` nutzt `@/lib/api-client` — korrekt mit `.data`
- `ustva.tsx` nutzt `@/lib/axios` (Legacy) — `.data`-Bug in Zeile 469
- `compliance-dashboard.tsx` mischt `@/lib/api-client` (JSON) + `@/lib/axios` (Blob)

## 5. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| CMP-001-P1 | ustva: Import auf `@/lib/api-client` umstellen | Mittel |
| CMP-001-P2 | ustva Zeile 469: `.data`-Extraktion korrigieren | Mittel |
| CMP-001-P3 | Compliance-Register: CRUD-Endpoints (mindestens Sachkunde, QS) | Mittel |
| CMP-001-P4 | `POST /api/v1/compliance/pcn-meldungen` Backend implementieren | Hoch |
| CMP-001-P5 | Flow-Spine `workflowInstanceId` in alle Masken durchreichen | Mittel |

## 6. Tests (manuell)

1. Meldewesen-Konsole → Connector anlegen/bearbeiten/löschen
2. Meldewesen-Konsole → Schedule anlegen → Job ausführen → Artefakte abrufen
3. Cross-Compliance → Register lesen (3+ Einträge)
4. EUDR-Compliance → Dashboard mit Batches und Risikobewertung
5. UStVA → Calculate → Approve → Submit (ELSTER)
6. Compliance-Dashboard → Alle Register + PDF-Download

---

*Erstellt von Claude Opus 4.6 — Slice CMP-001 — 2026-03-27*
