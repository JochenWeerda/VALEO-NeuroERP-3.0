---
title: Universal Mask Rollout Batch Waves 42–51
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-29
version: 2.0.0
description: Zehn Rollout-Kandidaten nach CRM/Sales/Agrar-Kontrakt — Runtime-Plattform, API-Vertrag, Governance.
---

# Rollout Batch Waves 42–51

Nach den Pilots CRM 360, Sales Order und Agrar-Kontrakt (Waves 27–41) folgen **zehn weitere Kandidaten** mit dem gleichen Vertrag. Ab **UIX-RUNTIME-021** laufen alle über `useUniversalMaskRuntime` (nicht mehr `usePilotRenderPlan` + domänenspezifische Tab-Hooks).

| Wave | screen_id | Registry mask_id | Fachbereich |
|------|-----------|------------------|-------------|
| 42 | `lager/stock-movement` | `lager/stock-movement` | Lagerbewegung |
| 43 | `lager/article-stock` | `lager/article-stock` | Artikelbestand |
| 44 | `finance/ap-invoice` | `finance/ap-invoice-form` | Eingangsrechnung |
| 45 | `finance/ar-open-item` | `finance/op-debitoren` | OP Debitoren |
| 46 | `einkauf/purchase-order` | `einkauf/bestellung-stamm` | Bestellung |
| 47 | `einkauf/supplier` | `einkauf/lieferanten-stamm` | Lieferant |
| 48 | `crm/opportunity` | `crm/opportunity-detail` | Opportunity |
| 49 | `sales/delivery-note` | `sales/delivery-note` | Lieferschein |
| 50 | `agrar/harvest-settlement` | `agrar/harvest-settlement` | Ernte-Abrechnung |
| 51 | `finance/payment-run` | `finance/zahlungslauf-kreditoren` | Zahlungslauf |

## API

- Summary: `GET /api/v1/mask-rollouts/{screen_id}/{entity_id}/screen-summary`
- Lazy Tab: `GET /api/v1/mask-rollouts/{screen_id}/{entity_id}/tabs/{tab_key}`
  - Query: `page`, `limit` (max 50), `q`, `sort`, `sort_dir`, `filter_plan` (JSON)
  - Fehlerhafte `filter_plan`-JSON → **422**
- Sort/Filter-Whitelist aus `ScreenDefinition` via `get_sortable_columns` / `get_filterable_columns`

Katalog: [`app/core/mask_rollout_catalog.py`](../../../app/core/mask_rollout_catalog.py)
Service: [`app/services/mask_rollout_summary_service.py`](../../../app/services/mask_rollout_summary_service.py)

## Frontend

- Generic Pilot: [`UniversalMaskRolloutPilotPage.tsx`](../../../packages/frontend-web/src/pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage.tsx)
- Hook: `useUniversalMaskRuntime` + `UniversalMaskRenderer`
- Route: `/mask-rollout/:screenId/:entityId` (`screenId` mit `__` statt `/`, z. B. `finance__ap-invoice`)
- Feature-Flag: `VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true`

## Readiness & Agent

- `GET /api/v1/masks/{mask_id}/readiness` — Generator-Readiness-Gates (UIX-030/033)
- `GET /api/v1/masks/{mask_id}/agent-contract` — AgentMaskContract (UIX-029)
- Plattformstatus: [`universal-mask-runtime-status.md`](universal-mask-runtime-status.md)

## Abnahme

- pytest: `tests/test_mask_rollout_batch_w42_51.py` (24 Tests)
- pytest: `tests/test_agent_mask_contract.py` (Agent + Readiness)
- Vitest: `mask-rollout-route.test.tsx`, `generatorReadiness.test.ts`
- Registry: `generator_ready=True` für alle zehn mask_ids (gesetzt in BATCH-019; **keine weiteren** bis UIX-032+034)

## Governance (UIX-037)

Neu bewertete Rollout-Reihenfolge nach Stabilisierung:

1. `einkauf/supplier` → 2. `crm/opportunity` → 3. `lager/article-stock` → … → 10. `finance/payment-run` / `agrar/harvest-settlement` zuletzt

## Bewusste Grenzen

- Mutationen (Speichern, Freigabe, Neuanlage) bleiben auf Legacy-Masken.
- Tab-Tabellen nutzen generische/fachliche Spalten aus `_ROLLOUT_TAB_COLUMNS` — Feintuning pro Domäne in UIX-037.
- Listenmasken ohne Detail-Route verlinken auf `/mask-rollout/...` statt eingebettetem Route-Switch.
