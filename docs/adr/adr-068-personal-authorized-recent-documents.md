---
title: ADR-068 Persoenliche berechtigte Dokumenthistorie
type: adr
audience: [architektur, entwickler, product, qa, datenschutz]
owner: domain/workspace
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-068 Persoenliche berechtigte Dokumenthistorie

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

L3 bietet eine bereichsuebergreifende Liste zuletzt verwendeter Dokumente.
Eine globale oder nur tenantgebundene Historie wuerde jedoch Benutzerverhalten
und moeglicherweise nicht mehr berechtigte Belege offenlegen.

## Entscheidung

- Native Detailmasken melden eine erfolgreiche Oeffnung zentral aus
  `UniversalNativeDetailPage`; Quellaggregate werden nicht veraendert.
- Eintraege sind durch Tenant, Benutzer, Screen und Dokument identifiziert.
  Erneutes Oeffnen aktualisiert Zeit und Rang statt eine Dublette anzulegen.
- Dokumentfamilien sind allowlistgebunden. Die erforderliche Leserolle wird
  beim Schreiben und erneut beim Lesen geprueft, damit Rollenentzug sofort
  wirkt.
- Nur interne Routen werden akzeptiert. Die Projektion speichert Typ, Nummer,
  Partner, Titel und Zeitpunkt, aber keinen Dokumentinhalt.
- Aufbewahrung ist auf 90 Tage und 200 Eintraege pro Benutzer begrenzt;
  einzelne oder alle eigenen Eintraege sind loeschbar.
- `workspace/letzte-dokumente` rendert als native Meridian-Worklist.

## Konsequenzen

`L3-GAP-RECENT-013` ist repo-seitig geschlossen. Nicht-native Altseiten koennen
spaeter denselben Touch-Vertrag nutzen; die zentrale native Wechselstrecke ist
bereits abgedeckt.
