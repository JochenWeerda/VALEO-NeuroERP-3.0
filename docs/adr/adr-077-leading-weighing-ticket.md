---
title: ADR-077 Fuehrender Wiegeschein im Inventory-Kern
type: adr
audience: [architektur, entwickler, qa]
owner: domain/inventory
status: accepted
last_reviewed: 2026-10-05
version: 1.0.0
---

# ADR-077 Fuehrender Wiegeschein im Inventory-Kern

**Status:** Accepted
**Datum:** 2026-10-05
**Auftrag:** User verlangt das Schliessen des offenen ADR-Handshakes und hat
Entwicklungsaltlasten zum Rueckbau freigegeben. Die bestehende Domain-Grenze
und die bereits kanonische Doppelwiegung werden bestaetigt.

## Kontext

Drei Speicher stehen nebeneinander. `domain_inventory.weighing_tickets`
traegt den Wiegeschein mit Brutto, Tara, Netto, zwei Messzeitpunkten,
Vertragszuordnung, Artikel und Mandant. Wiegescheinpositionen, Messungen,
Kontraktabrufe und Rueckverfolgbarkeit referenzieren diese Identitaet.
`wiegung_service.py` schreibt die Doppelwiegung bereits hierhin.
`domain_agrar.weighing_tickets` ist dagegen eine historische Kopie fuer
Mobile-Quittierungen mit deutschen Gewichtsfeldern; nur `waage_mobile.py`
konsumiert sie. `domain_ops.ops_wiegungen` wird durch das separate
Wiegung-ORM/Repository und die einfachen CRUD-Wege unter `/waage/wiegungen`
geschrieben und hat keine kanonische Mandantenbindung.
Am 2026-10-05 sind die beiden konkurrierenden Tabellen im bestehenden
valeo_probe leer. Dies ist ein Pruefstandbeleg, keine Aussage ueber andere DBs.

## Entscheidung

**Genau ein fuehrender Wiegeschein: `domain_inventory.weighing_tickets`.**
Alle fachlichen Beziehungen nutzen dessen `id` und `tenant_id`. Mobile
Quittierungen sind eigene Ereignisse zu diesem Wiegeschein, keine zweite
Wiegetabelle und keine zweite gespeicherte Wahrheit ueber das Gewicht.
Waagenstammdaten bleiben in Operations; sie sind kein konkurrierender Beleg.
Die getrennten Agrar- und Operations-Wiegebelege werden entfernt, sobald
ihre lebenden Verbraucher auf den kanonischen Vertrag umgestellt sind.
Keine neuen Archive, Copy-Tabellen oder dauerhaft parallelen Adapter.

## Konsequenzen

Der Entscheidungs-Handshake ist geschlossen. Die technische Zusammenfuehrung
ist ein eigener, ausdruecklich offener Folge-Slice; dieser ADR behauptet
keinen bereits vollzogenen Rueckbau. Er umfasst Mobile-Quittierungswege,
Operations-Wiegung-CRUD/Repository/ORM, Verbraucher und Tests sowie eine
Migration. Vor dem Entfernen Tabellenbestand und eingehende Referenzen
pruefen; vorhandene Belege nicht still verwerfen oder neu zuordnen.
Quittungen benoetigen eine mandantengebundene Referenz auf den kanonischen
Schein; ihr Status wird aus Ereignissen abgeleitet. Der Rueckbau darf keine
Gewichts- oder Richtungssemantik verlieren. Wiegescheinverknuepfungen werden
ueber IDs geloest; Kennzeichen allein ist kein eindeutiger Beleglink.

Abnahme: mobile Quittierung und Wiederholung fuer denselben kanonischen
Schein, Fremdtenant-Abweisung, CRUD mit identischer Beleg-ID, unveraenderte
Netto-/Richtungsregeln und Rueckverfolgbarkeit, keine lebenden Referenzen auf
beide Alttabellen. Bestehender gemeinsamer Pruefstand, kein neuer DB/Container.
