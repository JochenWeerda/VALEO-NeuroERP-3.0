---
title: MCP Mask-Writes Batch3 Agrar-Lifecycle 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: agrar.ration.transition — submit_review/approve/schedule/activate.
---

# MCP-MASK-WRITES-BATCH3 2026-10-08

## Lieferung

| Tool | Mask-Actions | Scope | Fachpfad |
|------|--------------|-------|----------|
| `agrar.ration.transition` | `submit_review`, `approve`, `schedule`, `activate` | `agrar:write` | `RationLifecycleService.transition` |

Parameter: `ration_id`, `action_key`, optional `reason` / `feeding_start` /
`expected_status`. `schedule` braucht `feeding_start`. Approve/Activate bei
Readiness-Blockern nur mit `reason` beginnend mit `OVERRIDE:`.

Token-Mandant, Default `dryRun`, `execute` + `idempotency_key`, Audit.
Kein FIBU/FIN-CLOSE.

## Map-Coverage (nach Generator)

| Status | Anzahl |
|--------|--------|
| `mapped` | 11 |
| `mapped_read` | 2 |
| `adjacent` | 1 |
| `open_high` | 2 |
| `open_medium` | 37 |

Registry: **27** Tools. Noch offen in Agrar-Lifecycle: `retire`, `archive`.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

105 Tests gruen (2026-10-08). Generator `--check` OK.

## Grenzen

~37 medium ohne MCP-Write; retire/archive; Personal/Fuhrpark; FIN-CLOSE/ADR-076.
