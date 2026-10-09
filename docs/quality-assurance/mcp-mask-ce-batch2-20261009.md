---
title: MCP Mask CE Batch2 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Batch2 — Bonus/Query-Import/Tour/PO-Speichern CE+MCP; Navigation/Form-Reset local_ui; Isolation Read+Write.
---

# MCP-MASK-CE-BATCH2-20261009

## Gewaehlt / geliefert

| Mask-Action | Klassifikation | CE / MCP |
|-------------|----------------|----------|
| `auswertungen/bonus-berechnung:calculate` | mapped | CE `/api/v1/l3-report-catalog/bonus-runs/actions/calculate` + `reporting.bonus.calculate` |
| `auswertungen/abfrage-center:import` | mapped | CE `/api/v1/query-center/actions/import` + `reporting.query.import_signed` |
| `logistik/tourenplanung:anlegen` | mapped | CE `/api/v1/logistik/tours/actions/anlegen` + `logistik.tour.anlegen` |
| `einkauf/purchase-order:speichern` | mapped | CE `/api/v1/einkauf/bestellungen/{id}/actions/speichern` + `einkauf.bestellung.speichern` |
| `einkauf/supplier:neue_bestellung` | local_ui | Navigation `/einkauf/bestellungen/neu` |
| `admin/postfaecher:neu` | local_ui | Form-Reset (kein HTTP) |

Isolation (bindend): Token-Mandant, `extra=forbid`, Parameter-Override 422,
SQL/Lookups Token-scoped, Cross-Tenant 404. Siehe
[mcp-tenant-isolation-read-write-20261009.md](./mcp-tenant-isolation-read-write-20261009.md).

Non-Goals unberuehrt: FIN-CLOSE, Zahlauf, Postfach-Speichern (WIP), Personal/Fuhrpark-CRUD.

## Kennzahlen

| Metrik | Wert |
|--------|------|
| mapped | **30** |
| blocked_no_endpoint | **11** |
| local_ui | **13** |
| open_high | **1** (Zahlauf) |
| Registry | **45** Tools |

## Nachweis

```bash
python scripts/generate_screen_action_catalog.py --check
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_ce_batch2_reporting.py \
  tests/test_mcp_mask_ce_batch2_tour_po.py \
  tests/test_mcp_mask_action_map.py tests/test_mcp_tool_registry.py \
  tests/test_mcp_local_action_classification.py \
  tests/test_mcp_tenant_isolation_all.py \
  --noconftest -q --override-ini addopts=''
```

Kein Commit/Push; keine DB.
