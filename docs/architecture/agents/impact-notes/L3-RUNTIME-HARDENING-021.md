---
title: Impact Note L3-RUNTIME-HARDENING-021
type: reference
audience: [architektur, frontend, backend, qa, agent]
owner: architecture
status: aktiv
last_reviewed: 2026-08-22
version: 1.0.0
---

# Impact Note L3-RUNTIME-HARDENING-021

## Scope

Haertet die mit `L3-DEEP-MASK-PARITY-020` gelieferten Masken gegen reale
Runtime-, Router-, Datenbank- und Tenant-Vertraege.

## Architekturwirkung

- `useUniversalMaskRuntime` erhaelt feste Queryparameter und laedt jede
  endpointgebundene Tabelle; `serverPagination` steuert nur die Paging-Art.
- `FastTableRenderer` bindet Mehrfachauswahl an sichtbare IDs, leert sie bei
  Query-/Seitenwechsel und behaelt sie bei fehlgeschlagenen Aktionen.
- `article_documents` besitzt einen expliziten Tenant-Link; DMS-CRUD verwendet
  ausschliesslich kanonische Spalten und externe Vorschauen bleiben gegated.
  Beide Bootstrap-Profile kennen Artikeldokumente; bestehende deutsche Profile
  koennen kontrolliert auf `Artikel` oder den generischen Typ `Sonstiges` fallen.
- `ops_chargen` verwendet `(tenant_id, chargen_id)` als Eindeutigkeitsgrenze;
  Repository-, Produktion-, Compliance- und Compat-Zugriffe filtern den Tenant.
- Duengemittelmengen nutzen Count, Aggregate und Page direkt in der Datenbank;
  Schlagflaechen werden in der Bilanz nicht je Massnahme mehrfach gezaehlt.
- Bonuskorrekturen erzeugen eine exportierbare unveraenderliche Detailzeile.
- Produktionsjournalnummern verwenden den zufaelligen UUIDv7-Anteil statt des
  zeitgleichen Praefixes und kollidieren nicht bei dicht erzeugten Auftraegen.

## Migration und Rollout

Migration `l3_runtime_hardening_20260822` backfillt Dokument-Tenants, ersetzt
die globale Chargen-Eindeutigkeit durch Tenant-Eindeutigkeit und ergaenzt die
relevanten Indizes. Die lokale Entwicklungsdatenbank wurde erfolgreich von
`feed_recipes_20260717` bis zum neuen Single Head migriert.

## Sicherheitswirkung

Dokumente und Chargen koennen nicht ueber IDs oder Legacy-Compat-Endpunkte
tenantuebergreifend gelesen, geloescht oder aufgeloest werden. Externe
DMS-Inhalte bleiben ohne konfigurierte Verbindung weder verlinkt noch sichtbar.
