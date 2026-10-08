---
title: MCP Mask-Writes Batch4 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: retire/archive + Feeding Handoff/Massnahme als MCP-Writes.
---

# MCP-MASK-WRITES-BATCH4 2026-10-08

## Lieferung

| Tool | Mask-Actions | Scope |
|------|--------------|-------|
| `agrar.ration.transition` (erweitert) | `retire`, `archive` (+ bisherige 4) | `agrar:write` |
| `agrar.feeding.supply_handoff` | `mask:agrar/feed-readiness:create_handoff` | `agrar:write` |
| `agrar.feeding.actual_measure` | `mask:agrar/feeding-actuals:create_measure` | `agrar:write` |

`retire`/`archive` brauchen `reason`. Handoff/Massnahme: Default `dryRun`,
`execute` + `idempotency_key` (an Fachdienst weitergereicht). Kein FIBU/FIN-CLOSE.

## Map-Coverage

| Status | Anzahl |
|--------|--------|
| `mapped` | 15 |
| `mapped_read` | 2 |
| `adjacent` | 1 |
| `open_high` | 2 |
| `open_medium` | 33 |

Registry: **29** Tools.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

109 Tests gruen (2026-10-08).

## Grenzen

~33 medium (configure_threshold, Personal/Fuhrpark, Speichern ohne Endpoint);
FIN-CLOSE/ADR-076.
