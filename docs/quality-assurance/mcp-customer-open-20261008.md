---
title: MCP Kunde oeffnen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: crm.customer.open — Mandanten-Aufloesung und kanonische Masken-Route ohne Schreiben.
---

# MCP-CUSTOMER-OPEN 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `crm.customer.open` | low | Liest `domain_crm.customers` im Token-Mandanten; liefert `route_path` `/crm/customers/{id}` und `screen_id` `crm/customer-360` |

Kein Schreiben: weder `dryRun` noch `execute` committen oder `mcp_tool_executions` schreiben.
`propose` ist abgewiesen (422). FIBU/Journal/ADR-076 unberührt.

## Mandanten-ID

- Quelle: Token-Claim `tenant_id` oder Alias `mandanten_id`
- Parameter `tenant_id` / `mandanten_id` → 422
- Lookup: `domain_crm.customers WHERE tenant_id = :tenant AND (customer_number|id)`

## Voice

Builtin-Action `nav-customers` Intent-Phrasen um „öffne Kunde“ / „öffne Kunden“ /
„Kunde öffnen“ ergänzt (Listen-Navigation). Entity-Aufloesung mit Nummer bleibt
MCP-Tool; Frontend-Deep-Link-Verdrahtung ist Folgearbeit.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
python scripts/generate_mcp_tool_reference.py --check
```

Registry: 21 Tools, Validierung ohne Fehler.

## Grenzen

Uebrige Read-Katalog-Tools ohne Execution-Adapter → 501. Mask-ID→MCP-Write-Paritaet,
Stufe-2-SUS und FIN-CLOSE bleiben eigene Slices.
