---
title: CRM Domain Pack
type: explanation
audience: [entwickler, architect, agent]
owner: domain/crm
status: pilot
last_reviewed: 2026-06-27
version: 1.0.0
description: Musterdomäne für Architecture OS — CRM Bounded Context.
---

# CRM — Domain Pack

**Owner:** `domain/crm` · **Status:** Pilot (Architecture OS MVP)

CRM umfasst Geschäftspartner, Vertrieb (O2C-Vorstufe), Servicefälle und den optionalen CRM-Microservice-Cluster.

## Schnellnavigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## Architektur-Sichten

- [C4 Component CRM](../../views/components/c4-crm.md)
- [Process Map — O2C](../../process-map.md)
- [Enterprise-Landkarte](../../views/enterprise-landscape.md)

## Code-Lage

| Schicht | Pfad |
|---|---|
| Frontend | `packages/frontend-web/src/pages/crm/`, `verkauf/` |
| Backend Monolith | `app/services/business_partner_service.py`, `app/api/v1/endpoints/` (crm*, business_partner*) |
| CRM Microservices | `docker-compose.yml` — `crm-core` … `crm-security` |
| Events | [events.md](../../../schnittstellen/events.md) |

## Index-Eintrag

Maschinenlesbar: [`config/architecture-index.yaml`](../../../../config/architecture-index.yaml) → `domains.crm`

## Agenten-Hinweis

Strukturelle CRM-Änderungen: [architecture-protocol.md](../../agents/architecture-protocol.md) + [Impact Note](../../agents/impact-note-template.md).
