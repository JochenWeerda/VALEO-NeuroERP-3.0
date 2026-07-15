---
title: "ADR-046 Versionierte Fuetterungsreferenzdaten und explizite FM-TM-Semantik"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-15
version: 1.0.0
---

# ADR-046 Versionierte Fuetterungsreferenzdaten und explizite FM-TM-Semantik

**Status:** Proposed

**Datum:** 2026-07-15

## Kontext

Naehrstoffe, Einheiten und Rundungen waren ueber Solver-Felder, UI-Labels und
Konstanten verteilt. Ein FM/TM-Schalter allein ist fachlich nicht eindeutig:
eine Futtermenge wird von Frischmasse nach Trockenmasse multipliziert, eine
Konzentration dagegen dividiert. Binaere Floats und implizite UI-Rundung koennen
zudem Grenzentscheidungen reproduzierbar veraendern.

## Entscheidung

- `feeding_unit_definitions` und `feeding_nutrient_definitions` sind die
  persistierte, versionierte Referenzbasis; globale Seeds koennen spaeter durch
  tenantgebundene Definitionen ergaenzt werden.
- Dimension, Basisfaktor, Praezision, Herkunft, Wertebereich und Revision sind
  explizite Daten. Historische Snapshots liegen append-only in
  `feeding_reference_revisions`.
- Alle Kernkonvertierungen verwenden `Decimal`. Rundung benoetigt Praezision und
  Modus; Standard fuer fachliche Ausgabe ist `half_up`.
- FM/TM-Konvertierung verlangt neben Ausgangs-/Zielbasis den `value_kind`
  `quantity` oder `concentration`. Eine implizite Deutung ist unzulaessig.
- Die Read-/Conversion-API und die native ScreenDefinition
  `agrar/feeding-reference-data` sind der erklaerbare Vertrag fuer Nutzer und
  nachgelagerte Adapter.

## Konsequenzen

Neue Naehrstoffe bis hin zu Mykotoxinen benoetigen keine neue Solver-Dataclass,
um katalogisiert und validiert zu werden. Bestehende Solver-Felder bleiben bis
`FEED-CORE-018` kompatibel und werden dort ueber einen expliziten Adapter an den
Katalog gebunden. Referenzdaten-Aenderungen erhalten spaeter einen eigenen
Governance-Befehl; diese erste Strecke ist bewusst read-only und erzeugt daher
keine fachlichen Aenderungsereignisse.

## Alternativen

- Weitere feste Codefelder wurden wegen Schema- und UI-Kopplung verworfen.
- Eine einzige FM/TM-Formel wurde wegen der gegensaetzlichen Mengen- und
  Konzentrationssemantik verworfen.
- JavaScript-/Float-Rundung wurde wegen fehlender Reproduzierbarkeit verworfen.
