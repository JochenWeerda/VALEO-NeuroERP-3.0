---
title: MCP Einkauf-Bestellung Deep-Link Navigation 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Voice/Dispatch navigiert auf sicheren route_path aus einkauf.bestellung.status.
---

# MCP-DEEP-LINK-PO 2026-10-08

## Lieferung

| Schicht | Verhalten |
|---------|-----------|
| Status-Read | Neues `einkauf.bestellung.status` (einkauf:read) liefert `route_path`/`screen_id` |
| List-Read | `einkauf.bestellung.list`-Items tragen `route_path`/`screen_id` |
| Intent | „öffne Bestellung BE-100“ → `nav-einkauf` + `bestellung_id` |
| Dispatch | mit `bestellung_id` → MCP dryRun → Navigate |
| Dispatch | mit sicherem `route_path` → Navigate ohne MCP |
| Dispatch | ohne Kennung → `/einkauf/bestellungen` |
| Guard | nur relative `/einkauf/bestellung/{id}` |

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py -k "bestellung_status or bestellung_list" \
  tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''

cd packages/frontend-web
npx vitest run src/__tests__/lib/mcp-po-open.test.ts \
  src/__tests__/features/ki-usability/ActionDispatchContext.test.tsx

cd services/ki-usability
python -m pytest tests/test_voice_intent_lager_einkauf_hr.py::TestResolverEinkauf \
  -q --override-ini addopts=
```

4 Bestellung- + 14 Registry-, 21 Frontend-, 12 Voice-Einkauf-Tests gruen.
Registry: 36 Tools.

## Grenzen

Kein Versand-Write, kein Obligo/FIN-CLOSE/ADR-076. Kein Commit/Push; keine neue DB.
