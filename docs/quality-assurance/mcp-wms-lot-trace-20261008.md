---
title: MCP Lot verfolgen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: wms.lot.trace — Mandanten-Lot-Trace Read-only, keine Buchung/QS-Aenderung.
---

# MCP-WMS-LOT-TRACE 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `wms.lot.trace` | low | Liest Silo-Lot (bevorzugt) oder Inventory-Lot im Token-Mandanten |

| Feld | Quelle |
|------|--------|
| `lot_id` / `artikel_id` / `status` | `silo_lots` bzw. `inventory_lots` |
| `menge_kg` | Silo: `quantity_tons * 1000`; Inventory: `current_qty` (t→kg) |
| `qs_status` | `silo_cells.qs_status` bzw. `inventory_lots.qs_status`, sonst Lot-Status |
| `silozelle` | `silo_cells.cell_code` oder null |
| `bewegungen` | `silo_lot_movements` bzw. `inventory_lot_movements` (max. 50) |

Lot per UUID oder Virtual-/Lotnummer. Keine Buchung, keine QS-Änderung, kein FIN-CLOSE.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

78 MCP-Tests gruen. Registry: 21 Tools.

## Grenzen

DMS/Agrar/Lager-Reads und Mask-Write bleiben offen;
`wms.cell.status` → Slice MCP-WMS-CELL-STATUS-20261008; FIN-CLOSE bewusst nicht.
