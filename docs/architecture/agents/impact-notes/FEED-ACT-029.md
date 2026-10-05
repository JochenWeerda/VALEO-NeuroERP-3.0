---
title: "Impact Note FEED-ACT-029"
type: reference
audience: [architektur, agrar, frontend, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-ACT-029

## Scope

Additives ActualFeeding-Aggregat im Agrar-Container, planversionsgebundener
Command, Komponentenprojektion, CSV und Umstellung des mobilen Abschlusses.
Kein Schwellen-/Aufgabenaggregat und keine Aenderung am Einkaufscontainer.

## Architekturartefakte

- Migration `feed_actual_feeding_20260716`
- reine Decimal-Abweichungs- und Wertfolgeregeln
- append-only Service mit Idempotenz, Korrekturbezug und Outbox
- REST unter `/feeding/actuals`, Komponentenprojektion und CSV
- native Meridian-Audit-Worklist im Controlling
- mobile Plan-to-Actual-Journey ohne Legacy-`ration_ref`-Persistenz

## Sicherheit und Datenqualitaet

Server prueft Rolle, Tenant und Business-Grant. Sollwerte werden nie vom Client
uebernommen. Fehlende Preis-/Naehrstoffbasis bleibt explizite Datenluecke.
Advisory Lock und Request-Hash sichern Retry; DB-Trigger schuetzen Historie.

## UI-Vertrag

Die Desktopauswertung laeuft ueber ScreenDefinition, RenderPlan,
UniversalMaskRuntime und UniversalMaskRenderer. Tabellenprofil `audit` zeigt
Plan, Feed, Soll/Ist/Delta, Ursache, Wertfolgen und Luecken. Mobil bleibt die
touch-optimierte Stalljourney; ihr Abschluss schreibt ausschliesslich den neuen
ActualFeeding-Command.
