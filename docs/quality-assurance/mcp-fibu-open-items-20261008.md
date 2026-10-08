---
title: MCP Offene Posten listen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: fibu.open_items.list — Mandanten-OP-Liste Read-only, kein FIN-CLOSE.
---

# MCP-FIBU-OPEN-ITEMS 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `fibu.open_items.list` | low | Liest `domain_erp.offene_posten` im Token-Mandanten |

| typ | konto_typ |
|-----|-----------|
| forderung | debitoren |
| verbindlichkeit | kreditoren |

Filter: nicht bezahlt/storniert/ausgeziffert, `offen > 0`, optional `faellig_bis`.
Kein Journal, kein Kassenabschluss (ADR-076 unberührt).

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

68 MCP-Tests gruen. Registry: 21 Tools.

## Grenzen

WMS/DMS/Agrar-Reads und Mask-Write bleiben offen; `fibu.dunning.status` → Slice MCP-FIBU-DUNNING-20261008.
