---
title: Architecture Impact Note L3-LEGACY-INTERFACES-017
type: reference
audience: [architektur, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-LEGACY-INTERFACES-017

- **Domains:** Integration, Finance, Inventory, Agrar
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-069](../../adr/adr-069-gated-l3-standard-unimet-adapters.md)
- **Containeraenderung:** keine
- **Datenmodell:** Profil, Intake-Batch, kanonisches Staging und append-only Audit
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Aktivierungs-Gates

Produktivbetrieb erfordert reale Standard-/Unimet-Dateien, Format- und
Mappingabnahme, Zielsystemvertrag, Datenschutz-/Betriebsfreigabe und Pilot.
Bis dahin ist jede API-/UI-Antwort explizit nicht-ausfuehrend.

## Checks

Sieben Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `l3_legacy_interfaces_20260821` genau einen Head. OpenAPI (2.746 Pfade),
Route-Generator (917 TanStack-Routen), Agent-Handbuch (59 Masken),
ADR-Navigation (74) und Architekturindex sind aktuell; `arch:validate` und
`arch:drift --strict` sind gruen.
