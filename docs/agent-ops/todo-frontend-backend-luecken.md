---
title: Arbeitsliste Frontend-Backend-Luecken
type: reference
audience: [agent, entwickler]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-09-17
version: 1.1.0
description: Abarbeitungsliste der Frontend-Aufrufe ohne Backend — je Eintrag Pfadkorrektur oder fehlender Endpunkt, mit Stand.
---

# Arbeitsliste: Frontend-Aufrufe ohne Backend

Gemessen mit `python scripts/check_frontend_api_calls.py --list`.

**Stand 2026-09-17: 0 tote Pfade** (Ratsche `BASELINE = 0`). Start 110; Praefix-Fehler,
Scanner-Phantome, Duenger/Saatgut-Mount, Einkauf-GET, Debitoren-Adapter,
CRM-Einwilligungen und die Restliste aus Claudes Verdrahtungsbericht sind
geschlossen.

Jeder Eintrag hatte genau zwei moegliche Antworten:

- **Pfad korrigieren** — die Route heisst anders, das Frontend zeigt daneben.
- **Endpunkt bauen** — es gibt ihn wirklich nicht; dann braucht es Modell,
  Migration, Endpunkt und Test.

Ein dritter Weg — den Aufruf still zu lassen — ist keiner: Der 404 landet im
`catch` und die Maske zeigt eine leere Liste statt eines Fehlers.

## A. Pfadkorrekturen

| Aufruf | Antwort | Stand |
|---|---|---|
| `/api/v1/chart-of-accounts/{id}` | Frontend auf `/finance/chart-of-accounts` | erledigt (Claude) |
| `/api/v1/gs1/batch-parse` | Frontend auf `/gs1/barcode/batch-parse` | erledigt (Claude) |
| `/api/v1/saatzucht` | Frontend auf `/saatzucht/partien` | erledigt (Claude) |
| `/api/v1/sales/quotations/{id}/print\|post` | Alias des Angebotsrouters unter `/sales/quotations` | erledigt |
| `/api/v1/qualitaet/reklamationen` | Listen-Adapter auf `domain_ops.reklamationen` (GET-Liste fehlte unter `/reklamationen`) | erledigt |
| `/api/v1/operations/exceptions` | Adapter auf Document-Control-Worklist, deutsche Feldschluessel der Ausnahmen-Maske | erledigt |
| `/api/v1/futter/{kategorie}/bulk-delete` | Sammelloeschung auf den Futtermittel-Stamm | erledigt |
| `/api/v1/preise/konditionen` | Einzelobjekt wie die Maske es liest, nicht die Zu-/Abschlag-Liste | erledigt |
| `/api/v1/waage/vorlagen` | Adapter auf `domain_agrar.waagen_vorlagen` mit Maskenfeldern | erledigt |
| `/api/v1/finance/export/datev` | Alias auf DATEV-Export | erledigt |
| `/api/v1/vies/validate/{ust_id}` | VIES-Pruefung unter dem Frontend-Pfad | erledigt |

## B. Fehlende Backends — erledigt 2026-09-17

### B1. CRM-Einwilligungen (DSGVO)

`/api/v1/crm/consents` inkl. Detail, confirm, revoke, history.

### B2. Agrar-Stammdaten

`agrar/duenger`, `agrar/saatgut`, `agrar/biostimulanzien` (Liste/Detail mit
`ist_aktiv`/`verfuegbar`), `agrar/kunden` (Kundenstamm plus Schlagzahlen),
`agrar/seed-orders` (Persistenz `domain_agrar.seed_orders`).

### B3. CRM-Vertrieb

`crm/segments/{id}/members|calculate|performance`,
`crm/opportunities/{id}/quotes`.

### B4. Belegaktionen Verkauf/Einkauf

`sales/orders/{id}/print|post` (bereits am Auftrag), Alias
`sales/quotations/{id}/print|post`, `einkauf/anfragen/{id}/send`,
`einkauf/lieferscheine/{id}/print` (Backend-Alias, FSX-Datei unangetastet),
`einkauf/rechnungen` Liste/Detail/PATCH/DELETE auf `einkauf_rechnungseingaenge`.

### B5. Finance

Lastschrift `approve|execute`, Anlagenbuchhaltung unter den deutschen
Maskenschluesseln, `finance/stats`, Fibu-Cockpit, Periodenabschluss, DATEV.

### B6. Uebrige

POS Gutscheine/Rabatte/TSE-Journal, Preiskalkulation und -historie,
Dienstplan-Zuweisungen (`domain_hr.work_plan_assignments`), EPCIS-Ereignisse
(`domain_inventory.epcis_events`), Kontrakt-Cube, `ai/ask`, `rag/search`,
Aenderungshistorie.

## Nicht verdrahtet

`lager/leitstand` bleibt ein leeres Cockpit ohne Kacheln. Eine Seite dafuer
waere Dekoration, solange die Fachfrage offen ist.

## Wechselwirkungen

- **Maske:** `tests/test_mask_endpoint_inventory.py` prueft Adressen, nicht
  Spalten. Biostimulanzien-Liste liefert `ist_aktiv`/`verfuegbar`, damit leer
  nicht wie „nichts erfasst" aussieht.
- **Mandant:** Neue Endpunkte filtern ueber `tenant_id` aus dem Anfragekontext.
- **Gates:** `scripts/check_frontend_api_calls.py` Schwelle **0**,
  `tests/test_mask_frontend_bridges.py`, OpenAPI-`summary=`, Studio-Katalog.
