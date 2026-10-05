---
title: Architecture Impact Note L3-ROHWARE-OPERATOR-009
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-ROHWARE-OPERATOR-009

- **Domains:** Inventory, Einkauf, Agrar
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-062](../../adr/adr-062-foreign-goods-operator-projection.md)
- **Containeraenderung:** keine
- **Datenmodell:** additiver append-only Audit auf kanonischer Fremdwarenquelle
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Lagerpilot, Druckerprofil und Echtdaten-UAT bleiben extern. Die bestehende
Fremdwaren-Einlagerung bleibt Eigentumer der Bestandsdaten.

## Checks

Sechs fokussierte Backendtests, ein Frontendtest, TypeScript und Ruff sind
gruen. Alembic hat mit `foreign_goods_worklist_20260821` genau einen Head.
OpenAPI (2.714 Pfade), Route-Inventar (911/911), Agent-Handbuch (53 Masken),
ADR-Navigation (67) und Architekturindex sind aktuell; `arch:validate` und
`arch:drift --strict` sind gruen.
