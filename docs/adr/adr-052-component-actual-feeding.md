---
title: "ADR-052 Komponentenbezogene Ist-Fuetterung gegen Planversion"
type: adr
audience: [architektur, agrar, controlling, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-052 Komponentenbezogene Ist-Fuetterung gegen Planversion

**Status:** Accepted

**Datum:** 2026-07-16

## Kontext

Die mobile Stallansicht dokumentierte Ist-Mengen bislang in einem breiten
Legacy-FeedingControl-Payload mit einer textuellen `ration_ref`. Damit fehlten
ein FK auf die unveraenderliche Planversion, Komponenten-FKs, reproduzierbare
Wertfolgen, Ursachenklassifikation und eine revisionssichere Korrektur.

## Entscheidung

- Jede Ist-Fuetterung referenziert genau eine aktuelle `FeedingPlanVersion` und
  alle ihre `MixingInstruction`-Komponenten.
- Sollmenge stammt ausschliesslich aus der Instruction; der Client sendet nur
  Feed-ID und Istmenge. Fehlende, doppelte oder fremde Komponenten blockieren.
- Absolute und prozentuale Abweichung werden Decimal-basiert gespeichert. Bei
  Soll null ist Prozent fachlich unbekannt.
- Preis- und Naehrstoffwerte werden zum Fuetterungszeitpunkt aufgeloest und als
  Provenienz im append-only Komponentenstand eingefroren. Nur explizite
  FM-kompatible Einheiten/Basen werden verrechnet; Luecken bleiben sichtbar.
- Ursache ist eine kontrollierte Klassifikation. `other` verlangt Kommentar.
- Restfutter, TM, Schuettelbox und Temperaturen bleiben als auditierter
  Kontext am Record erhalten, ohne die Komponentenabweichung umzudeuten.
- Retry verwendet Idempotency-Key/Request-Hash. Korrektur erzeugt einen neuen
  Record mit `supersedes_id`; Update/Delete sind per Trigger verboten.
- Record, Komponenten und `feeding.actual.recorded` entstehen atomar.
- Die mobile Journey schreibt nur noch diesen Command. Das alte FeedingControl
  bleibt fuer historische DLG-Protokolle lesbar, ist aber keine zweite
  Persistenz des neuen mobilen Abschlusses.

## Konsequenzen

Komponentenabweichung, Ursache, Kosten- und Naehrstofffolge sind direkt zur
Planversion auditierbar und tenant-/grant-sicher exportierbar. Tages-KPI und
Aufgaben aus Schwellenwerten folgen separat in FEED-ACT-030.
