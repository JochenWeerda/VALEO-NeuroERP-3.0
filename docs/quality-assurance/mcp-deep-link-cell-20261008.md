---
title: MCP Silozelle Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus wms.cell.status.
---

# MCP-DEEP-LINK-CELL 2026-10-08

## Lieferung

Folge zu [mcp-wms-cell-status-20261008](./mcp-wms-cell-status-20261008.md) und Muster
[mcp-deep-link-lot-20261008](./mcp-deep-link-lot-20261008.md):

| Schicht | Verhalten |
|---------|-----------|
| Status-Read | `wms.cell.status` liefert `cell_id`, `route_path`, `screen_id` |
| Intent | „öffne Zelle ZELLE-A1“ / „Silozelle öffnen …“ → `nav-silo-cell` + `cell_code` |
| Dispatch | mit `cell_code` → MCP dryRun → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/lager/silo-uebersicht` |
| Guard | nur relative `/lager/silo-zellen/{id}` (ScreenDef Twin-Activate-Route) |

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k cell_status \
  tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-cell-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_lager_einkauf_hr.py::TestResolverLager \
  -q --override-ini addopts=
```

5 Cell-Status- + Registry-, 18 Frontend-, 16 Voice-Lager-Tests gruen.

## Grenzen

Kein Write, kein FIN-CLOSE/ADR-076. Route `/lager/silo-zellen/{id}` ist der
kanonische Twin-Activate-Pfad (`lager/silo-cell`); Listen-Fallback bleibt die
existierende Silo-Uebersicht. Kein Commit/Push; keine neue DB.
