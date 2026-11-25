---
title: Studio-made offene Routen — erste Hebung
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-25
description: Inventar und erste Create-Paritaet fuer Altmasken (Saatgut, Duenger, Lead, Debitoren).
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

## Erste Hebung (dieser Slice)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/saatgut` (+ Stamm-Routen) | Detail native, Create → ObjectPage-Legacy | `creation` in SD + `createStammNativeDetailPage` ohne Legacy |
| `agrar/duenger` (+ Stamm-Routen) | wie oben | wie oben |
| `crm/lead-detail` Anlage | LeadMaskBuilder / LegacyLeadDetail | `UniversalNativeCreatePage` (`crm/lead`) |
| `finance/debitoren-stamm` | totgeladener Legacy-Import | native Detail + Capture `finance/debitoren/new` |

## Noch offen (Folge)

- 35 `legacy_wrapper`-Routen (Admin-Suite, Agrar-Prozessmasken ohne SD-Create)
- Restliche `createStammNativeDetailPage(..., legacyImport)` ohne `creation` (Bankkonto, Kreditor, Opportunity, Einkauf-Anfrage/Angebot, …)
- Gate D Browser/Image pro Maske; Permission-Projektion fuer Agrar-POST nach Generatorlauf nachziehen

## Tests

```bash
python -m pytest tests/test_stamm_object_page_parent.py -q --noconftest -o addopts=
cd packages/frontend-web && npx vitest run \
  src/__tests__/pages/mask-objectpage-stamm-native-route.test.ts \
  src/__tests__/pages/batch11-native-list.test.ts \
  src/__tests__/pages/crm/native-party-route-contract.test.tsx
```
