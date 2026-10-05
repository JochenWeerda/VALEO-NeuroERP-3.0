---
title: Architecture Impact Note L3-REPORT-CATALOG-014
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-REPORT-CATALOG-014

- **Domains:** Reporting, Finance, CRM, Inventory, Agrar
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-067](../../adr/adr-067-governed-l3-report-catalog.md)
- **Containeraenderung:** keine
- **Datenmodell:** tenantgebundene Reporting-Facts und Export-Audit
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Die fachliche Summenparitaet muss mit produktiven L3-/VALEO-Echtdaten im UAT
abgenommen werden. Der Repo-Vertrag liefert feste Dimensionen, reproduzierbare
Summen und nachvollziehbare Quellen, ersetzt aber keine fachliche Freigabe.

## Checks

Fuenf Backendtests, ein Frontendtest, TypeScript und Ruff sind gruen. Alembic
hat mit `l3_report_catalog_20260821` genau einen Head. OpenAPI (2.735 Pfade),
Route-Generator (915 TanStack-Routen), Agent-Handbuch (57 Masken),
ADR-Navigation (72) und Architekturindex sind aktuell; `arch:validate` und
`arch:drift --strict` sind gruen.
