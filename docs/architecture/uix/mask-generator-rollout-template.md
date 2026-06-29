---
title: Universal Mask Generator — Domain Rollout Template
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-29
version: 1.1.0
description: Schritt-fuer-Schritt Template fuer Agrar, Inventory, Finance Mask-Piloten (useUniversalMaskRuntime-Muster ab Wave 42).
---

# Domain Rollout Template (Wave 40 / aktualisiert Wave 42)

Referenz-Slices: CRM (`UIX-CRM-PILOT-002`), Sales (`UIX-SALES-PILOT-007`), RenderPlan (`UIX-RENDER-PLAN-009`), Native Runtime (`UIX-NATIVE-RUNTIME-020`).

## Checkliste pro Domäne

1. **Registry:** `generator_ready: true` in [`app/core/mask_classification.py`](../../../app/core/mask_classification.py)
2. **Backend:** `GET /{entity}/screen-summary` (mit `tab_endpoints`, `available_tabs`) + `GET /tabs/{tab_key}?page&limit`
3. **ScreenDefinition:** Eintrag in [`app/core/screen_definitions.py`](../../../app/core/screen_definitions.py) mit `dataSources[]`, Tab-`tables` (inkl. `dataSourceKey`, `serverPagination: true`) und ggf. Lookup-`fields`
4. **Frontend Feature-Flag:** `VITE_ENABLE_UNIVERSAL_MASK_<DOMAIN>=true`
5. **Pilot-Page:** `useUniversalMaskRuntime` + `UniversalMaskRenderer plan={plan} lookupBindings={lookupBindings} tableQueryStates={tableQueryStates} tableTotals={tableTotals} onTableQueryChange={setTableQuery}`
6. **Paritätsmatrix:** `docs/architecture/domains/<domain>/mask-parity-*.md`
7. **Tests:** Vitest (RenderPlan + Runtime), pytest (screen-summary + ScreenDefinition-Struktur), Playwright smoke

## Rollout-Reihenfolge

1. CRM 360 (abgeschlossen — native Runtime ab UIX-NATIVE-RUNTIME-020)
2. Sales Order (abgeschlossen)
3. Agrar — Ernte/Contract (abgeschlossen: Kontrakt-Pilot Wave 41)
4. **Batch Waves 42–51** — zehn Kandidaten (Inventory, Finance, Einkauf, CRM, Sales, Agrar Settlement) — siehe [`mask-rollout-batch-w42-51.md`](mask-rollout-batch-w42-51.md)
5. Inventory — Bestand/Lagerbewegung (in Batch enthalten)
6. Finance — AP/AR Object Pages (in Batch enthalten)

## Datei-Vorlage (ab Wave 42)

```
app/core/screen_definitions.py          ← dataSources[], Tab-tables, Fields erweiterter Eintrag
tests/test_<entity>_screen_definition.py ← strukturelle Pruefung dataSources, serverPagination

packages/frontend-web/src/pages/<domain>/Universal<Entity>PilotPage.tsx
packages/frontend-web/src/__tests__/pages/<domain>/universal-<entity>-pilot.test.tsx
packages/frontend-web/tests/e2e/<domain>-universal-*-pilot.spec.ts
```

> Legacy-Dateien `<entity>-tab-tables.ts` und `use-<entity>-tab-data.ts` werden nicht mehr benoetigt — `useUniversalMaskRuntime` uebernimmt Entity-Query, Table-Queries und Lookup-Bindings vollstaendig.

## Minimalbeispiel Pilot-Page

```tsx
const { plan, entityData, tableRows, tableTotals, tableQueryStates, setTableQuery, lookupBindings, isEntityLoading, entityError } =
  useUniversalMaskRuntime({
    screenId: 'crm/customer-360',
    entityId: id,
    schema: nativeScreenQuery.data,
    tabEndpoints: summaryQuery.data?.tab_endpoints,
    availableTabs: summaryQuery.data?.available_tabs,
    summaryTitle: summaryQuery.data?.title,
    summarySubtitle: summaryQuery.data?.subtitle,
    summaryItems,
    enabled: Boolean(id && nativeScreenQuery.data),
  })

return plan ? (
  <UniversalMaskRenderer
    plan={plan}
    data={entityData}
    tables={tableRows}
    tableTotals={tableTotals}
    tableQueryStates={tableQueryStates}
    onTableQueryChange={setTableQuery}
    lookupBindings={lookupBindings}
    onAction={() => undefined}
  />
) : null
```

## Performance-Pflicht

- `compileRenderPlan` statt Page-`useMemo`-Merge
- Lazy Tabs only
- `serverPagination: true` in ScreenDefinition + `onTableQueryChange` in Renderer (kein client-seitiges Slice)
- Lookup min 2 Zeichen; `lookupEndpoint` kommt aus `dataSources` via `compileDataBindingPlan`
