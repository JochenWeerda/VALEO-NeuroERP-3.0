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
