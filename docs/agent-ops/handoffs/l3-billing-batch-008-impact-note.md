---
title: Architecture Impact Note L3-BILLING-BATCH-008
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-BILLING-BATCH-008

- **Domains:** Finance, Agrar
- **Entscheidungsstufe:** Significant
- **ADR:** [ADR-061](../../adr/adr-061-billing-batch-orchestration.md)
- **Containeraenderung:** keine
- **Datenmodell:** additive Stapel, idempotente Zeilen und append-only Audit in `domain_finance`
- **UI-Kette:** `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`

## Externe Gates

Providerzustellung, fiskalische Pilotabnahme und Echtdaten-UAT bleiben extern.
Die vorhandenen Rechnungs-/Self-Billing-Services bleiben Eigentumer der
Dokument-, DQ-, GoBD- und Buchungslogik.

## Checks

Die native Maske ist `generatorReady=true` mit Advisory-Score 1.0. Sechs
Backendtests und ein fokussierter Frontendtest sind gruen; TypeScript und Ruff
laufen ohne Fehler. Alembic hat mit `billing_batch_20260821` genau einen Head.
OpenAPI (2.710 Pfade), Route-Inventar (910/910), Agent-Handbuch (52 Masken),
ADR-Navigation (66) und Architekturindex wurden regeneriert; `arch:validate`
und `arch:drift --strict` sind gruen.
