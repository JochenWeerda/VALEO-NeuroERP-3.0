---
title: MCP AP-Freigabe Vier-Augen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: finance.ap_invoice.propose/freigeben analog sales.invoice.post; echter CommandEndpoint; kein FIN-CLOSE.
---

# MCP-AP-FREIGABE 2026-10-08

## Lieferung

| Tool | Rolle |
|------|-------|
| `finance.ap_invoice.propose` | dryRun-Preview; `propose` → `agent_proposals` (`ap_invoice_freigabe`, pending); `execute` → 501 |
| `finance.ap_invoice.freigeben` | nur nach `approval_status=approved`; ruft `approve_ap_invoice` (CommandEndpoint-Fachweg); `fibu_journal=false` |

Scope `finance:write`, `risk_class=high`, `human_approval_required=true`.
Kein Client-Freigabe-Boolean. Mandant nur aus Token. Kein Journal-Post, kein FIN-CLOSE.

Mask-Map: `mask:finance/ap-invoice:freigeben` → `mapped` / `finance.ap_invoice.freigeben`.
Propose bleibt `mcp_native`. Stats: mapped **23** / open_high **2** / blocked_no_endpoint **31**.
Registry: **38** Tools.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python scripts/generate_mcp_tool_reference.py
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

131 Tests gruen (2026-10-08).

## Grenzen

- Zahlauf-Freigabe bleibt `open_high` (`forbiddenForAgents`, ADR-076-Umfeld).
- Inventur-Bestandsvortrag nachgezogen als propose-only
  (`MCP-INVENTUR-OPENING-PROPOSE-20261008`, `mapped_propose_only`).
- FIN-CLOSE bleibt `blocked_adr_076` (kein Scheinabschluss).
- 31× `blocked_no_endpoint` unveraendert.
