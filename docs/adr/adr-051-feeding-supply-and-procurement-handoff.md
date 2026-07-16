---
title: "ADR-051: Planbasierte Futterversorgung und kontrollierter Einkaufs-Handoff"
type: adr
audience: [architektur, agrar, einkauf, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-051: Planbasierte Futterversorgung und kontrollierter Einkaufs-Handoff

**Status:** Accepted

**Datum:** 2026-07-16

## Kontext

Ein freigegebener Fuetterungsplan erzeugt einen zeitgebundenen Materialbedarf.
Die bisherige Readiness-Projektion las jedoch aktive Editor-/Mobile-Snapshots;
Sicherheitsreserve, explizite Handelseinheit und eine kontrollierte Grenze zum
Einkauf fehlten.

## Entscheidung

Versorgungsbedarf wird ausschliesslich aus aktuellen, unveraenderlichen
`FeedingPlanVersion`-Mischanweisungen abgeleitet. Editor- und Mobile-Snapshots
sind keine Bedarfsquelle. Netto-, Sicherheits- und Bruttobedarf, Bestand,
Reichweite, Unterdeckung, Handelseinheit und Rundungsdelta bleiben als getrennte
Werte sichtbar.

Unbekannter Bestand bleibt `null`; er wird weder als Nullbestand noch als
Bestellmenge interpretiert. Verpackungen werden nur fuer explizite Einheiten
Kilogramm und Tonne konvertiert. Eine Unterdeckung wird auf die positive
Handelseinheit aufgerundet, ohne das Rundungsdelta zu verbergen.

Die Agrar-Domaene erzeugt mit Pflichtgrund und Idempotency-Key einen
append-only `FeedingSupplyHandoff` samt atomarem Outbox-Ereignis. Der Handoff
ist ein Vorschlag an den Einkauf und erzeugt, disponiert oder genehmigt niemals
selbst eine Bestellung.

## Begruendung

Planversionen geben Tierzahl, Dosierung und Gueltigkeit reproduzierbar vor.
Eine direkte Bestellautomatik wuerde Lieferant, Kontrakt, offene Bestellungen,
Reservierungen und Freigabegrenzen der Einkaufsdomaene umgehen. Die explizite
Uebergabe haelt diese Verantwortungsgrenze und macht fachliche Unsicherheit
sichtbar.

## Konsequenzen

- Bestand und Produkt-Handelseinheit bleiben kanonische Katalog-/Lagerdaten.
- Supply ist eine jederzeit neu berechenbare Read-Projektion.
- Ein Handoff speichert den zum Entscheidungszeitpunkt sichtbaren Snapshot.
- Einkauf kann `feeding.supply.procurement_handoff.created` idempotent
  konsumieren und daraus spaeter einen eigenen Bestellvorschlag ableiten.
- Chargen-FIFO, Reservierungen und offene Lieferungen bleiben FEED-SUP-002.

## Rollback

Die additive Tabelle und ihr Trigger koennen vor produktivem Eventkonsum
entfernt werden. Nach Eventkonsum gilt Forward-Fix, weil externe
Einkaufsprojektionen den Handoff bereits referenzieren koennen.
