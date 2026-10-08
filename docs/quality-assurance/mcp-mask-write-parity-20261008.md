---
title: MCP Mask-Write-Parität 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Mask-ID→MCP Mapping; FIN-CLOSE/ADR-076 blockiert; Completion-Audit-Text.
---

# MCP-MASK-WRITE-PARITY 2026-10-08

## Lieferung

| Artefakt | Rolle |
|----------|--------|
| [`config/mcp_mask_action_map.yaml`](../../config/mcp_mask_action_map.yaml) | Maschinenlesbare Parität |
| `scripts/generate_mcp_mask_action_map.py` | Generator + `--check` |
| `tests/test_mcp_mask_action_map.py` | Drift-/Vertragsasserts |

### Coverage (Generatorlauf)

| Status | Bedeutung | Anzahl |
|--------|-----------|--------|
| `mapped` | Mask-Mutation → MCP-Write | 2 (Baseline; Stand nach WRITES-TOP: 4) |
| `mapped_read` | Mask → MCP-Read (kein Write) | 2 |
| `adjacent` | verwandte Belegkette, nicht 1:1 | 1 |
| `open_high` | FIBU/HIGH bewusst ohne MCP-Write | 2 |
| `open_medium` | Mutation ohne MCP-Write | 45 (Baseline; Stand nach WRITES-TOP: 43) |
| `mcp_native` | MCP-Write ohne mask:* | 3 (`contact.log`, `invoice.propose/post`) |

**MCP-fähig (Write, Baseline):** `mask:crm/customer-360:create_activity`,
`mask:crm/opportunity:create_activity` → `crm.activity.create`.

**Nachfolger:** [mcp-mask-writes-top-20261008.md](mcp-mask-writes-top-20261008.md)
— Lead `qualifizieren` + Einkauf `versenden` → mapped.

**MCP-native Writes ohne Mask-ID:** `crm.contact.log`, `sales.invoice.propose`,
`sales.invoice.post`.

**Bewusst offen HIGH/FIBU:** `mask:finance/ap-invoice:freigeben`,
`mask:finance/payment-run:freigeben`. Mahnen nur Read (`fibu.dunning.status`).

**FIN-CLOSE:** `blocked_adr_076` — kein MCP-Tool, HTTP 409, kein Journal-DML
([ADR-076](../adr/adr-076-cash-close-retirement.md)).

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

## Completion-Audit-Text (für Parent — Goal noch nicht complete)

```
Goal „Offenes umsetzen“ — Audit 2026-10-08

Erledigt:
- Alle 21 MCP-Katalog-Tools haben Execution-Adapter (Reads + Top-Writes).
- CRM Deep-Link/open/search/summary360; Sales order.status; FiBu OP/Dunning;
  WMS lot/cell; DMS/Agrar/Lager/Einkauf/Compliance/Proposals.
- Mask→MCP-Write-Parität inventarisiert (mcp_mask_action_map.yaml):
  Top-CRM-Activity mapped; Invoice Writes mcp_native; HIGH/FIBU offen;
  FIN-CLOSE explizit blocked_adr_076.

Bewusst nicht erledigt (Blocker / Out-of-Scope):
- FIN-CLOSE / agentic Finance Journal (ADR-076) — nicht implementieren.
- ~45 medium Mask-Mutationen ohne MCP-Write (Personal/Fuhrpark/Logistik/…).
- Stufe-2-SUS Live.

Empfehlung Parent:
Goal kann als „Katalog-Read/Write-Kern + Paritätsinventar geschlossen“ gelten,
solange FIN-CLOSE und SUS-Live als bekannte Rest-Blocker geführt werden.
Parent markiert complete — nicht dieser Slice.
```
