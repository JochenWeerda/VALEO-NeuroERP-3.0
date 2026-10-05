---
title: DMS / Compliance — API
type: reference
audience: [entwickler]
owner: domain/dms-compliance
status: aktiv
last_reviewed: 2026-08-21
version: 1.1.0
---

# DMS / Compliance — API

- Endpoints: `compliance*`, `dms*`, `archive*`
- Services: `compliance_*`, `archive_*`, `dms_*`, `connector_*`
- Container: `dms-adapter`, `paperless`, `paperless-db`, `paperless-redis`
- Dokumentenruecklauf: `GET/POST /api/v1/docflow/returns`,
  `GET /api/v1/docflow/returns/summary`,
  `GET /api/v1/docflow/returns/{id}/evidence` und
  `POST /api/v1/docflow/returns/{id}/transition`.
- DMS-Volltext: `GET /api/v1/dms/search` mit Tenant-, Text-, Typ-, Kategorie-,
  Artikel- und Seitenfilter; externe Vorschau ist ein Konfigurationsgate.
- Terrorschutz: `POST /api/v1/compliance/sanctions/pruefen` mit Scope
  `manual|personal|customers`; `GET .../pruefprotokoll?scope=...` ist tenantgebunden.
