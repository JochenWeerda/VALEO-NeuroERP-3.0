---
title: Universal Mask Rollout Batch Waves 42–51
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Zehn Rollout-Kandidaten nach CRM/Sales/Agrar-Kontrakt mit screen-summary und Generic Pilot Route.
---

# Rollout Batch Waves 42–51

Nach den Pilots CRM 360, Sales Order und Agrar-Kontrakt (Waves 27–41) folgen **zehn weitere Kandidaten** mit dem gleichen Vertrag:

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
- Lazy Tab: `GET /api/v1/mask-rollouts/{screen_id}/{entity_id}/tabs/{tab_key}?page&limit`

Katalog: [`app/core/mask_rollout_catalog.py`](../../../app/core/mask_rollout_catalog.py)
Service: [`app/services/mask_rollout_summary_service.py`](../../../app/services/mask_rollout_summary_service.py)

## Frontend

- Generic Pilot: [`UniversalMaskRolloutPilotPage.tsx`](../../../packages/frontend-web/src/pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage.tsx)
- Route: `/mask-rollout/:screenId/:entityId` (`screenId` mit `__` statt `/`, z. B. `finance__ap-invoice`)
- Feature-Flag: `VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true`

## Abnahme

- pytest: `tests/test_mask_rollout_batch_w42_51.py`
- Vitest: `mask-rollout-route.test.tsx`
- Registry: `generator_ready=True` fuer alle zehn mask_ids

## Bewusste Grenzen

- Mutationen (Speichern, Freigabe, Neuanlage) bleiben auf Legacy-Masken.
- Tab-Tabellen nutzen generische Spaltenableitung aus API-Items (keine fachliche Feintuning-Matrix pro Domäne).
- Listenmasken ohne Detail-Route verlinken auf `/mask-rollout/...` statt eingebettetem Route-Switch.
