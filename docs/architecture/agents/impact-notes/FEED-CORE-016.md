---
title: "Architecture Impact Note FEED-CORE-016"
type: reference
audience: [architektur, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
---

# Architecture Impact Note FEED-CORE-016

## Meta

- **Slice / Ticket:** FEED-CORE-016
- **Domain:** Agrar / Fuetterungsberatung
- **Entscheidungsstufe:** Significant
- **Autor:** Codex

## Aenderung

Bestehendes `feeding_groups`-Aggregat additiv um typisierte Parameter,
Gueltigkeit, optimistische Revision, append-only Historie und Business-Grant-
Scoping erweitert. Neue Detail-/Update-/History-Vertraege sowie native
Meridian-ObjectPage; kein neuer Container oder Bounded Context.

## Betroffene Artefakte

- [x] Code und additive Alembic-Migration
- [ ] C4/`workspace.dsl` — keine Container-/Grenzaenderung
- [ ] Architecture Index — bestehende Prefixe und Container
- [x] Agrar Domain Pack
- [x] ADR-045 (proposed)
- [x] Backend-/Frontend-/Governance-Tests
- [x] Workboard/Slice/Feeding-Referenzwerk

## Drift-Check

Vor Abschluss: `pnpm arch:validate`, `pnpm arch:drift`, Agent-Handbuch-Check,
Alembic-Single-Head sowie fokussierte Domain/API/Screen-/Frontend-Gates.

## Offene Risiken

Tierindividuelle Mitgliedschaften bleiben FEED-HERD-003. Businesslose
Legacygruppen benoetigen den kontrollierten Betriebs-Backfill.
