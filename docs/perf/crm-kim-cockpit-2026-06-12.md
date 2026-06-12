# CRM/KIM 360°-Cockpit — Performance-Optimierung (2026-06-12)

Ziel: Das `/crm`-Cockpit reagiert beim **Öffnen** und beim **Kundenwechsel** deutlich
schneller. Frontend: `packages/frontend-web/src/pages/crm/kim/index.tsx`.
Backend: `app/api/v1/endpoints/crm_kim.py`.

## Befund (Ladefolge vorher)
| Schritt | Verhalten vorher |
|---|---|
| Initiale Route `/crm` | `fetchCustomers()` lädt **alle 462** Debitoren mit schwerem `_CUST_SELECT` (LEFT JOIN `kunden_crm360` + JSON-Mapping je Zeile) |
| Kundenwechsel | **4 parallele** Requests: `fetchContacts` + `fetchLogs` + `fetchFinancials` + `fetchDocuments` (+ separater Kundenstamm) |
| DB | `kunden_ansprechpartner.kunden_nr` ohne Index (Seq Scan), `open_items.partner_id` ohne Index |

## Messwerte (Backend, warm, `GAP00001`, Tenant Dev)
| Endpoint | Vorher | Nachher | Δ |
|---|---|---|---|
| `GET /crm/kim/customers` (Default) | **307 ms** (462 Zeilen) | **20 ms** (100 Zeilen) | **−93 % / ~15×** |
| Kundenwechsel | 4 Requests (contacts 17 / logs 14 / financials 21 / documents 18 ms) + Stammdaten | **1 Bündel `…/dashboard` ~21 ms** (inkl. Stammdaten) | 4→1 Roundtrip |
| `kunden_ansprechpartner WHERE kunden_nr=…` | Seq Scan | **Index Scan** (`ix_kunden_ansprechpartner_kunden_nr`) | — |

Messung: `Measure-Command` über `Invoke-RestMethod`, 5 Läufe warm, Durchschnitt.
Die Bündel-/Index-Gewinne skalieren mit echtem Datenvolumen (in DEV sind
`kunden_ansprechpartner`/`open_items` leer; bei produktiven Mengen wirkt der Index
zusätzlich).

## Änderungen
1. **Bündelendpoint** `GET /api/v1/crm/kim/customers/{kunden_nr}/dashboard` →
   `{customer, contacts, logs, financials, documents, meta:{timings, sourceStatus}}`.
   Reine Wiederverwendung der bestehenden Endpoint-Funktionen über **eine** DB-Session;
   jede Quelle tolerant (ein Fehlschlag → leer + Status, kein 500 fürs ganze Dashboard)
   und mit Laufzeit in `meta.timings`.
2. **Frontend Kundenwechsel** nutzt `kimApi.fetchDashboard(id)` statt vier Einzelrequests.
3. **Fallback** in `fetchDashboard`: ist der Bündelendpoint nicht verfügbar (404/ältere
   Backend-Version), werden die vier Einzelrequests wie bisher parallel geholt.
4. **Kundenliste reduziert**: `list_customers` mit serverseitiger Suche (`q`) +
   `limit`/`offset`-Pagination; Default-Limit klein (kein Voll-Laden). Frontend lädt
   eine konfigurierbare Seite (`CUSTOMER_PAGE_LIMIT=100`) und sucht **serverseitig**
   (debounced) über `onSearchChange` — der aktive Kunde bleibt dabei stets erhalten.
5. **Indizes** (Migration `crm_kim_perf_indexes_20260612`): `kunden_ansprechpartner(kunden_nr)`
   und `open_items(tenant_id, partner_id)`. `kunden`/`kunden_crm360` (PK `kunden_nr`) und
   `sales_orders(customer_id)` waren bereits indiziert.

## Verifikation
- Backend-Tests: bestehende `test_crm_kim*` (15) grün; neuer `test_crm_kim_dashboard.py`
  (Bündel-Vertrag, DB-frei) grün. tsc 0, ESLint clean.
- Live verifiziert: Bündel liefert alle fünf Quellen `ok` + `meta.timings`; Suche
  `q=GAP&limit=5` → 5 Treffer; Default-Liste 462→50/100.
- Perf-Smoke `playwright-tests/specs/crm/kim-performance-smoke.spec.ts`: Cockpit öffnet
  unter Budget, Kundenwechsel löst **genau den Bündelrequest** aus (keine Einzelströme),
  kein 404 bei Zurück. (Lokale `@smoke`-Login-Fixture greift nur gegen den CI-Preview;
  Browser-Abnahme in CI — wie übrige Smoke-Specs.)

## Invarianten gewahrt
Keine fachlichen Felder entfernt; keine Mockdaten im Produktivpfad; bestehende Tests
erhalten. Der Bündelendpoint ist additiv — die Einzelendpoints bleiben unverändert
(Fallback-Kompatibilität).
