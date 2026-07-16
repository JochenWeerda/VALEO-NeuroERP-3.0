---
title: "Impact Note FEED-ACT-030"
type: reference
audience: [architektur, agrar, frontend, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-16
version: 1.0.0
---

# Impact Note FEED-ACT-030

## Scope

Additive, versionierte Abweichungspolicies und append-only Massnahmen fuer
komponentenbezogene Ist-Fuetterungen sowie IOFC und Planversionsmarker im
Tagescontrolling. Kein automatischer Task, kein universeller Default und kein
neuer Workflow-/CRM-Kern.

## Architekturartefakte

- Migration `feed_actual_measures_20260716`
- reine Decimal-Regeln fuer Schwellen und IOFC
- tenant-/grant-sicherer Service fuer Policies, Findings und Massnahmen
- REST unter `/feeding/actuals/deviation-policies`, `/findings` und `/measures`
- planversionsgebundene Erweiterung von `feeding_controlling_daily`
- Meridian-Worklist mit schmalen Domain-Overlays fuer bewusste Commands

## Sicherheits- und Auditwirkung

Server erzwingt READ/WRITE/APPROVE-Rollen, Tenant und Business-Grant.
Massnahmen verlangen Owner, Termin, Grund und Idempotency-Key. Trigger
verhindern Mutation oder Loeschung der Policy- und Massnahmenhistorie.

## UI-Vertrag

Die Auswertung bleibt in ScreenDefinition, RenderPlan,
`useUniversalMaskRuntime` und `UniversalMaskRenderer`. Findings,
Konfigurationsluecken und offene Massnahmen sind native Tabellen; nur der
explizite Massnahmen- bzw. Policy-Command wird als schmales Dialog-Overlay
erfasst. Versionswechsel im Trend sind zusaetzlich als Text lesbar.
