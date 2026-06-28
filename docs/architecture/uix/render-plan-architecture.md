---
title: RenderPlan Architecture
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Performance-orientierte Rendering-Engine — SchemaCompiler, RenderPlan-Cache, Fast Renderer.
---

# RenderPlan Architecture

Kanonische Referenz fuer Waves 33–40 (UIX-RENDER-PLAN-009 ff.).

## Prinzip

MaskSchema wird **einmal** pro Cache-Key in einen flachen `RenderPlan` uebersetzt. React rendert den Plan — es interpretiert kein JSON mehr zur Laufzeit.

```text
ScreenDefinition + SummaryContext + AuthContext
        ↓
SchemaCompiler (compileRenderPlan)
        ↓
RenderPlanCache (LRU, max 50)
        ↓
UniversalMaskRenderer + Fast*Renderer
```

## Module

| Pfad | Aufgabe |
|------|---------|
| `render-plan/types.ts` | RenderPlan-Typen |
| `render-plan/schema-compiler.ts` | Compiler + Cache-Integration |
| `render-plan/cache.ts` | LRU-Cache |
| `render-plan/compile-context.ts` | Cache-Key (screenId, schemaVersion, tenant, role, permissions, flags) |
| `render-plan/plan-to-screen.ts` | Übergang: RenderPlan → ScreenDefinition |
| `hooks/useRenderPlan.ts` | React-Hook fuer Pilot-Pages |

## Cache-Key

```text
screenId::schemaVersion::tenantId::roleHash::permissionHash::featureFlagHash
```

Invalidierung bei Logout oder `schemaVersion`-Wechsel.

## Compiler-Regeln

- Actions: Permission-Filter im Compiler
- Tabs: Schnittmenge Schema ∩ `summary.available_tabs`
- Tabellen: `virtualized: true`, `pageSize ≤ 50`, `serverPagination: true`
- Lookups: min 2 Zeichen, max 25 Treffer, Cache 15min, Debounce 300ms

## Performance-Vertrag

Siehe ADR-011 Erweiterung RenderPlan Engine und `scripts/check_mask_performance_contract.ts` + `scripts/check_mask_bundle_budget.ts`.
