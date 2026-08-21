---
title: Inventory — Tests
type: reference
audience: [qa]
owner: domain/inventory
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Inventory — Tests

MDE-Cross-Domain-Vertrag:

```bash
pytest tests/test_mde_inbox.py tests/test_p0_integration_slices.py -q --no-cov
pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/schnittstelle/mde-inbox.test.tsx src/__tests__/components/mask-builder/mde-row-actions.test.tsx
```

```bash
pytest tests/ -k "inventory or warehouse or lager"
```

Frontend: `packages/frontend-web/src/pages/lager/`

Inventur-Nebenlaeufe: `pytest tests/test_inventory_auxiliary.py -q --no-cov`
und `vitest run src/__tests__/pages/lager/inventur-nebenlaeufe.test.tsx`.
