---
title: "Impact Note FEED-PLAN-027"
type: reference
audience: [architektur, frontend, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-PLAN-027

## Scope und Architektur

Additive Read-Projektion `current/scheduled/stale`, native Meridian-ObjectPage,
druckfaehige Planprojektion und Umstellung der mobilen Stallroute auf
FeedingPlanVersion. Keine Planberechnung im Browser und keine parallele
Maskenarchitektur.

## Daten- und Sicherheitsvertrag

Der Server bestimmt den Status aus Gueltigkeit und einer wirksam gewordenen
neueren Version. `/current` liefert nur grant-sichere aktuelle Planversionen mit
Instructions. Mobile Cache-Eintraege tragen Version 2 und die Planversions-ID;
Legacy-Cache v1 wird ignoriert.

## UI-Vertrag und Grenzen

`agrar/feeding-plan` laeuft ueber ScreenDefinition, RenderPlan,
useUniversalMaskRuntime und UniversalMaskRenderer. Die Druckprojektion verwendet
dieselben Daten und enthaelt IDs, Herkunft, Gueltigkeit und Zeitstempel.
Stale/Scheduled sind Textzustand. Signierter Server-PDF-Job und profilierte
Berichtsvorlagen bleiben Berichts-Ausbau.
