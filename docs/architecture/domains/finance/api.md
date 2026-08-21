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
