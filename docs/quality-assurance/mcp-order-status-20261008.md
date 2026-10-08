---
title: MCP Auftragsstatus 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: sales.order.status — Mandanten-Lifecycle Read-only.
---

# MCP-ORDER-STATUS 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `sales.order.status` | low | Liest `domain_crm.sales_orders` (+ Items) im Token-Mandanten |

| Status | naechster_schritt | offene_positionen |
|--------|-------------------|-------------------|
| open | Auftrag bestätigen | COUNT Items qty>0 |
| confirmed | Lieferschein erstellen | COUNT Items qty>0 |
| in_delivery | Auftrag abschließen | COUNT Items qty>0 |
| completed / cancelled | Keine Aktion … | 0 |

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

63 MCP-Tests gruen. Registry: 21 Tools.

## Grenzen

Weitere Katalog-Reads (FIBU/WMS/DMS/…) und Mask-Write bleiben offen. FIN-CLOSE unberührt.

**Nachzug:** Deep-Link Voice/Dispatch → Slice MCP-ORDER-NAV-20261008
(`route_path` / `screen_id` am Status-Read).
