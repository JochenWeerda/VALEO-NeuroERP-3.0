---
title: Architecture Impact Note L3-HABIT-BRIDGE-001
type: reference
audience: [architektur, entwickler, qa, agent]
owner: Codex
status: accepted
last_reviewed: 2026-08-19
version: 1.0.0
---

# Architecture Impact Note L3-HABIT-BRIDGE-001

## Meta

- **Slice / Ticket:** L3-HABIT-BRIDGE-001
- **Domains:** UIX-Plattform, CRM, Sales, Inventory
- **Entscheidungsstufe:** Significant
- **Agent / Autor:** Codex

## Aenderung

Der Single Mask Builder erhaelt additive, herstellerneutrale Vertraege fuer
Aktionszonen, Sticky-Regionen, Summary-Position, deklarative Tastaturaktionen
und Enter-Fokus. Die drei Referenz-ScreenDefinitions `crm/customer-360`,
`lager/article-stock` und `sales/delivery-note` aktivieren diese Vertraege.

## Betroffene Artefakte

- [x] Code (`app/`, `packages/`)
- [ ] C4-Container oder Servicegrenzen
- [x] `config/architecture-index.yaml`
- [x] Domain Packs CRM/Inventory
- [x] ADR-056 (Proposed)
- [x] Unit-, Component-, Backend- und Visual-Vertraege
- [x] Workboard und Slice

## Drift-Check

`pnpm arch:validate` und `pnpm arch:drift` sind gruen (905/905 Routen,
210/210 Services, 406/406 Endpoints). Es gibt keine neue API-Route, keinen
Container und keine Domaenengrenzen-Aenderung. Der generierte
Architekturindex enthaelt ADR-056.

## Technische Abnahme

- Mask-Builder/RenderPlan: 125 Tests gruen; gezielte neue Vertraege 16/16.
- Backend-ScreenDefinitions und Readiness: 4/4 Tests gruen.
- Meridian-Visual-Audit: 12/12 bei 1366, 1440 und 1920 Pixeln gruen.
- TypeScript, Production-Build, Architecture-Validierung/-Drift und
  Agent-Handbuch-Drift sind gruen.

## Risiken und Gates

- Originalbilder enthalten Echtdaten und bleiben ausserhalb des Repositories.
- Fachliche Pilotabnahme durch erfahrene L3-Anwender ist extern.
- Weitere maskenspezifische Aktionen werden erst nach vorhandenem Command- und
  Berechtigungsvertrag deklariert.
