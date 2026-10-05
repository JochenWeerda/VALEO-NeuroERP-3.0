---
title: Architecture Impact Note L3-QUERY-CENTER-010
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-QUERY-CENTER-010

- **Domains:** Reporting, Finance, Platform
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-063](../../adr/adr-063-safe-user-query-center.md)
- **Containeraenderung:** keine
- **Datenmodell:** tenant-/benutzergebundene Definitionen und append-only Audit
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Sicherheitsgrenze

Es gibt keinen SQL-Vertrag. Datenprodukt, Felder, Filter und Aggregationen
muessen die serverseitige Allowlist passieren; Vorschauen enden bei 200 Zeilen.
Importe werden signatur- und allowlistgeprueft.

## Checks

Sechs Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `query_center_20260821` genau einen Head. OpenAPI (2.719 Pfade),
Route-Inventar (912/912), Agent-Handbuch (54 Masken), ADR-Navigation (68) und
Architekturindex sind aktuell; `arch:validate` und `arch:drift --strict` sind
gruen.
