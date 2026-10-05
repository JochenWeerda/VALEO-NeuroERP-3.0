---
title: ADR-041 Hybride Experience-Architektur der Fuetterungsberatung
type: adr
audience: [architektur, produkt, ux, entwickler]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-14
version: 1.0.0
---

# ADR-041 Hybride Experience-Architektur der Fuetterungsberatung

## Status

Accepted, 2026-07-14.

## Kontext

Die vorhandene Rationsseite vereint Einstieg, Wizard, Solver, Review, Diagnose und
Fuetterung in einer spezialisierten Frontenddatei. Das ist fuer simultane
Rationsrechnung leistungsfaehig, aber fuer Portalnutzer, Lifecycle-Worklists und
Controlling zu schwer. Eine vollstaendige Ueberfuehrung in generische Form- und
Tabellenrenderer wuerde andererseits den engen Solver-Feedbackzyklus verschlechtern.

## Entscheidung

Der kanonische Einstieg wird die native ScreenDefinition `agrar/feed-advice` und
durchlaeuft `ScreenDefinition -> RenderPlan -> useUniversalMaskRuntime ->
UniversalMaskRenderer`. Sie trennt Planung, Stallarbeit, Bestand, Analysen,
Rationslebenszyklus und Controlling als rollenbezogene Aufgaben.

Der Solver bleibt ein spezialisierter Task-Workspace, wird aber lazy und nur nach
expliziter Aufgabenwahl geladen. Er erhaelt keine eigenen Stammdaten-, Lifecycle-
oder Controlling-Schattenmodelle. Neue generische Anforderungen werden zuerst im
zentralen ScreenDefinition-Vertrag umgesetzt.

## Konsequenzen

- Der Portalstart wird schneller und leichter verstaendlich.
- Alle Cockpits verwenden kuenftig den UniversalMaskRuntime statt den Compiler
  direkt zu umgehen.
- Die interne Expertenroute bleibt waehrend der Migration funktionsgleich.
- Lifecycle und Controlling werden als native Folgemasken gebaut.
- Der Spezialarbeitsplatz ist eine bewusst begrenzte Ausnahme und muss schrittweise
  in Fachkomponenten zerlegt werden.

## Verworfene Alternativen

- **Monolith unveraendert:** zu hohe kognitive und technische Kopplung.
- **Vollstaendig generischer Solver:** unzureichend fuer simultane Tabellen-,
  Constraint- und Vorschauinteraktion.
- **Parallele Portal-Neuentwicklung:** wuerde Fachlogik und API-Pfade duplizieren.

