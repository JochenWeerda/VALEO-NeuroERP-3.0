---
title: RenderPlan Architecture
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-29
version: 1.2.0
description: Performance-orientierte Rendering-Engine — SchemaCompiler, RenderPlan-Cache, Fast Renderer, UniversalMaskRuntime, Readiness-Gates.
---

# RenderPlan Architecture

Kanonische Referenz fuer Waves 33–40 (UIX-RENDER-PLAN-009 ff.) und Adapter-Paritaet (UIX-NATIVE-RUNTIME-020).

## Prinzip

MaskSchema wird **einmal** pro Cache-Key in einen flachen `RenderPlan` uebersetzt. React rendert den Plan — es interpretiert kein JSON mehr zur Laufzeit. Der `DataBindingPlan` loest `dataSources[]`-Templates zur Laufzeit auf und verbindet Tabellen mit ihren Server-Endpunkten.

```text
ScreenDefinition + SummaryContext + AuthContext
        ↓
SchemaCompiler (compileRenderPlan)
        ↓
RenderPlanCache (LRU, max 50)
        ↓
compileDataBindingPlan (dataSources[] + entityId → Endpunkte)
        ↓
useUniversalMaskRuntime
  ├── entityQuery      (useQuery, entity-Endpunkt)
  ├── tableQueries     (useQueries, je Tabelle mit serverPagination)
  └── lookupBindings   (LookupBindingContext → FastFormRenderer)
        ↓
UniversalMaskRenderer + Fast*Renderer
```

## Module

### Compiler-Schicht (`render-plan/`, `hooks/`)

| Pfad | Aufgabe |
|------|---------|
| `render-plan/types.ts` | RenderPlan-Typen |
| `render-plan/schema-compiler.ts` | Compiler + Cache-Integration |
| `render-plan/cache.ts` | LRU-Cache |
| `render-plan/compile-context.ts` | Cache-Key (screenId, schemaVersion, tenant, role, permissions, flags) |
| `render-plan/plan-to-screen.ts` | Übergang: RenderPlan → ScreenDefinition |
| `hooks/useRenderPlan.ts` | React-Hook fuer Pilot-Pages |

### Runtime-Schicht (`runtime/`)

| Pfad | Aufgabe |
|------|---------|
| `runtime/types.ts` | `DataBindingPlan`, `TableQueryState`, `TableBinding`, `LookupBinding`, `EntityBinding`, `TablePageResponse` |
| `runtime/data-source-resolver.ts` | Template-Substitution: `{entity_id}` → Wert |
| `runtime/table-query-state.ts` | `defaultTableQueryState`, `hasContentChange`, `toQueryParams` |
| `runtime/compile-data-binding-plan.ts` | `RenderPlan` + `dataSources[]` + `entityId` → `DataBindingPlan` |
| `runtime/LookupBindingContext.ts` | React Context; `LookupBindingProvider`, `useLookupBindings()` |
| `runtime/useUniversalMaskRuntime.ts` | Master-Hook: Plan, Entity-Query, Table-Queries, Lookup-Bindings |

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

## DataBindingPlan-Regeln

- **Entity**: `dataSources.find(d => d.key === 'entity')` → `resolveEndpoint(template, {entity_id, tenant_id})`
- **Tabellen**: zuerst `dataSources[dataSourceKey]`, Fallback auf `tabEndpoints[tabKey]`; Tabellen ohne aufloesbaren Endpunkt werden stillschweigend uebersprungen (kein throw)
- **Lookups**: Felder mit `componentKind === 'lookup'` und passendem `dataSourceKey`; Abfragestring (`?q=...`) wird abgeschnitten — `useLookupSearch` fuegt `q` zur Laufzeit hinzu
- **Merge-Fix**: `use-pilot-render-plan.ts` behaelt native `tabs`/`fields`/`dataSources` wenn `adapter.temporary !== true`

## Renderer-Verdrahtung (opt-in)

`FastTableRenderer` und `FastTabRenderer` akzeptieren optionale Props `total`, `page`, `onQueryChange`. Wenn `serverPagination === true` und `onQueryChange` gesetzt, entfaellt das client-seitige Slice; Vor-/Zurueck-Controls werden eingeblendet. `FastFormRenderer` liest `lookupEndpoint` aus `LookupBindingContext`.

## Performance-Vertrag

Siehe ADR-011 Erweiterung RenderPlan Engine und `scripts/check_mask_performance_contract.ts` + `scripts/check_mask_bundle_budget.ts`.

## Runtime-Schicht (UIX-021…033)

| Modul | Aufgabe |
|-------|---------|
| `runtime/useUniversalFormState.ts` | Form-Werte, Dirty, Validierung, Submit-Guard |
| `runtime/useActionRuntime.ts` | Actions: execute/dryRun/validate/propose, Audit, Idempotenz |
| `runtime/useWorkflowState.ts` | Workflow-Panel, BlockingReasons |
| `runtime/generateAgentMaskContract.ts` | Agent-Vertrag aus ScreenDefinition |
| `runtime/generatorReadiness.ts` | 6 mandatory + 6 advisory Gates pro Tabelle |

Backend-Spiegel: `GET /api/v1/masks/{id}/readiness`, `GET /api/v1/masks/{id}/agent-contract`.

Tab-API-Query (Rollouts + CRM): `page`, `limit`, `q`, `sort`, `sort_dir`, `filter_plan` — Sort/Filter nur gegen Whitelist aus ScreenDefinition.

Plattformstatus und Governance: [`universal-mask-runtime-status.md`](universal-mask-runtime-status.md).
