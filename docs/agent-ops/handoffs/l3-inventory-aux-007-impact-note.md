---
title: Architecture Impact Note L3-INVENTORY-AUX-007
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-INVENTORY-AUX-007

- **Domains:** Inventory, Finance
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-060](../../adr/adr-060-governed-inventory-auxiliary-batches.md)
- **Containeraenderung:** keine
- **Datenmodell:** additive hashgebundene Batches und append-only Audit in `domain_inventory`
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Produktive Dateiablage, Druckeradapter und Pilotdaten bleiben extern. Die
repo-seitigen Hash-, Kontroll-, Bewertungs- und Vier-Augen-Vertraege sind davon
unabhaengig pruefbar.

## Checks

Die native Maske ist `generatorReady=true` mit Advisory-Score 1.0. Sechs
Backendtests und ein fokussierter Frontendtest sind gruen; TypeScript und Ruff
laufen ohne Fehler. Alembic hat mit `inventory_auxiliary_20260821` genau einen
Head. OpenAPI (2.703 Pfade), Route-Inventar (909/909), Agent-Handbuch (51
Masken), ADR-Navigation (65) und Architekturindex wurden regeneriert;
`arch:validate` und `arch:drift --strict` sind gruen.
