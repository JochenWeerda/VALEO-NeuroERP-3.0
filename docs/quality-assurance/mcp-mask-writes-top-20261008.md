---
title: MCP Top medium Mask-Writes 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: crm.lead.qualify und einkauf.bestellung.versenden — Token-Mandant, Idempotenz, Audit; Map mapped.
---

# MCP-MASK-WRITES-TOP 2026-10-08

## Lieferung

| Tool | Mask-Action | Scope | Risiko | Fachpfad |
|------|-------------|-------|--------|----------|
| `crm.lead.qualify` | `mask:crm/lead:qualifizieren` | `crm:write` | medium | `crm_lead_service.qualify` |
| `einkauf.bestellung.versenden` | `mask:einkauf/purchase-order:versenden` | `einkauf:write` | medium | `ProcurementService` Versand |

Beide analog zu `crm.contact.log` / `crm.activity.create`: Default `dryRun`,
`execute` erfordert `idempotency_key`, Audit-Eintrag, Mandant nur aus Token.
Kein Obligo-Journal, kein FIN-CLOSE (ADR-076).

## Mandanten-ID / Guards

- Quelle: Token-Claim `tenant_id` oder Alias `mandanten_id`
- Parameter `tenant_id` / `mandanten_id` → 422 (`extra=forbid`)
- Lead: `lead_id` + `customer_id` oder `kunden_nr` (Mandanten-Kunde)
- Bestellung: `bestellung_id` (UUID oder Bestellnummer), optional `versand_art`/`empfaenger`
- Scope-Pflicht: `crm:write` bzw. `einkauf:write`

## Map-Coverage (nach Generator)

| Status | Anzahl |
|--------|--------|
| `mapped` | 4 |
| `mapped_read` | 2 |
| `adjacent` | 1 |
| `open_high` | 2 |
| `open_medium` | 43 |
| `mcp_native` | 3 |

Registry: **23** Tools.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

97 Tests gruen (2026-10-08). Generator `--check` OK.

## Grenzen

~43 medium Mask-Mutationen ohne MCP-Write (u. a. EK anbieten/WE, Personal,
Fuhrpark). HIGH/FIBU Freigaben und FIN-CLOSE bleiben bewusst offen.
