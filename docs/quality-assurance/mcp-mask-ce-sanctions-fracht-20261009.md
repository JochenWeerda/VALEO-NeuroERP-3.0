---
title: MCP Mask CE Sanktionen und Frachttabelle 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Echte commandEndpoints + MCP-Writes fuer Sanktionspruefung und Frachttabelle; Verladung neu als local_ui.
---

# MCP-MASK-CE-SANCTIONS-FRACHT 2026-10-09

## Lieferung

| Mask-Action | CE | MCP-Tool |
|-------------|----|---------|
| `auswertungen/sanktionspruefung-kunden:check` | `/api/v1/compliance/sanctions/actions/pruefen/customers` | `compliance.sanctions.check` |
| `auswertungen/sanktionspruefung-personal:check` | `/api/v1/compliance/sanctions/actions/pruefen/personal` | `compliance.sanctions.check` |
| `logistik/frachttabellen:anlegen` | `/api/v1/logistik/frachttabellen/actions/anlegen` | `logistik.frachttabelle.anlegen` |
| `logistik/verladung:neu` | — (Navigation) | — (`local_ui`) |

ActionRuntime-Modi: dryRun/validate/propose ohne Schreibwirkung; execute mit
mandantengebundenem Protokoll bzw. INSERT. Scope der Sanktionsmaske kommt aus
dem CE-Pfad (kein Silent-Override). Legacy-REST `/pruefen` bleibt kompatibel.
Kein Auto-Freigeben von Treffern, kein FIBU/FIN-CLOSE, kein Zahlauf, Postfach unberuehrt.

Map-Stats: mapped **26** / blocked_no_endpoint **17** / local_ui **11** /
open_high **1** (Zahlauf). Registry: **41** Tools.

## Nachweis

```bash
python scripts/generate_screen_action_catalog.py --check
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_ce_sanctions_fracht.py \
  tests/test_mcp_local_action_classification.py \
  tests/test_mcp_mask_action_map.py tests/test_mcp_tool_registry.py \
  tests/test_mcp_execution.py --noconftest -q --override-ini addopts=''
```

## Grenzen

- FIN-CLOSE bleibt `blocked_adr_076` (kein Adapter).
- Zahlauf bleibt `open_high` / `forbiddenForAgents`.
- 17× `blocked_no_endpoint` (Personal/Fuhrpark-Speichern, Postfach, Bonus,
  Abfrage-Import, PO-Speichern, Tour anlegen, …) ohne neuen CE.
- Stufe-2-SUS live unveraendert.
