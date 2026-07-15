---
title: "Impact Note FEED-CORE-017"
type: reference
audience: [architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
---

# Impact Note FEED-CORE-017

## Scope

Additive Referenzdatenstrecke im bestehenden Agrar-/Rations-Optimization-
Container: UnitDefinition, NutrientDefinition, append-only Revisionen,
Decimal-Konvertierung, Read-/Conversion-API und native Meridian-ListReport.

## Betroffene Architektur

- Kein neuer Service oder Container; Eigentuemerschaft bleibt `domain/agrar`.
- Neuer Router unter dem bestehenden Prefix
  `/api/v1/agrar/rations-optimization/reference-data`.
- Additive Migration nach `feed_core_groups_20260715`; bestehende Tabellen und
  APIs bleiben unveraendert.
- ScreenDefinition → RenderPlan → UniversalMaskRuntime →
  UniversalMaskRenderer bleibt der einzige UI-Pfad.

## Kompatibilitaet und Rollback

Bestehende Solver-Felder werden in diesem Slice nicht umgedeutet. Der Adapter
folgt in `FEED-CORE-018`, wodurch Upgrade und Forward-Fix ohne Dual-Write moeglich
bleiben. Rollback entfernt nur neue Referenztabellen und die read-only Route.

## Nachweis

Property-/Boundary-, Migration-/Screen-, echte PostgreSQL-API- und RBAC-Tests;
Alembic Single-Head, Architekturdrift, Doku-Governance und Frontend-Typecheck.
