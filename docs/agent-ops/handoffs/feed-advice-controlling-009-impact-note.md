---
title: FEED-ADVICE-CONTROLLING-009 Impact Note
type: handoff
audience: [agent, entwickler, produkt, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-07-14
version: 1.0.0
---

# FEED-ADVICE-CONTROLLING-009 Impact Note

## Ergebnis

Idempotente Tagesbeobachtungen verbinden die aktive Rationsversion mit Aufnahme,
Kosten, Milch/ECM, Stickstoffeffizienz und Methan. Die native Controlling-Worklist
ersetzt den bisherigen Rücksprung in den Solver und bietet eine kompakte manuelle
Erfassung; unbekannte Daten bleiben ausdrücklich leer.

## Architekturwirkung

- Neue lineare Migration `feed_advice_controlling_20260714`.
- Kanonischer API-Vertrag für manuelle, Mischwagen-, Herd- und Importquellen.
- Native ScreenDefinition `agrar/feed-controlling` im Meridian-Runtime-Pfad.
- ADR-044 definiert Idempotenz, Berechnungsgrundlagen und Schätzkennzeichnung.

## Abnahme

Die finalen Test-, Browser- und Architektur-Gates werden im Workboard protokolliert.

