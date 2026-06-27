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

Bearer Token + `X-Tenant-ID` — [ADR-032](../../../adr/adr-032-auth-enforcement-router-global-dependency.md)
