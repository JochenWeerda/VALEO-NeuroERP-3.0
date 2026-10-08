---
title: MCP Mask-Writes Batch5 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: configure_threshold, Feed-Analyse release/reject, Reklamation abschliessen.
---

# MCP-MASK-WRITES-BATCH5 2026-10-08

## Lieferung

| Tool | Mask-Actions | Scope |
|------|--------------|-------|
| `agrar.feeding.configure_threshold` | `configure_threshold` | `agrar:write` |
| `agrar.feed_analysis.transition` | `release`, `reject` | `agrar:write` |
| `qualitaet.reklamation.abschliessen` | `abschliessen` | `quality:write` |

Token-Mandant, Default `dryRun`, `execute` + `idempotency_key`, Audit.
Kein FIBU/FIN-CLOSE. Personal/Fuhrpark bewusst nicht verdrahtet (nur
ActionRuntime-Command-Namen ohne HTTP-Endpoint/Mandantenpfad).

## Map-Coverage

| Status | Anzahl |
|--------|--------|
| `mapped` | 19 |
| `mapped_read` | 2 |
| `adjacent` | 1 |
| `open_high` | 2 |
| `open_medium` | 32 |

Registry: **32** Tools (56 Mask-Mutationen betrachtet).

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

112 Tests gruen (2026-10-08).

## Grenzen

~32 medium (Personal/Fuhrpark/Speichern ohne Endpoint); Produktionsleitstand-Sync;
Inventur-Opening high; FIN-CLOSE/ADR-076.
