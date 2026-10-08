---
title: MCP Mask-Writes Next 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Angebot→Bestellung, Avis→Wareneingang, Lager-Storno als MCP-Writes.
---

# MCP-MASK-WRITES-NEXT 2026-10-08

## Lieferung

| Tool | Mask-Action | Scope | Fachpfad |
|------|-------------|-------|----------|
| `einkauf.angebot.bestellen` | `mask:einkauf/angebot:bestellen` | `einkauf:write` | `EinkaufCompatService.convert_angebot_to_order` |
| `einkauf.anlieferavis.wareneingang` | `mask:einkauf/anlieferavis:wareneingang` | `einkauf:write` | `buche_wareneingang_aus_avis` |
| `lager.stock_movement.stornieren` | `mask:lager/stock-movement:stornieren` | `lager:write` | `storno_korrektur` |

Token-Mandant, Default `dryRun`, `execute` + `idempotency_key`, Audit.
Kein Obligo, kein FIBU-Journal, kein FIN-CLOSE (ADR-076).

## Map-Coverage (nach Generator)

| Status | Anzahl |
|--------|--------|
| `mapped` | 7 |
| `mapped_read` | 2 |
| `adjacent` | 1 |
| `open_high` | 2 |
| `open_medium` | 41 |

Registry: **26** Tools (53 Mask-Mutationen betrachtet; Storno neu in Map).

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

103 Tests gruen (2026-10-08). Generator `--check` OK.

## Grenzen

~41 medium ohne MCP-Write (Personal/Fuhrpark/Agrar-Lifecycle/Speichern ohne Endpoint).
HIGH/FIBU und FIN-CLOSE bleiben bewusst offen.
