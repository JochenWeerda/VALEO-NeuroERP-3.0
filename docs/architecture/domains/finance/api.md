---
title: Finance — API
type: reference
audience: [entwickler]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance — API

## eBilanz XML-Entwurf (2026-10-08)

GET /api/v1/ebilanz/taxonomie-felder: amtliche 6.9 GCD-/Kernkonzepte mit limit
1..1000 (Default 100) und skip ab 0. POST /api/v1/ebilanz/export/{export_id}/xbrl-entwurf:
entity_identifier, entity_scheme und facts als Konzeptname -> Dezimal-/Textstring
oder nil. Echte application/xml-Antwort, DRAFT_UNVALIDATED, no-store; Finance-
Schreibrecht und vorhandener Export im Request-Mandanten erforderlich.
Version/IFRS 409, Fakten-/Periodenfehler 422, fehlender/fremder Export 404.
Kein Persistenz-/Amtlichkeits-/Uebertragungserfolg.
[Vertrag und Grenzen](../../../quality-assurance/ebilanz-xbrl-draft-20261008.md).

## Kassen-Tagesabschluss: unbewerteten Direktbuchungsweg gesperrt

POST /api/v1/finance/cash/close-day antwortet mit HTTP 409 und fachlichem
Grund. Kein belegter Kassenbestand und keine Gegenkontierung: keine
Journal-/Zeilenbuchung, kein Commit und kein erfolgreicher Tagesabschluss.
Die alte Summe aller Tagesjournale auf dem geratenen Konto 1000 ist entfernt.
Ein echter Kassenabschluss braucht den fachlichen Bestands-/Bewertungsvertrag.
[ADR-076](../../../adr/adr-076-cash-close-retirement.md).
Routenabnahme: [OpenAPI-Ausschnitt](../../../schnittstellen/contracts/cash-close-retirement-20261005.openapi.json).
Die globale OpenAPI-Datei bleibt beim fremden OPENAPI-DRIFT-REFRESH-Owner.

## Bank-Hauptbuchvertrag und Integrationsvorbehalt

Bankkonto Create/Update/Response: gl_account_id als eigene buchbare
ASSET/bank-Konto-ID; gl_account_number entfaellt. Auswahl:
GET /api/v1/finance/bank-accounts/ledger-options (Header-Tenant, limit<=200).
Reconcile und Summary teilen ReconciliationResult. Geldwerte Decimal-Strings,
fehlende Nachweise null. comparison_state INCOMPLETE/DIFFERENCES/BALANCES_EQUAL;
BALANCES_EQUAL bedeutet Salden-/OP-Kohaerenz, keinen zeilenweisen Journal-Link.
Differenzen maximal 100/Seite mit offset/limit, Gesamtzahl separat.
Neue Migration und Parallel-Merge sind Betriebs-Voraussetzung; gemeinsamer
Migrationsstand noch nicht integriert. [ADR-075](../../../adr/adr-075-bank-ledger-evidence.md).

## Bankvergleich ohne Direktbuchung

POST /api/v1/finance/bank-reconciliation/{statement_id}/reconcile ist
lesend. auto_book=true gibt 409; Default False. can_be_booked stets false,
booking_suggestions entfernt. Differenzen schlagen INVESTIGATE statt geratene
Konten vor. OP-Zuordnung erfolgt durch payments/match, Journalbuchung durch
den bestehenden Journalworkflow. Fehlender GL-/Mandantennachweis bleibt offen.
[ADR-074](../../../adr/adr-074-bank-directbook-retirement.md).

## Rechnungstapel

- `POST|GET /api/v1/billing-batches`
- `GET /api/v1/billing-batches/summary`
- `GET /api/v1/billing-batches/lines`
- `POST /api/v1/billing-batches/{id}/validate|release|execute`
- `POST /api/v1/billing-batches/lines/{id}/retry`

Entscheidung: [ADR-061](../../../adr/adr-061-billing-batch-orchestration.md).

- OpenAPI: [openapi.json](../../../schnittstellen/openapi.json)
- Endpoints: `finance*`, `fibu*`, `ap_*`, `ar_*`, `meldewesen`, `pos` — [endpoint-inventory.md](../../../schnittstellen/endpoint-inventory.md)
- Services: `finance_*`, `accounting_*`, `closing_*`, `ap_invoice*` — [service-inventory.md](../../../entwickler/service-inventory.md)
- Container: primär `backend` (Monolith)
- Berichtskatalog: `/api/v1/l3-report-catalog`, feste Runs, Drilldown und CSV.
- Bonuslaeufe: `GET|POST /api/v1/l3-report-catalog/bonus-runs`,
  `POST .../{run_id}/corrections`, `GET .../{run_id}/export.csv`.
- Belegkontrolle: gespeicherte Frontend-Sichten nutzen die vorhandenen
  `/api/v1/document-control`-Listen-, Status- und Auditvertraege.

## Bankauszug: kanonischer aktiver Vertrag

`POST /api/v1/finance/bank-statements/import` mit bank_account_id und format,
`GET /api/v1/finance/bank-statements/{statement_id}/lines`,
`POST /api/v1/finance/payments/match/{payment_id}` und
`POST /api/v1/finance/payments/auto-match`. X-Tenant-ID bestimmt den Mandanten.
Die vier konkurrierenden INT-BANK-001-Routen unter /api/v1/bank entfallen;
kein Redirect und keine implizite Uebernahme alter IBAN-/DTO-Vertraege.
Externe Alt-Konsumenten benoetigen eine bewusste Vertragsumstellung.
[ADR-073](../../../adr/adr-073-bank-model-retirement.md).
