---
title: CRM — API
type: reference
audience: [entwickler, integrator]
owner: domain/crm
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# CRM — API

## OpenAPI

- Gesamt: [openapi.json](../../../schnittstellen/openapi.json)
- Endpoint-Inventar: [endpoint-inventory.md](../../../schnittstellen/endpoint-inventory.md) — Filter `crm`, `business_partner`, `verkauf`

## Wichtige Endpoint-Module (Monolith)

| Modul | Fokus |
|---|---|
| `business_partners` | Geschäftspartner CRUD, Suche |
| `crm_*` | CRM-spezifische Routen (compat + Kern) |
| `verkauf` | Aufträge, Angebote (O2C-Vorstufe) |

## CRM-Microservice-Cluster

| Service | Port (Dev) | Basis-URL-Env |
|---|---|---|
| crm-core | 5600 | `CRM_CORE_BASE_URL` |
| crm-sales | 5700 | `CRM_SALES_BASE_URL` |
| crm-service | 5800 | `CRM_SERVICE_BASE_URL` |

Siehe [C4 Container](../../views/c4-02-containers.md) — CRM-Cluster-Tabelle.

## Authentifizierung

### Ausfuehrbarer MCP-Kontaktadapter (2026-09-21)

`POST /api/v1/mcp/tools/call` verbindet `crm.contact.log` mit demselben
`CrmKontaktService` wie die Oberflaeche. Verifizierter OIDC-Token mit `sub`,
`tenant_id` und Scope `crm:write` erforderlich. Ein abweichender Tenant-Header
wird abgewiesen. Kunden ohne passende Business-Partner-Mandantenzuordnung
werden nicht freigegeben. Standardmodus ist `dryRun`; `execute` verlangt
`idempotency_key`. Kontakt, Audit und Replay-Journal werden atomar gespeichert.
Weitere Tools sind dadurch nicht automatisch ausfuehrbar.

Vertrag und Nachweise: [MCP-Ausfuehrung](../../../quality-assurance/mcp-execution-crm-20260921.md).

Bearer Token + `X-Tenant-ID` — [ADR-032](../../../adr/adr-032-auth-enforcement-router-global-dependency.md)
