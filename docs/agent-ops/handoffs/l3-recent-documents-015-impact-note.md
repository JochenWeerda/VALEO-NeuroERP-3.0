---
title: Architecture Impact Note L3-RECENT-DOCUMENTS-015
type: reference
audience: [architektur, entwickler, qa, datenschutz]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-RECENT-DOCUMENTS-015

- **Domains:** Workspace, CRM, Finance, Einkauf, Sales, Inventory, Agrar, Quality
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-068](../../adr/adr-068-personal-authorized-recent-documents.md)
- **Containeraenderung:** keine
- **Datenmodell:** persoenliche, ablaufende Access-Projektion ohne Dokumentinhalt
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Datenschutz und externe Gates

Die Projektion ist kein globales Nutzungsprotokoll. Sie speichert nur die
minimalen Wiederfindungsmetadaten, prueft aktuelle Rollen und kann vom Benutzer
geleert werden. Eine betriebliche DSFA-/Retention-Abnahme bleibt extern.

## Checks

Sechs Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `l3_recent_documents_20260821` genau einen Head. OpenAPI (2.739 Pfade),
Route-Generator (916 TanStack-Routen), Agent-Handbuch (58 Masken),
ADR-Navigation (73) und Architekturindex sind aktuell; `arch:validate` und
`arch:drift --strict` sind gruen.
