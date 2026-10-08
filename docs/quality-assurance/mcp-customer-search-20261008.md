---
title: MCP Kunden suchen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: crm.customer.search — Mandanten-Trefferliste inkl. route_path, Read-only.
---

# MCP-CUSTOMER-SEARCH 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `crm.customer.search` | low | Sucht in `domain_crm.customers` des Token-Mandanten (Name/Nummer/Adresse-Text); liefert `items` inkl. `route_path` |

Ergaenzt die Kette search → open → Voice/Deep-Link. Kein Schreiben, kein FIBU/ADR-076.
`propose` → 422. Leere Trefferliste → 200 mit `items=[]`.

## Mandanten-ID

- Quelle: Token-Claim `tenant_id` oder Alias `mandanten_id`
- Parameter `tenant_id` / `mandanten_id` → 422
- `limit` Default 20, Maximum 50

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
python scripts/generate_mcp_tool_reference.py --check
```

52 MCP-Tests gruen (2026-10-08). Registry: 21 Tools.

## Grenzen

Weitere Katalog-Reads ohne Adapter (u. a. `crm.customer.summary360`,
`sales.order.status`, FIBU/WMS/DMS/…) → 501. Mask-Write-Paritaet, FIN-CLOSE
und Stufe-2-SUS bleiben eigene Slices.
