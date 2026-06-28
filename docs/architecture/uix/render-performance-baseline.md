---
title: Mask Render Performance Baseline
type: reference
audience: [agent, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Baseline fuer RenderPlan-Performance (Shell, Lazy Tabs, Bundle).
---

# Mask Render Performance Baseline

Stand: 2026-06-28 (Wave 38 / UIX-PERF-MEASURE-014)

## Zielmetriken

| Metrik | Ziel | Nachweis |
|--------|------|----------|
| Initial Requests | Summary (+ optional screen-definition) | Playwright `mask-render-performance.spec.ts` |
| Tab API | Erst nach Tab-Klick | Playwright CRM smoke |
| DOM-Zeilen Tabelle | ≤ 60 (virtualisiert) | Playwright Sales smoke |
| Registry-Vertrag | lazy tabs, lookup ≥ 2 | `check_mask_performance_contract.ts` |
| Bundle total JS | ≤ 4096 KB gzip (gesamt dist) | `check_mask_bundle_budget.ts` |
| Größter Chunk | ≤ 512 KB gzip | `check_mask_bundle_budget.ts` |

## Pilot-Routen

- CRM: `/crm/kunden-stamm-modern/:id` — `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true`
- Sales: `/sales/order-editor/:id` — `VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER=true`

## Messung lokal

```bash
# Verhaltens-Smoke (lazy tabs, virtual table) — aktiv
cd packages/frontend-web
pnpm build
cd ../..
npx ts-node scripts/check_mask_bundle_budget.ts
VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true npx playwright test tests/e2e/mask-render-performance.spec.ts
```

## A/B PoC Legacy vs. RenderPlan — geparkt

**Status:** geparkt (2026-06-28) — wartet auf stabile Frontend-Baseline nach 428-Fehler-Fix.

Vorbereitet, aber noch nicht als Proof-of-Concept abgeschlossen:

- Playwright: `tests/e2e/mask-render-ab-benchmark.spec.ts` (standardmaessig `test.skip`, Opt-in via `MASK_AB_BENCHMARK=1`)
- Benchmark-Route: `/dev/mask-benchmark/:domain/:variant/:id`
- Skript: `pnpm benchmark:mask-render-ab` (schreibt nach `evidence/perf/mask-render-ab.latest.json`)

Aktivierung wenn Baseline gruen:

```bash
MASK_AB_BENCHMARK=1 pnpm benchmark:mask-render-ab
```
