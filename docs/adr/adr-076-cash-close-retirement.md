---
title: ADR-076 Kassenabschluss ohne Scheinbuchung
type: adr
audience: [architektur, entwickler, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-10-05
version: 1.0.0
---

# ADR-076 Kassenabschluss ohne Scheinbuchung

**Status:** Proposed
**Datum:** 2026-10-05

## Kontext

POST finance/cash/close-day summierte alle Tagesjournale des Mandanten und
schrieb diese Summen erneut als posted-Journal. Zwei Zeilen auf dem fest
geratenen Konto 1000 hatten keine belegte Kontenidentitaet, keine fachliche
Gegenkontierung und keine kanonischen Betragsspalten/Hashstempel. Der
Abschluss konnte Nicht-Kassenjournale oder fruehere Abschlussjournale erneut
zaehlen; leere Tage erzeugten Nulljournale. Ein erfolgreicher Kassenabschluss
war damit weder durch Kassenbestand noch Bewertungsmodell nachgewiesen.
Die bestehende Kassenmaske sendet diesen Aufruf und zeigt HTTP-Fehler bereits
an. User erlaubt das Entfernen aller Entwicklungsaltlasten.

## Entscheidung

Den konkurrierenden Direktbuchungsweg einschliesslich Summierung und
festen Konten vollstaendig entfernen. Die noch konsumierte Aktion gibt
HTTP 409 mit fachlichem Grund, ohne Datenbankzugriff/Journal-DML/Commit.
Kein Adapter, Archiv oder Ersatzjournal aus erfundenen Konten. Der bewertete
Kassenabschluss bleibt ein offener Fachvertrag, keine neue Funktion in
 diesem Slice. Domain Pack und eigener OpenAPI-Routenausschnitt dokumentieren
409; globales OpenAPI-Refresh bleibt beim vorhandenen fremden Claim.

## Konsequenzen

Kein weiterer Scheinbeleg und keine Doppelbuchung durch wiederholten Aufruf.
Die Maske erreicht ihre bestehende Fehlerbehandlung und meldet keinen Erfolg.
Ein echter Abschluss benoetigt belegten Tenant/Kassenbestand, Gegenkonto,
exakte Bewertung und den zentralen Journal-/Perioden-/Transaktionsvertrag.
Tests pruefen 409 ohne Datenbankaufrufe, unveraenderten realen Journalbestand,
Wiederholung und OpenAPI ohne 200. Keine Migration oder Datenbereinigung:
fremde/alte gespeicherte Daten werden in diesem Slice nicht geloescht.
