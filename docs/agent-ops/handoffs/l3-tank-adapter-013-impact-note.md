---
title: Architecture Impact Note L3-TANK-ADAPTER-013
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-TANK-ADAPTER-013

- **Domains:** Agrar, Operations, Sales
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-066](../../adr/adr-066-tank-adapter-intake-outbox.md)
- **Containeraenderung:** keine
- **Datenmodell:** idempotente Intake-, Sales-Outbox- und Audit-Tabellen
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Reale Anlagenprotokolle und der produktive Sales-Consumer sind extern. Der
Outbox-Handover ist ein belastbarer, idempotenter Erzeugungsauftrag und keine
vorgetaeuschte Sales-Zustellung.

## Checks

Sechs Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `tank_adapter_20260821` genau einen Head. OpenAPI (2.730 Pfade),
Route-Inventar (914/914), Agent-Handbuch (56 Masken), ADR-Navigation (71) und
Architekturindex sind aktuell; `arch:validate` und `arch:drift --strict` sind
gruen.
