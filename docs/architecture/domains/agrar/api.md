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

## Produktionsleitstand

- `GET /api/v1/production-control/operations` - tenantgebundene, serverseitig paginierte Produktionsliste.
- `GET /api/v1/production-control/summary` - Worklist-Zusammenfassung.
- `POST /api/v1/production-control/operations` - Muehlen-, Umbuchungs-, Stapel- oder Nachbearbeitungsvorgang.
- `POST /api/v1/production-control/sync` - kanonische Mischfutterauftraege idempotent projizieren.
- `POST /api/v1/production-control/operations/{id}/transition` - begruendeter, auditierter Statuswechsel.
- `GET /api/v1/production-control/operations/{id}/audit` - append-only Verlauf.

Entscheidung: [ADR-059](../../../adr/adr-059-production-control-projection.md).

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
  - tenant- und Business-Grant-isolierter Fuetterungsgruppenstamm mit typisierten Profilen.
- `GET|PATCH /api/v1/agrar/rations-optimization/lifecycle/groups/{id}`
  - Detail bzw. optimistisch versioniertes Update mit Pflichtgrund.
- `GET /api/v1/agrar/rations-optimization/lifecycle/groups/{id}/history`
  - append-only Parameterrevisionen.
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
Gruppenentscheidung: [ADR-045](../../../adr/adr-045-versioned-feeding-groups.md).

## Fuetterungsberatung / Referenzdaten und Einheiten

- `GET /api/v1/agrar/rations-optimization/reference-data/nutrients` — effektiver
  globaler/tenantgebundener Naehrstoffkatalog mit Basis, Einheit, Wertebereich,
  Herkunft und Revision.
- `GET /api/v1/agrar/rations-optimization/reference-data/units` —
  dimensionsgebundene Einheiten mit Basisfaktor und Ausgabe-Praezision.
- `POST /api/v1/agrar/rations-optimization/reference-data/convert-basis` —
  Decimal-basierte FM/TM-Konvertierung mit expliziter Mengen- oder
  Konzentrationssemantik und Rundungsmodus.

Entscheidung: [ADR-046](../../../adr/adr-046-feeding-reference-data-and-unit-conversion.md).

## Fuetterungsberatung / Futtermittelkatalog

- `GET|POST /api/v1/agrar/rations-optimization/feed-catalog/feeds`
- `GET|PATCH /api/v1/agrar/rations-optimization/feed-catalog/feeds/{id}`
- `GET /api/v1/agrar/rations-optimization/feed-catalog/feeds/{id}/history`
- `GET|POST .../feeds/{id}/reference-values`
- `GET|POST .../feeds/{id}/products`

Alle Pfade sind tenant- und Feed-Rollen-gebunden. Kopfupdates verlangen
`expected_revision` und Grund; Werte tragen Basis/Einheit/Herkunft, Produkte
Gebinde/Mindestabnahme/Preis/Fracht/Gueltigkeit. Entscheidung:
[ADR-047](../../../adr/adr-047-canonical-feeding-feed-catalog.md).

## Fütterungsberatung / Einsatzbereitschaft

- `POST /api/v1/agrar/rations-optimization/readiness/evaluate` — prüft einen
  Entwurfssnapshot gegen Bestand, Analyse und Preisgültigkeit.
- `GET /api/v1/agrar/rations-optimization/readiness/materials` — Read-Model der
  aktuell eingesetzten Futtermittel mit Reichweite und Handlungsbedarf.

Entscheidung: [ADR-043](../../../adr/adr-043-feed-readiness-read-model.md).

## Fütterungsberatung / Controlling

- `POST /api/v1/agrar/rations-optimization/controlling/observations` — idempotente
  Tagesbeobachtung je Gruppe, Quelle und Quellenreferenz.
- `GET /api/v1/agrar/rations-optimization/controlling/series` — gruppen- und
  zeitraumfilterbare Soll-Ist-Serie.

Entscheidung: [ADR-044](../../../adr/adr-044-feeding-controlling-observations.md).

## Fütterungsberatung / Futteranalysen

- `GET|POST /api/v1/agrar/rations-optimization/feed-analyses`
- `POST /api/v1/agrar/rations-optimization/feed-analyses/import-preview`
- `GET /api/v1/agrar/rations-optimization/feed-analyses/{id}`
- `GET|POST .../feed-analyses/{id}/values`
- `GET .../feed-analyses/{id}/findings` und `/history`
- `POST .../feed-analyses/{id}/validate`, `/transition` und `/document-reference`
- `POST .../feed-analyses/{id}/actions/release|reject` für
  `validate`, `dryRun`, `propose` und `execute` der Mask ActionRuntime.

Original-/Rechenwerte, Basis, Methode und Schätzstatus bleiben getrennt.
Release erfordert Approver-Rolle, blockierungsfreie Validierung und bei Importen
eine DMS-ID mit SHA-256. Entscheidung:
[ADR-048](../../../adr/adr-048-feeding-analysis-provenance.md).

## Fuetterungsberatung / Rationsvorlagen und Betriebsakte

- `POST /api/v1/agrar/rations-optimization/feeding/ration-templates`
- `GET .../feeding/businesses/{id}/ration-templates`
- `POST .../feeding/ration-templates/{id}/apply`
- `GET .../feeding/businesses/{id}/overview|groups|rations|findings`

Vorlagen referenzieren eine unveraenderliche Quellversion. Apply erzeugt mit
optimistischer Zielversion und Auditgrund eine neue Draft-Version; Quelle und
Ziel muessen dieselbe Fuetterungsgruppe besitzen. Alle Pfade erzwingen Tenant,
Feed-Rolle und Business-Grant. Entscheidung:
[ADR-049](../../../adr/adr-049-feeding-business-file-and-ration-templates.md).

## Fuetterungsberatung / Planpublikation

- `POST /api/v1/agrar/rations-optimization/feeding/plans/publish`
- `GET /api/v1/agrar/rations-optimization/feeding/plans?group_id=...`
- `GET /api/v1/agrar/rations-optimization/feeding/plans/current`
- `GET /api/v1/agrar/rations-optimization/feeding/plans/{version_id}`
- `GET /api/v1/agrar/rations-optimization/feeding/plans/{version_id}/instructions`

Publish verlangt freigegebene/aktive Quellversion, Tierzahl, Dosierschritt,
Rundungsmodus, Gueltigkeit, Auditgrund und Idempotency-Key. Die Antwort enthaelt
geordnete MixingInstructions mit ungerundeter und dosierbarer Chargenmenge samt
Delta. Entscheidung: [ADR-050](../../../adr/adr-050-feeding-plan-version-and-publication.md).

`plan_status` wird serverseitig als `scheduled`, `current` oder `stale`
abgeleitet. Eine neuere Version ersetzt die vorherige erst ab ihrem
`valid_from`; abgelaufene Plaene erscheinen nie in `/current`.

## Fuetterungsberatung / Events

Feeding-Commands schreiben ihre Ereignisse atomar in `public.outbox_events`.
Die Huelle besteht aus `schema_version=1.0`, `event_id`, `event_type`,
`aggregate_id`, `timestamp` und `payload`; die geschlossene Typliste liegt in
`app/agrar/rations/events.py`. Zustellung ist at-least-once, Konsumenten
deduplizieren `event_id`. Entscheidung:
[ADR-054](../../../adr/adr-054-schemafeste-feeding-events.md).

## Fuetterungsberatung / Massnahmen und Beratungsentwuerfe

- `POST /api/v1/agrar/rations-optimization/feeding/measures/{id}/transitions`
- `GET /api/v1/agrar/rations-optimization/feeding/measures/{id}/history`
- `POST /api/v1/agrar/rations-optimization/feeding/measures/process-overdue`
- `GET /api/v1/agrar/rations-optimization/feeding/notifications`
- `POST|GET .../feeding/consulting-cases/{id}/measures`
- `POST|GET .../feeding/consulting-cases/{id}/report-drafts`

Alle Ressourcen sind rollen-, tenant- und Business-Grant-gebunden. Transitionen
sind optimistisch versioniert; Entwuerfe sind strukturiert und keine PDF-
Behauptung. Entscheidung: [ADR-055](../../../adr/adr-055-feeding-measure-lifecycle.md).
