---
title: MCP Lot Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus wms.lot.trace.
---

# MCP-DEEP-LINK-LOT 2026-10-08

## Lieferung

Folge zu [mcp-wms-lot-trace-20261008](./mcp-wms-lot-trace-20261008.md) und Muster
[mcp-order-nav-20261008](./mcp-order-nav-20261008.md):

| Schicht | Verhalten |
|---------|-----------|
| Trace-Read | `wms.lot.trace` liefert `route_path` + `screen_id` |
| Intent | „öffne Lot LOT-42“ / „Lot öffnen …“ / Charge → `nav-lot` + `lot_id` |
| Dispatch | mit `lot_id` → MCP `wms.lot.trace` (dryRun) → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/charge/rueckverfolgung` |
| Guard | nur relative `/charge/stamm/{id}` (kein Open-Redirect; keine freien Lager-URLs) |

Kanonische Maske: bestehende Detailroute `charge/stamm/:id` (Screen `charge/stamm`).

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k lot_trace \
  tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-lot-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_lager_einkauf_hr.py::TestResolverLager \
  -q --override-ini addopts=
```

5 Lot-Trace- + 14 Registry-, 15 Frontend-, 13 Voice-Lager-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076, kein open_high.
`wms.cell.status` Deep-Link bewusst eigener Slice.
Kein Commit/Push; keine neue DB/Container.
