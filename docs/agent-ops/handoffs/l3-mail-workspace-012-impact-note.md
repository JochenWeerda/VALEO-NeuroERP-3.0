---
title: Architecture Impact Note L3-MAIL-WORKSPACE-012
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-MAIL-WORKSPACE-012

- **Domains:** CRM, DMS/Compliance, Platform
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-065](../../adr/adr-065-role-scoped-mail-workspace.md)
- **Containeraenderung:** keine
- **Datenmodell:** Rollenmessages, hashgebundene Anlagen und append-only Audit
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

SMTP-/Graph-Zustellung, Providerquittung und Virenscan sind externe Gates. Die
repo-seitige Queue behauptet keinen Versand, bevor ein Provider ihn bestaetigt.

## Checks

Sechs Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `mail_workspace_20260821` genau einen Head. OpenAPI (2.725 Pfade),
Route-Inventar (913/913), Agent-Handbuch (55 Masken), ADR-Navigation (70) und
Architekturindex sind aktuell; `arch:validate` und `arch:drift --strict` sind
gruen.
