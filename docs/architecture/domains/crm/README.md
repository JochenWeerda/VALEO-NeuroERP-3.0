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

## UIX / Universal Mask Generator

CRM ist Pilotdomaene fuer `UIX-MASK-FRAMEWORK-001`.
Die Kunden-360-Maske wird als erster Generator-Kandidat gefuehrt:

- Mask Registry: `crm/customer-360`
- Startvertrag: `GET /api/v1/crm/customers/{customer_id}/screen-summary`
- Migration: bestehende CRM-Masken bleiben aktiv; CRM-Mask-JSONs werden zuerst
  ueber Adapter in `ScreenDefinition` uebersetzt.
- Performance-Regel: Summary zuerst, Kontakte/Belege/Dokumente/Aktivitaeten erst
  bei Tab-Aktivierung, Tabellen serverseitig limitiert und virtualisierbar.

### UIX-CRM-PILOT-002

Der erste produktive Pilot ist `packages/frontend-web/src/pages/crm/kunden-stamm-modern.tsx`.

- Aktivierung: `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true`
- Fallback: bei deaktiviertem Flag bleibt Legacy bzw. die bestehende
  Mask-Builder-Seite aktiv.
- Datenfluss: `screen-summary` laedt zuerst; die Customer-Detailquery wird erst
  danach aktiviert.
- Abnahme: Unit-Tests fuer Adapter/Renderer/Route-Switch plus Playwright-Smoke
  fuer Desktop und Mobile mit gemockter CRM-API.

### UIX-CRM-PARITY-003

Lazy Tab-Listendaten fuer den Generator-Pilot:

- `tab_endpoints` im screen-summary-Vertrag
- `GET /api/v1/crm/customers/{id}/tabs/{tab_key}` (read-only, max. 25 Zeilen)
- Paritaetsmatrix: [mask-parity-customer-360.md](./mask-parity-customer-360.md)

### UIX-DATA-CONTRACT-005

Native ScreenDefinition:

- `GET /api/v1/masks/{mask_id}/screen-definition`
- Pilot bevorzugt native Metadaten, Felder weiterhin aus Adapter bis vollstaendige native Lieferung
