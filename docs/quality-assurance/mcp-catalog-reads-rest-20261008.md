---
title: MCP Rest-Katalog-Reads 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Batch-Verdrahtung aller restlichen MCP-Katalog-Reads (kein Write/FIN-CLOSE).
---

# MCP-CATALOG-READS-REST 2026-10-08

## Lieferung

| Tool | Scope | Quelle |
|------|-------|--------|
| `dms.document.search` | nachweisraum:read | `domain_nachweisraum.nachweisraum_dokumente` |
| `dms.gobd.export_status` | nachweisraum:read | `domain_nachweisraum.gobd_exporte` |
| `agrar.contract.get` | agrar:read | `domain_inventory.agrar_contracts` |
| `agrar.weighing_ticket.list` | agrar:read | `domain_inventory.weighing_tickets` |
| `lager.bestand.get` | lager:read | `domain_inventory.articles` |
| `lager.inventur.status` | lager:read | `inventory_counts` + lines |
| `einkauf.bestellung.list` | einkauf:read | `domain_einkauf.bestellungen` |
| `compliance.gate.status` | compliance:read | eBilanz/GoBD/TSE-Signale; sonst `keine_daten` |
| `agent.proposal.list` | agent:read | `public.agent_proposals` |

Alle: Token-Mandant, `extra=forbid`, dryRun/execute nur Lesen, propose → 422.
Keine Fake-Freigaben; fehlende Entität → 404 bzw. leere Liste / `keine_daten`.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

90 MCP-Tests gruen. Registry: 21 Tools, alle Reads verdrahtet.

## Grenzen

Mask-Write-Rest und FIN-CLOSE/agentic Finance bleiben bewusst offen.
