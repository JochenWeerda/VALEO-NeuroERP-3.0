---
title: MCP Inventur-Opening propose-only 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: lager.inventur.propose_opening — Snapshot + pending Proposal; execute 501; kein Booking.
---

# MCP-INVENTUR-OPENING-PROPOSE 2026-10-08

## Lieferung

| Tool | Rolle |
|------|-------|
| `lager.inventur.propose_opening` | dryRun liest Inventur-Snapshot (`inventory_counts` + Zeilen, gleiche Quelle wie `InventoryAuxiliaryService.create`); `propose` → `agent_proposals` (`inventur_opening`, pending); `execute` → **501** |

Scope `lager:write`, `risk_class=high`, `human_approval_required=true`.
Kein CommandEndpoint, kein `opening_balance`-Batch, kein Journal.
Freigabe-Boolean im Aufruf → 422.

Mask-Map: `mask:lager/inventur-nebenlaeufe:create_opening` → **`mapped_propose_only`** /
`lager.inventur.propose_opening`.

Stats: mapped 23 / mapped_propose_only **1** / open_high **1** (nur Zahlauf) /
blocked_no_endpoint 31. Registry: **39** Tools.

## Snapshot-Quelle

Echt und vorhanden — keine Erfindung:

- `domain_inventory.inventory_counts` (count_id, warehouse, status)
- `domain_inventory.inventory_count_lines` + `articles.purchase_price`
  → `line_count`, `difference_count`, `preliminary_value`

Route-Hinweis: `/lager/inventur-nebenlaeufe` (Screen `lager/inventur-nebenlaeufe`);
`source_route` `/lager/inventur?count={id}` analog Auxiliary-Service.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python scripts/generate_mcp_tool_reference.py
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

137 Tests gruen (2026-10-08).

## Grenzen

- Kein Freigabe-/Apply-MCP-Tool (bewusst: Human-Input-Flow ohne CommandEndpoint).
- Zahlauf-Freigabe bleibt `open_high` (nicht verdrahten).
- FIN-CLOSE bleibt `blocked_adr_076`.
- 31× `blocked_no_endpoint` unveraendert.
