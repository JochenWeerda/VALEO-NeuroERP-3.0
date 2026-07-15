---
title: "Impact Note FEED-CORE-018"
type: reference
audience: [architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
---

# Impact Note FEED-CORE-018

## Scope und Grenzen

Additiver Ausbau des bestehenden `domain_shared.futtermittel_einzelfutter` im
Agrar-/Rations-Optimization-Container. Keine neue Stammdatenidentitaet, kein
zweiter Bestand und kein neuer Servicecontainer.

## Verträge

- neuer Feed-Catalog-Router unter dem vorhandenen Rations-Prefix;
- Legacy-CRUD bleibt kompatibel, erzwingt jetzt aber Feed-Rollen und delegiert
  Mutationen an den versionierenden Application Service;
- der Solver-Dictvertrag bleibt stabil; ein expliziter Adapter kapselt die
  flexible/Legacy-Priorisierung;
- die native ScreenDefinition ersetzt Stub-Datenquellen durch echte Entity-,
  Wert-, Produkt- und History-Endpunkte.

## Migration und Rollback

Migration `feed_core_feed_catalog_20260715` folgt linear auf CORE-017, backfillt
Klassifikation/Freigabe und Revision 1. Rollback entfernt nur additive
Kindtabellen/-felder; bestehende Feed-Identitaeten bleiben erhalten.
