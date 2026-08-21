---
title: ADR-062 Fremdware als auditierte Operator-Projektion
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/inventory
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-062 Fremdware als auditierte Operator-Projektion

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

Die kanonische Fremdwaren-Einlagerung war im Einkaufs-Backend vorhanden, aber
L3-Anwender hatten keinen geschlossenen Arbeitsplatz fuer Eigentuemerkontext,
Lagerbestand, Umbuchung, Erledigung und Nachweis.

## Entscheidung

- `domain_einkauf.fremdwaren_einlagerung` bleibt die kanonische Quelle; eine
  zweite Bestandsfuehrung wird nicht aufgebaut.
- Die Worklist ist durchgehend mandantengefiltert und zeigt Mandant sowie
  Eigentuemer explizit. Eigentümer-, Lager-, Status- und Textfilter werden
  serverseitig angewandt.
- Umbuchung und Teil-/Vollauslagerung sperren den Datensatz, validieren den
  Status und schreiben einen append-only Auditdatensatz mit Benutzer und
  Pflichtgrund.
- `lager/fremdware` ist eine native, virtualisierte Meridian-Worklist ueber der
  zentralen ScreenDefinition-/RenderPlan-Laufzeit.

## Konsequenzen

`L3-ROHWARE-002` ist repo-seitig geschlossen. Lagerpilot, Druckerprofil und
Echtdaten-UAT bleiben externe Rollout-Gates.
