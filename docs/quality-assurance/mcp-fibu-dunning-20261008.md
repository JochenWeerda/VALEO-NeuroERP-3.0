---
title: MCP Mahnstatus abfragen 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: fibu.dunning.status — Mandanten-Mahnstatus Read-only, kein Mahnlauf/FIN-CLOSE.
---

# MCP-FIBU-DUNNING 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `fibu.dunning.status` | low | Liest Debitoren-OP + `dunning_notices` im Token-Mandanten |

| Feld | Quelle |
|------|--------|
| `mahnstufe` | max(OP `mahn_stufe`, letzte Notice `dunning_level`) |
| `letzte_mahnung` | neueste `dunning_notices.dunning_date` oder null |
| `gesamt_offen_eur` | Summe `offen` Debitoren-OP (nicht bezahlt/storniert/ausgeziffert) |

Kunde nur über `domain_crm.customers` des Authentifizierungs-Mandanten.
Kein Mahnlauf, kein Journal, kein Kassenabschluss (ADR-076 unberührt).

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

73 MCP-Tests gruen. Registry: 21 Tools.

## Grenzen

`wms.cell.status`, DMS/Agrar-Reads und Mask-Write bleiben offen;
`wms.lot.trace` → Slice MCP-WMS-LOT-TRACE-20261008; FIN-CLOSE bewusst nicht.
