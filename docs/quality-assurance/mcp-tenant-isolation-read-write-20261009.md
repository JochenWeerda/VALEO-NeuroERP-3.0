---
title: MCP Mandantenisolation Read+Write+CRUD 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Nachweis dass alle MCP-Tools (Reads, Writes, CRUD) nur den Token-Mandanten lesen/mutieren.
---

# MCP Mandantenisolation (Read + Write + CRUD) 2026-10-09

## Vorgabe

Alle MCP-/Mask-Zugriffe duerfen **nur** den Token-Mandanten lesen oder mutieren.
Gilt fuer search/status/list/get/open/trace **und** Writes/CRUD — nie
mandantenuebergreifend.

## Absicherung

| Schicht | Mechanismus |
|---------|-------------|
| Entry | `execute_mcp_tool`: Tenant nur aus Claims (`tenant_id`/`mandanten_id`); Header-Mismatch → 403 |
| Parameter | `_reject_identity_parameters` + Input-Models `extra=forbid` → 422 bei Override |
| Mask-CE | `parse_action_body` strippt `tenant_id`/`mandanten_id` aus Payload |
| Adapter | SQL/Lookups mit Token-tenant; fremde Entity-IDs → 404; Mutations INSERT/UPDATE mit Token-tenant |
| Batch2 | Bonus/Query-Import Services mit Token-tenant; Import droppt fremde `tenant_id`/`owner_id`/`id` |
| Sanktionen | Pruefprotokoll mandantengebunden; Referenzliste `sanctions_list` global (Shared Master) |
| Post-Invoice | Positions-SELECT via JOIN auf `delivery_notes.tenant_id` (Defense-in-Depth) |

## Audit-Ergebnis

- 43 Tool-Adapter in `mcp_execution_service.py` geprueft.
- Einziger nachgezogener SQL-Gap: Positions-SELECT ohne Parent-Tenant-Join bei
  `sales.invoice.post` — behoben.
- Zentrale Identity-Guards decken Reads und Writes ab.

## Nachweis

```bash
python -m pytest tests/test_mcp_tenant_isolation_all.py \
  tests/test_mcp_mask_ce_batch2_reporting.py \
  --noconftest -q --override-ini addopts=''
```

Cross-Tenant-Negativfaelle u. a.: `crm.customer.search`, `crm.customer.open`,
`sales.order.status`, `crm.contact.log` (+ weitere Writes).

## Grenzen / weiter offen

- Shared-Referenzdaten (z. B. globale Sanktionsliste) sind bewusst nicht
  mandantengebunden; Schreibprotokolle sind es.
- FIN-CLOSE / Zahlauf / Stufe-2-SUS unveraendert (Non-Goals).
- Kein Commit/Push in diesem Slice.
