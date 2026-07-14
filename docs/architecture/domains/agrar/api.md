---
title: Agrar — API
type: reference
audience: [entwickler]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Agrar — API

- Endpoints: `agrar*`, `agri*`, `annahme*` — [endpoint-inventory.md](../../../schnittstellen/endpoint-inventory.md)
- Services: `agrar_*`, `agri_*`, `agribusiness_*`, `annahme_*`
- Module: `modules/agrar/`
- Container: `backend`, `rations-optimization`

## Fütterungsberatung / Herd Data

- `POST /api/v1/agrar/rations-optimization/integrations/herd-data/connections`
  — tenantgebundene Verbindung ohne gespeichertes Provider-Secret.
- `GET /api/v1/agrar/rations-optimization/integrations/herd-data/connections`
  — Verbindungen und Freigabestatus.
- `POST /api/v1/agrar/rations-optimization/integrations/herd-data/connections/{id}/sync`
  — manueller Delta-Sync; Live-Gates für Vertrag, Einwilligung, Secret und Egress.
- `POST /api/v1/agrar/rations-optimization/integrations/herd-data/mock-import`
  — normalisierter Entwicklungs-/UAT-Vertrag ohne externen Zugriff.
- `GET /api/v1/agrar/rations-optimization/integrations/herd-data/observations`
  — Gruppen-KPIs, Gesundheitsalarme und genetische Profile.

Entscheidung: [ADR-040](../../../adr/adr-040-contract-gated-herd-data-connectors.md).

## Fuetterungsberatung / Rationslebenszyklus

- `POST|GET /api/v1/agrar/rations-optimization/lifecycle/groups`
  - tenantisolierter Fuetterungsgruppenstamm.
- `POST|GET /api/v1/agrar/rations-optimization/lifecycle/rations`
  - Rationskopf mit unveraenderlicher erster Version bzw. Worklist.
- `GET /api/v1/agrar/rations-optimization/lifecycle/rations/{id}` und
  `/versions` - Detail, Inhalts-Snapshot und Versionshistorie.
- `POST /api/v1/agrar/rations-optimization/lifecycle/versions/{id}/transitions`
  - optimistisch gepruefter Statuswechsel mit Grund und optionalem
  Aktivierungszeitpunkt.
- `GET /api/v1/agrar/rations-optimization/lifecycle/rations/{id}/audit`
  - unveraenderliche fachliche Ereignisspur.
- `GET /api/v1/agrar/rations-optimization/lifecycle/active-rations`
  - aktuelle, freigegebene Ausfuehrungssnapshots fuer Stall und Mobilansicht.

Entscheidung: [ADR-042](../../../adr/adr-042-immutable-ration-lifecycle.md).
