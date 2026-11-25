---
title: Studio-made offene Routen — Hebung
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-25
description: Inventar und Create-Paritaet fuer Altmasken (Agrar, CRM, Finance).
---

# Studio-made offene Routen (2026-11-25)

## Inventar (main, `mask_route_migration_inventory.py`)

| Klasse | Anzahl |
|--------|--------|
| Routen gesamt | 1147 |
| runtime_wired | 1037 |
| legacy_wrapper (`createLegacyMaskPage`) | 35 |
| hand_built | 69 |
| legacy_mask_pattern (Routen) | 0 |
| ObjectPage/ListReport-Seiten (`*-legacy.tsx` u. a.) | 16 |

Qualitaetskatalog: [made-by-studio-qualitaetsversprechen.md](../architecture/uix/made-by-studio-qualitaetsversprechen.md).

## Erste Hebung

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/saatgut` (+ Stamm-Routen) | Detail native, Create → ObjectPage-Legacy | `creation` in SD + `createStammNativeDetailPage` ohne Legacy |
| `agrar/duenger` (+ Stamm-Routen) | wie oben | wie oben |
| `crm/lead-detail` Anlage | LeadMaskBuilder / LegacyLeadDetail | `UniversalNativeCreatePage` (`crm/lead`) |
| `finance/debitoren-stamm` | totgeladener Legacy-Import | native Detail + Capture `finance/debitoren/new` |

## Zweite Hebung (Batch 2)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `finance/bankkonto` (`bankkonten-stamm`) | Create → ObjectPage-Legacy (+ Client-IBAN-Lookup) | `creation` → POST `/api/v1/banken/konten`; IBAN-Pruefung serverseitig |
| `finance/kreditor` (`kreditoren-stamm`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/finance/creditors` (CreditorWrite-Felder) |
| `crm/opportunity` (`opportunity-detail`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/crm/opportunities/`; `tenant_id` optional im Schema |

Permission-Projektion (UI): `finance.bankkonto.*` / `finance.kreditor.*` → FINANCE_*; `crm.opportunity.*` → CRM_* / SALES_*.

## Noch offen (Folge)

- 35 `legacy_wrapper`-Routen (Admin-Suite, Agrar-Prozessmasken ohne SD-Create)
- Restliche `createStammNativeDetailPage(..., legacyImport)` (Einkauf-Anfrage/Angebot/Anlieferavis, Reklamation, …)
- Gate D Browser/Image pro Maske; Permission-Projektion nach Generatorlauf nachziehen

## Tests

```bash
python -m pytest tests/test_stamm_object_page_parent.py -q --noconftest -o addopts=
cd packages/frontend-web && npx vitest run \
  src/__tests__/pages/mask-objectpage-stamm-native-route.test.ts \
  src/__tests__/bank-account-form-contract.test.tsx \
  src/__tests__/components/mask-builder/screen-permissions.test.ts
```
