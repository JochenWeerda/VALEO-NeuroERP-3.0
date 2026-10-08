---
title: MCP Kunden-360-Zusammenfassung 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: crm.customer.summary360 — Mandanten-Kennzahlen Read-only.
---

# MCP-CUSTOMER-SUMMARY360 2026-10-08

## Lieferung

| Tool | Risiko | Verhalten |
|------|--------|-----------|
| `crm.customer.summary360` | low | Stamm `domain_crm.customers` + Aggregates (offene Auftraege, OP-Saldo, letzte Aktivitäten, Segment) |

SQL analog CRM Screen-Summary/360. Bewusst **kein** `public.kunden`-Fallback
(strenger als UI-`_kunde_finden`). Fehlende Aggregate-Tabellen → ehrlich 0 / [].

## Antwort

`kunden_nr`, `name`, `customer_id`, `offene_auftraege`, `op_saldo_eur`,
`letzte_kontakte[]`, `segment`, `route_path`, `screen_id`.

## Nachweis

```bash
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py --noconftest -q --override-ini addopts=''
```

57 MCP-Tests gruen. Registry: 21 Tools (unverändert).

## Grenzen

Weitere Reads (`sales.order.status`, FIBU/WMS/…) → 501. FIN-CLOSE unberührt.
