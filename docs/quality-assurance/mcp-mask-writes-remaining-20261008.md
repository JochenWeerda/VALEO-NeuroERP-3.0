---
title: MCP Mask-Writes Remaining 2026-10-08
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-08
description: Rest-Klassifikation open_medium; Leitstand/Kalender/MDE verdrahtet; blocked_no_endpoint.
---

# MCP-MASK-WRITES-REMAINING 2026-10-08

## Lieferung

| Tool | Mask-Actions | Scope |
|------|--------------|-------|
| `produktion.control.sync` | `produktion/produktionsleitstand:sync` | `ops:write` |
| `planung.calendar.reproject` | `planung/kalender:reproject` | `planung:write` |
| `mobile.sync.process_pending` | `schnittstelle/mde-inbox:process_pending` | `mobile:write` |

Token-Mandant, Default `dryRun`, `execute` + `idempotency_key`, Audit.
Kein FIBU/FIN-CLOSE. Keine Backend-Erfindung.

## Klassifikation Rest (vorher ≈32 open_medium)

| Status | Bedeutung | Anzahl |
|--------|-----------|--------|
| `mapped` | inkl. 3 neue Writes | 22 |
| `mapped_read` | | 2 |
| `adjacent` | | 1 |
| `blocked_no_endpoint` | Personal/Fuhrpark/Admin/Reporting/Speichern ohne HTTP | 31 |
| `open_high` | Finance-Freigaben + Inventur-Opening | 3 |
| `open_medium` | **keine mehr** | **0** |

59 Mask-Mutationen; `classification_complete: true`; `next_medium_candidates: []`.
Registry: **35** Tools.

## Nachweis

```bash
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_execution.py tests/test_mcp_tool_registry.py tests/test_mcp_mask_action_map.py --noconftest -q --override-ini addopts=''
```

116 Tests gruen (2026-10-08).

## Grenzen / Parent

- Personal/Fuhrpark bewusst `blocked_no_endpoint` (nur ActionRuntime-Commands).
- Inventur-Opening `open_high` (Vier-Augen / danger=high).
- FIN-CLOSE bleibt `blocked_adr_076`.
- Goal „Offenes umsetzen“: Mask-Write-medium-Parität ohne Backend-Erfindung
  completed; Parent entscheidet Goal-Status (FIN-CLOSE/SUS getrennt).
