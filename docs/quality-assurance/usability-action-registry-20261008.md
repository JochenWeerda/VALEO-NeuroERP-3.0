---
title: Usability Action-Registry aus ScreenDefinitions
type: reference
audience: [qa, entwickler, agent]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-08
version: 1.0.0
description: Nachweis ACTION-DEN — Maskenaktionen als mask:{screen}:{key} in ki-usability Registry.
---

# Usability Action-Registry — 2026-10-08

**Slice:** `USABILITY-ACTION-REGISTRY-20261008`
**Gap:** U-C10-01 / ACTION-DEN ([Gap-Hub](../gap/executive-summary-20261007.md))

## Lieferung

| Artefakt | Rolle |
|---|---|
| `app/core/screen_action_catalog.py` | Extraktion nur mit Ausführungspfad |
| `scripts/generate_screen_action_catalog.py` | Generiert JSON; `--check` Drift |
| `services/ki-usability/app/data/screen_mask_actions.json` | Committed Katalog |
| `services/ki-usability/app/services/action_registry.py` | Merge Builtin + Mask |

## Kennzahlen (Generatorlauf)

- Maskenaktionen mit Pfad: **85**
- Screens mit exportierten Aktionen: **45**
- Builtin-Actions: unverändert (~78)
- Registry gesamt nach Merge: Builtin + 85

IDs: `mask:{screenId}:{actionKey}` — keine Kollision mit Shortcuts wie `save-document`.

## Abgrenzung

- FIN-CLOSE bleibt HTTP 409 (ADR-076); nicht in diesem Slice.
- MCP-WRITE + MASK-WRITE-PARITY-20261008: Top-Adapter + Mapping
  `config/mcp_mask_action_map.yaml`; Activity mapped; Invoice mcp_native;
  ~45 medium + HIGH/FIBU offen; FIN-CLOSE ADR-076 blockiert.
- Stub-Aktionen ohne Endpoint/Route/Command werden nicht exportiert.

## Tests

- `pytest tests/test_screen_action_catalog.py`
- `pytest services/ki-usability/tests/test_screen_mask_actions_merge.py` (cwd: service)
- `python scripts/generate_screen_action_catalog.py --check`
