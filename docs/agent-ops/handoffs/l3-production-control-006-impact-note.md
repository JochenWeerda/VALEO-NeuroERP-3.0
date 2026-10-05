---
title: Architecture Impact Note L3-PRODUCTION-CONTROL-006
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-PRODUCTION-CONTROL-006

- **Domains:** Agrar, Inventory
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-059](../../adr/adr-059-production-control-projection.md)
- **Containeraenderung:** keine; vorhandener Backend-/Frontend-/Postgres-Rand
- **Datenmodell:** additive Operationsprojektion und append-only Audit in `domain_ops`
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Physische Muehlen-/SPS-Anbindung, reale Schichtplanung und Anlagenpilot bleiben
adapter- bzw. standortgebundene Gates. Der repo-seitige Lifecycle erzeugt keine
direkten Maschinenbefehle.

## Checks

Die native Maske ist `generatorReady=true` mit Advisory-Score 1.0. Sechs
Backendtests und ein fokussierter Frontendtest sind gruen; TypeScript und Ruff
laufen ohne Fehler. Alembic hat mit `production_control_20260821` genau einen
Head. OpenAPI (2.700 Pfade), Route-Inventar (908/908), Agent-Handbuch (50
Masken), ADR-Navigation (64) und Architekturindex wurden regeneriert;
`arch:validate` und `arch:drift --strict` sind gruen.
