---
title: ADR-044 Kanonische Tagesbeobachtungen für das Fütterungscontrolling
type: adr
audience: [architektur, fachlich, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-14
version: 1.0.0
---

# ADR-044 Kanonische Tagesbeobachtungen für das Fütterungscontrolling

## Status

Accepted, 2026-07-14.

## Kontext

Sollwerte lagen im Solver, Istwerte in manueller Dokumentation, Herdsystemen oder
Mischwagen. Ohne gemeinsamen Zeit- und Gruppenschlüssel waren Aufnahme, Kosten,
Milch/ECM, Stickstoff und Methan weder reproduzierbar noch vergleichbar.

## Entscheidung

Das Controlling speichert eine tenantgebundene Tagesbeobachtung je Gruppe,
Quelle und stabiler Quellenreferenz. Wiederholte Importe sind idempotente Upserts.
Die bei Erfassung aktive unveränderliche Rationsversion liefert die Sollwerte und
wird am Datensatz referenziert. Unbekannte Messwerte bleiben `null`.

ECM wird nur aus Milchmenge, Fett und Eiweiß berechnet. N-Effizienz wird nur aus
Milchprotein-N und gemessener Futter-N-Aufnahme berechnet. Methan wird nicht
automatisch geschätzt; ein Schätzwert muss explizit als solcher markiert werden.
Providerdaten münden über denselben Vertrag, sobald ihr lizensiertes Mapping
vorliegt.

Die native ScreenDefinition `agrar/feed-controlling` zeigt 30-Tage-Soll-Ist-
Abweichungen und erlaubt eine kompakte manuelle Tageserfassung.

## Konsequenzen

- Kennzahlen sind gruppen-, versions-, quellen- und zeitbezogen nachvollziehbar.
- Fehlende Werte werden nicht mit Null oder erfundenen Schätzungen vermischt.
- DDW-, MLP- und Mischwagenadapter können später idempotent einspeisen.
- Eine spätere Aggregationsschicht kann dieselbe kanonische Serie verwenden.

