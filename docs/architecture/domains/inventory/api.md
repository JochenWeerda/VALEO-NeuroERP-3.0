---
title: Inventory — API
type: reference
audience: [entwickler]
owner: domain/inventory
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Inventory — API

## Inventur-Nebenlaeufe

- `POST|GET /api/v1/inventory/auxiliary/batches`
- `GET /api/v1/inventory/auxiliary/summary`
- `POST /api/v1/inventory/auxiliary/batches/{id}/transition`

Entscheidung: [ADR-060](../../../adr/adr-060-governed-inventory-auxiliary-batches.md).

- Endpoints: `inventory*`, `lager*`, `warehouse*`
- Services: `inventory_*`, `warehouse_*`
- Microservice: `inventory-service` (docker-compose)
- Cross-Domain-MDE-Vertrag (`L3-MDE-INBOX-003`, Owner Platform/Integration):
  `POST /api/v1/mobile/sync-events`, `GET /api/v1/mobile/sync-queue`,
  `GET /api/v1/mobile/sync-summary`, `POST /api/v1/mobile/sync-process`,
  `POST /api/v1/mobile/sync-queue/{event_id}/retry` und
  `GET /api/v1/mobile/sync-queue/{event_id}/audit`.
- Monolith-Routen unter `/api/v1` für compat-Lager
- Chargen: tenantgebundene CRUD-/Listenpfade unter `/api/v1/chargen` sowie
  `POST /api/v1/chargen/operator/bulk-release` mit Qualitaetsgate und Auditgrund.
