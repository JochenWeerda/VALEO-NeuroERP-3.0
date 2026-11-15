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

## DocFlow-Teilmengen (14.11.2026)

`GET /api/v1/docflow/{doc_id}/conversion-options?target_doc_type=...` liefert
Positionskennungen, Artikel, Einheiten und Restmengen fuer genau diese Folgeart
sowie die Belegversion. Der Weg braucht Leserecht am Quellbeleg und
Bearbeitungsrecht an der Zielart; er gibt keine Preise zurueck und bootstrapped
keine Altdaten. Der verifizierte Mandant bleibt bindend.

Die Studio-Belegfamilie 1.9.0 sammelt explizite Mengen in der gemeinsamen
Tabelleneingabe (initial null, keine automatische Volluebernahme). UI und CLI
uebersetzen die Auswahl auf dasselbe `quantities_by_source_item_id` des
bestehenden `POST /api/v1/docflow/{doc_id}/convert`; Vorschau und Ausfuehrung
behalten Version und ausgewaehlte Mengen. Restmenge, Positionszugehoerigkeit,
Idempotenz und Versionskonflikte entscheidet weiterhin der Domain-Command.
Schreibende Agentenaktionen bleiben gesperrt. [Abnahmegrenzen](../../../quality-assurance/docflow-teilmengen-eingabe-20261114.md).
