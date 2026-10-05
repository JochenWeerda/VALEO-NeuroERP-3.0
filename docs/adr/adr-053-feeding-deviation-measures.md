---
title: "ADR-053 Versionierte Abweichungsschwellen und menschliche Massnahmen"
type: adr
audience: [architektur, agrar, controlling, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-16
version: 1.0.0
---

# ADR-053 Versionierte Abweichungsschwellen und menschliche Massnahmen

**Status:** Accepted

**Datum:** 2026-07-16

## Kontext

Komponentenabweichungen waren bereits planversionsgebunden belegt, hatten aber
keine tenant- und Komponentenklassen-spezifische Bewertung. Eine universelle
stille 5-Prozent-Regel waere fachlich falsch. Ebenso darf ein technischer
Befund weder automatisch eine personengebundene Aufgabe erzeugen noch fehlende
IOFC-Eingaben als Nullwert ausgeben.

## Entscheidung

- `FeedingDeviationPolicy` ist je Tenant und Komponentenklasse versioniert.
  Warn- und Kritischgrenze sowie Gueltigkeitsbeginn und Pflichtgrund sind
  append-only; `critical_pct` muss groesser als `warning_pct` sein.
- Ein Finding ist eine deterministische Projektion aus Actual-Komponente,
  Planversion und der am Fuetterungstag gueltigen Policy. Ohne Policy lautet
  der Zustand explizit `unconfigured`.
- Nur ein menschlicher, berechtigter Command kann aus einem Warning/Critical-
  Finding eine `FeedingActualMeasure` mit Titel, Owner, Termin, Grund und
  Idempotency-Key erzeugen. Finding und Komponente werden im Nachweis
  eingefroren; Update und Delete sind verboten.
- IOFC wird nur bei vorhandener Milchmenge, Milchpreis und Futterkosten
  berechnet: `Milchmenge * Milchpreis - Futterkosten`. Formelinputs und
  Milchumsatz bleiben am Tagespunkt nachvollziehbar; sonst bleibt IOFC `null`.
- Jeder Tagespunkt referenziert die am Beobachtungstag gueltige
  `FeedingPlanVersion`. Die UI kennzeichnet Wechsel mit Textmarker und
  Versionsnummer, nicht allein durch Farbe.

## Konsequenzen

Schwellen koennen fachlich validiert und ohne Rueckwirkung fortgeschrieben
werden. Befund und menschliche Verantwortung bleiben getrennt. Historische
Trends sind reproduzierbar; fehlende Datenbasis wird nicht als wirtschaftliche
Null interpretiert.
