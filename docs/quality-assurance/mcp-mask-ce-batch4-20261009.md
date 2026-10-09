---
title: MCP Mask CE Batch4 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Batch4 — Personal Training CE+MCP; Fuhrpark blocked_missing_tenant (keine Migration).
---

# MCP-MASK-CE-BATCH4-20261009

## Gewaehlt / geliefert

| Mask-Action | Klassifikation | CE / MCP |
|-------------|----------------|----------|
| `personal/onboarding:speichern` | mapped | CE `/api/v1/training/onboarding/runs/actions/speichern` + `hr.onboarding.speichern` |
| `personal/qualifikationen:speichern` | mapped | CE `/api/v1/training/qualifications/actions/speichern` + `hr.qualifikation.speichern` |
| `personal/schulungen:speichern` | mapped | CE `/api/v1/training/assignments/actions/speichern` + `hr.schulung.speichern` |

Service+Mandant klar: `domain_hr.*` mit `tenant_id` + Token-`get_tenant_id`.
Checkliste/Kurs Cross-Tenant → 404. Isolation: Override 422, dryRun ohne Schreibwirkung.

## Fuhrpark — blocked_missing_tenant

| Mask-Action | Gap |
|-------------|-----|
| `fuhrpark/*:speichern` + `fahrzeug-stamm:loeschen` (5) | Repository ohne `tenant_id`; kein MCP-Write |

**Folge-Claim (nicht dieser Slice):** additive `tenant_id`-Spalte + Mandanten-SQL
im Fuhrpark-Repository, danach CE+MCP. Keine DB/Migration hier.

## Kennzahlen

| Metrik | Wert |
|--------|------|
| mapped | **36** (+3) |
| blocked_missing_tenant | **5** |
| blocked_no_endpoint | **0** |
| local_ui | **13** |
| open_high | **1** (Zahlauf) |
| Registry | **51** Tools (+3) |

## Nachweis

```bash
python scripts/generate_screen_action_catalog.py --check
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_ce_batch4_training.py \
  tests/test_mcp_mask_action_map.py tests/test_mcp_tool_registry.py \
  tests/test_mcp_local_action_classification.py \
  --noconftest -q --override-ini addopts=''
```

Kein Commit/Push; keine DB/Migration.
