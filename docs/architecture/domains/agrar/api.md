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
