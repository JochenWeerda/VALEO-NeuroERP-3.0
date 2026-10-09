---
title: MCP Mask CE Batch3 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Batch3 — Bewerbung/Einwilligung/Postfach CE+MCP; Fuhrpark Isolation-Blocker; Personal-Rest blocked.
---

# MCP-MASK-CE-BATCH3-20261009

## Gewaehlt / geliefert

| Mask-Action | Klassifikation | CE / MCP |
|-------------|----------------|----------|
| `personal/bewerbungen:speichern` | mapped | CE `/api/v1/personal/applications/actions/speichern` + `hr.bewerbung.speichern` |
| `personal/einwilligungserklaerungen:anlegen` | mapped | CE `/api/v1/personal/applications/einwilligungserklaerungen/actions/anlegen` + `hr.einwilligung.anlegen` |
| `admin/postfaecher:speichern` | mapped | CE `/api/v1/admin/postfaecher/actions/speichern` + `admin.postfach.speichern` |

Isolation (bindend): Token-Mandant, Parameter-Override 422, CE-Payload-Strip,
MCP Cross-Tenant Postfach 404, CE dryRun ohne Schreibwirkung. Passwort nicht im Audit.

## Ehrlich blocked (Audit)

| Mask-Action | Grund |
|-------------|-------|
| `fuhrpark/*:speichern` / `fahrzeug-stamm:loeschen` (5) | REST vorhanden, Repository ohne Token-`tenant_id` — Isolation-Blocker |
| `personal/onboarding\|qualifikationen\|schulungen:speichern` (3) | Kein tenant-gebundenes HTTP-CommandEndpoint |

`*:neu` Form-Reset bleibt `local_ui` (kein Fake-Endpoint).

Non-Goals unberuehrt: FIN-CLOSE, Zahlauf, keine DB/Migration.

## Kennzahlen

| Metrik | Wert |
|--------|------|
| mapped | **33** (+3) |
| blocked_no_endpoint | **8** (−3) |
| local_ui | **13** |
| open_high | **1** (Zahlauf) |
| Registry | **48** Tools (+3) |

## Nachweis

```bash
python scripts/generate_screen_action_catalog.py --check
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_ce_batch3_hr_postfach.py \
  tests/test_mcp_mask_action_map.py tests/test_mcp_tool_registry.py \
  tests/test_mcp_local_action_classification.py \
  tests/test_mcp_tenant_isolation_all.py \
  --noconftest -q --override-ini addopts=''
```

Kein Commit/Push; keine DB.
