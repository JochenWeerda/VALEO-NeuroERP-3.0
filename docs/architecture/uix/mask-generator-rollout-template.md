---
title: Universal Mask Generator — Domain Rollout Template
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Schritt-fuer-Schritt Template fuer Agrar, Inventory, Finance Mask-Piloten.
---

# Domain Rollout Template (Wave 40)

Referenz-Slices: CRM (`UIX-CRM-PILOT-002`), Sales (`UIX-SALES-PILOT-007`), RenderPlan (`UIX-RENDER-PLAN-009`).

## Checkliste pro Domäne

1. **Registry:** `generator_ready: true` in [`app/core/mask_classification.py`](../../../app/core/mask_classification.py)
2. **Backend:** `GET /{entity}/screen-summary` + `tab_endpoints` + `GET /tabs/{tab_key}?page&limit`
3. **ScreenDefinition:** Eintrag in [`app/core/screen_definitions.py`](../../../app/core/screen_definitions.py)
4. **Frontend Feature-Flag:** `VITE_ENABLE_UNIVERSAL_MASK_<DOMAIN>=true`
5. **Pilot-Page:** `usePilotRenderPlan` + `useMaskPilotState` + `UniversalMaskRenderer plan={plan}`
6. **Paritätsmatrix:** `docs/architecture/domains/<domain>/mask-parity-*.md`
7. **Tests:** Vitest (RenderPlan), pytest (screen-summary), Playwright smoke

## Rollout-Reihenfolge

1. CRM 360 (abgeschlossen)
2. Sales Order (abgeschlossen)
3. Agrar — Ernte/Contract (nächster Kandidat)
4. Inventory — Bestand/Lagerbewegung
5. Finance — AP/AR Object Pages

## Datei-Vorlage

```
packages/frontend-web/src/features/<domain>-masks/
  <entity>-mask-support.ts
  <entity>-tab-tables.ts
  use-<entity>-tab-data.ts
packages/frontend-web/src/pages/<domain>/Universal<Entity>PilotPage.tsx
tests/test_<entity>_screen_summary.py
packages/frontend-web/tests/e2e/<domain>-universal-*-pilot.spec.ts
```

## Performance-Pflicht

- `compileRenderPlan` statt Page-`useMemo`-Merge
- Lazy Tabs only
- VirtualDataTable + server paging
- Lookup min 2 Zeichen
