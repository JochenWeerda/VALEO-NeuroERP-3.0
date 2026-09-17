---
title: Arbeitsliste Frontend-Backend-Luecken
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Abarbeitungsliste der Frontend-Aufrufe ohne Backend — je Eintrag Pfadkorrektur oder fehlender Endpunkt, mit Stand.
---

# Arbeitsliste: Frontend-Aufrufe ohne Backend

Gemessen mit `python scripts/check_frontend_api_calls.py --list`. Der Scanner
liest seit 2026-09-17 auch angehaengte Template-Literale (`/artikel${params}`)
als Abfrageteil — dadurch sind 37 vermeintliche Luecken als Phantome
ausgeschieden. **Echter Stand: 40** (nach Duenger/Saatgut-Mount, Einkauf-GET,
Debitoren-/Kreditoren-Adapter und CRM-Einwilligungen).

Jeder Eintrag hat genau zwei moegliche Antworten:

- **Pfad korrigieren** — die Route heisst anders, das Frontend zeigt daneben.
- **Endpunkt bauen** — es gibt ihn wirklich nicht; dann braucht es Modell,
  Migration, Endpunkt und Test.

Ein dritter Weg — den Aufruf still zu lassen — ist keiner: Der 404 landet im
`catch` und die Maske zeigt eine leere Liste statt eines Fehlers.

## A. Pfadkorrekturen

| Aufruf | Richtige Route | Stand |
|---|---|---|
| `/api/v1/chart-of-accounts/{id}` | `/api/v1/finance/chart-of-accounts/{id}` | offen |
| `/api/v1/gs1/batch-parse` | `/api/v1/gs1/barcode/batch-parse` | offen |
| `/api/v1/qualitaet/reklamationen` | `/api/v1/reklamationen` | offen |
| `/api/v1/saatzucht` | `/api/v1/saatzucht/partien` | offen |
| `/api/v1/operations/exceptions` | `/api/v1/document-control/exceptions` | offen |
| `/api/v1/futter/{kategorie}/bulk-delete` | `/api/v1/futter/einzelfuttermittel/bulk-delete` | offen |
| `/api/v1/preise/konditionen` | `/api/v1/preise/zu-abschlaege/konditionen` | offen |
| `/api/v1/foreign-goods/{a}/{b}` | `/api/v1/foreign-goods` (Filter statt Pfad) | offen |

## B. Fehlende Backends

Nach fachlichem Gewicht sortiert.

### B1. CRM-Einwilligungen (DSGVO) — erledigt 2026-09-17

`/api/v1/crm/consents` inkl. Detail, confirm, revoke, history,
resend-confirmation und `/contact/{id}`. Persistenz `domain_crm.crm_consents`.

### B2. Agrar-Stammdaten — Teilerledigt 2026-09-17

`agrar/duenger` (Liste, Detail, Statistik) und `agrar/saatgut` (Liste, Detail)
sind eingehaengt. Offen: `agrar/biostimulanzien`, `agrar/seed-orders`,
`agrar/kunden`.

### B3. CRM-Vertrieb — 5 Aufrufe

`crm/segments/{id}/members|calculate|performance`,
`crm/opportunities/{id}/history|quotes`.

### B4. Belegaktionen Verkauf/Einkauf — 8 Aufrufe

`sales/orders/{id}/print|post`, `sales/quotations/{id}/print|post`,
`einkauf/anfragen/{id}/send`, `einkauf/lieferscheine/{id}/print`,
`einkauf/rechnungen` (Liste, Detail). GET fuer Angebot, Anlieferavis und
Auftragsbestaetigung ist verdrahtet.

### B5. Finance — 10 Aufrufe

`finance/debitoren` (Liste, Detail) und `finance/creditors` sind Adapter ueber
Kunden- bzw. Lieferantenstamm. Offen: `finance/direct-debits/{id}/approve|execute`,
`finance/fixed-assets` (Liste, Detail, Abschreibung), `finance/stats`,
`finance/followup/fibu/cockpit`, `finance/periods/{id}/close`,
`finance/export/datev`.

### B6. Uebrige — 14 Aufrufe

`pos/gift-cards`, `pos/rabatte`, `pos/tse-journal`, `preise/berechnen`,
`preise/historie`, `personal/work-plan/assignments`, `inventory/epcis/events`,
`analytics/cubes/contract-positions`, `ai/ask`, `rag/search`, `waage/vorlagen`,
`agrar/psm/abgabe/{id}/status`, `compliance/exports/{a}/{b}`,
`vies/validate/{ust_id}`, `audit/change-logs/audit-trail/{typ}/{id}`.

## Wechselwirkungen, die bei jeder Position zu pruefen sind

- **Maske:** Haengt eine ScreenDefinition an dem Endpunkt (`entity`- oder
  Tab-Quelle)? Dann Feldschluessel gegen die echte Antwort pruefen —
  `tests/test_mask_endpoint_inventory.py` faengt nur die Adresse, nicht die
  Spalten.
- **Belegkette:** Steht die Maske in `config/process_chains.yaml`? Ein neuer
  Beleg ohne Kettenschritt ist unsichtbar.
- **Mandant:** Jeder neue Endpunkt filtert ueber `tenant_id` aus dem
  Anfragekontext, nie aus dem Rumpf.
- **Gates:** `scripts/check_frontend_api_calls.py` (Schwelle sinkt),
  `check_openapi_docs` (jede Route braucht `summary=`), `generate_openapi.py`,
  Agent-Handbuch, Architektur-Index.
