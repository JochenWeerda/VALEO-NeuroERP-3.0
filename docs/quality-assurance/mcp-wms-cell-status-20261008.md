---
title: MCP Silozellen-Status 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: wms.cell.status — Mandanten-Silozelle Read-only, kein Transfer/QS-Write.
---

# MCP-WMS-CELL-STATUS 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `wms.cell.status` | low | Liest `domain_inventory.silo_cells` im Token-Mandanten |

| Feld | Quelle |
|------|--------|
| `cell_code` / `current_stock_kg` / `qs_status` | `silo_cells` |
| `current_material` | `current_material_id` oder null |
| `flush_required` | `qs_status = reinigung` oder Kante `material_flow_edges.flush_required` |

Zelle per Zellencode oder UUID. Kein Transfer, keine QS-Änderung, kein FIN-CLOSE.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

83 MCP-Tests gruen. Registry: 21 Tools.

## Grenzen

Mask-Write-Rest und FIN-CLOSE bleiben offen;
Rest-Reads → Slice MCP-CATALOG-READS-REST-20261008.

**Nachzug:** Deep-Link Voice/Dispatch → Slice MCP-DEEP-LINK-CELL-20261008
(`route_path` `/lager/silo-zellen/{id}` / `screen_id` `lager/silo-cell`).
