---
title: "ADR-047 Kanonischer Fuetterungs-Futtermittelkatalog auf bestehendem Stamm"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-15
version: 1.0.0
---

# ADR-047 Kanonischer Fuetterungs-Futtermittelkatalog auf bestehendem Stamm

**Status:** Proposed

**Datum:** 2026-07-15

## Kontext

`domain_shared.futtermittel_einzelfutter` ist bereits mit Einkauf, Bestand,
Produktion und Labor verknuepft, enthaelt aber nur feste Naehrstoffspalten und
keine revisionsfeste Beratungssicht. Ein neues paralleles Feed-Aggregat wuerde
Identitaet, Bestand und Artikelbezug duplizieren.

## Entscheidung

- Der bestehende Einzelfuttermittel-Datensatz bleibt der kanonische Feed-Kopf.
- Klassifikation, Freigabe, Gueltigkeit und Revision werden additiv ergaenzt.
- Flexible `feeding_feed_reference_values` referenzieren Naehrstoffcode, Einheit,
  Basis, Wertstatus, Herkunft und Gueltigkeit.
- `feeding_feed_products` bildet lieferbare SKU, Gebinde, Mindestabnahme,
  Basispreis, Fracht und Gueltigkeit ab.
- Jede Kopfmutation erzeugt einen append-only Snapshot. Auch die Legacy-CRUD
  delegiert an den neuen Service und kann RBAC/Audit nicht umgehen.
- Der Solveradapter priorisiert gueltige flexible Werte und faellt nur
  kompatibel auf Legacyfelder zurueck. Preise werden als
  `(EUR/t + Fracht EUR/t) / 1000 / TM-Anteil` uebergeben.
- Die vorhandene native ObjectPage wird auf echte Katalogendpunkte umgebunden;
  nur ihr Revisionsdialog bleibt ein Domain-Overlay.

## Konsequenzen

Einkauf und Produktion behalten stabile Feed-IDs. Analysen koennen im naechsten
Slice neue gueltige Werte liefern, ohne den Solververtrag zu veraendern. Der
Legacyfallback bleibt bis zur nachgewiesenen Datenmigration sichtbar und
golden-getestet.
