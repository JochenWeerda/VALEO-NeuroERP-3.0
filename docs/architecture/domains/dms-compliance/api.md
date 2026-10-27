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
- Mayan-Eingang: `POST /api/dms/webhook` verwendet den verifizierten
  Request-Mandanten und einen serverseitig konfigurierten `DMS_TENANT_ID` fuer
  die globale Mayan-Verbindung. Ohne Bindung antwortet er 503, fuer einen
  anderen Mandanten 404, jeweils vor dem DMS-Abruf. Webhook-Wiederholungen
  aktualisieren OCR/Vorschlagsfelder, setzen `processed` aber nicht zurueck.
- Die bestehenden Inbox-Wege unter `/api/dms/inbox` und `/api/v1/dms/inbox`
  lesen ausschliesslich Eintraege des verifizierten Mandanten mit
  `finance_roles.beleg_read`. Schreiben behaelt `SCHREIBEN["BELEGE"]`;
  fremde IDs liefern 404. `POST .../{id}/create` liefert 409 mit
  `open_mask=/einkauf/rechnung-eingang-erfassung`, weil ein OCR-Vorschlag
  keinen Beleg anlegt oder bucht. Die vorhandene Dokumenten-Inbox bietet
  `/api/mcp/documents/inbox/{id}/prepare` fuer den fachlichen Maskenwechsel.
- Terrorschutz: `POST /api/v1/compliance/sanctions/pruefen` mit Scope
  `manual|personal|customers`; `GET .../pruefprotokoll?scope=...` ist tenantgebunden.
