---
title: MCP Auftrag Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus sales.order.status.
---

# MCP-ORDER-NAV 2026-10-08

## Lieferung

Folge zu [mcp-order-status-20261008](./mcp-order-status-20261008.md) und Muster
[mcp-customer-nav-20261008](./mcp-customer-nav-20261008.md):

| Schicht | Verhalten |
|---------|-----------|
| Status-Read | `sales.order.status` liefert `route_path` + `screen_id` |
| Intent | „öffne Auftrag SO-100“ / „Auftrag öffnen A-42“ → `nav-orders` + `auftrag_nr` |
| Dispatch | mit `auftrag_nr` → MCP `sales.order.status` (dryRun) → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/sales/auftraege-liste` |
| Guard | nur relative `/sales/order-editor/{id}` (kein Open-Redirect) |

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py::test_order_status_dry_run_returns_lifecycle_without_writing \
  tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-order-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_verkauf_crm.py -q --override-ini addopts=
```

17 MCP-Registry/Status-, 12 Frontend-, 30 Voice-CRM-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076, kein open_high (AP/Zahlauf/Inventur),
kein blocked_no_endpoint ohne HTTP. Postfach-Slice bleibt fremder Claim.
Stufe-2-SUS und 31× blocked_no_endpoint bleiben offen.
Kein Commit/Push in diesem Slice; keine neue DB/Container.
