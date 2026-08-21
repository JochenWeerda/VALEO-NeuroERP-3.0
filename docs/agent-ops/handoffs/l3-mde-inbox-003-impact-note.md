---
title: Architecture Impact Note L3-MDE-INBOX-003
type: reference
audience: [architektur, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-08-21
version: 1.0.0
---

# Architecture Impact Note L3-MDE-INBOX-003

## Meta

- **Slice / Ticket:** L3-MDE-INBOX-003
- **Domain(s):** Platform/Integration, Inventory, Agrar, Logistics
- **Entscheidungsstufe:** Significant
- **Agent / Autor:** Codex

## Aenderung

Der vorhandene Mobile-Sync-Kern wird als kanonischer MDE-Eingang gehaertet
und durch eine native, serverseitig paginierte Meridian-Worklist bedienbar.
Fachliche Handler und Domaenengrenzen bleiben unveraendert.

## Betroffene Artefakte

- [x] Code (`app/`, `packages/`)
- [ ] `docs/architecture/c4/workspace.dsl` (kein neuer Container/Systemrand)
- [x] `config/architecture-index.yaml` (Generator)
- [x] Domain Pack (`docs/architecture/domains/inventory/`)
- [x] ADR ([ADR-057](../../adr/adr-057-mde-inbox-on-mobile-sync-core.md))
- [x] Tests
- [x] Process Kernel / Workboard

## Drift-Check

```bash
pnpm arch:validate
pnpm arch:drift
```

Ergebnis 2026-08-21: `arch:render`, `arch:validate` und `arch:drift` sind gruen.
Der Index ordnet 906/906 Routen, 210/210 Services und 406/406 Endpoints zu.
OpenAPI (2687 Pfade), ADR-Navigation (62 ADRs) und Agent-Handbuch (47 Masken)
sind regeneriert und driftfrei. 35 Backend-Tests, 10 fokussierte Frontend-Tests
und der vollstaendige TypeScript-Check sind gruen. Alembic weist genau den
neuen Head `mde_inbox_hardening_20260821` aus.

## Offene Risiken / Follow-ups

- Reale Geraete-/Providerformate benoetigen Adaptermapping und Pilotdaten.
- Produktive Scheduler-Frequenz und Alarmierung sind je Mandant festzulegen.
