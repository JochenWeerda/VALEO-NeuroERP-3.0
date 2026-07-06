---
title: Mask Runtime API (Entwickler)
type: reference
audience: [entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-06-29
version: 1.0.0
description: REST- und Frontend-API der Universal Mask Runtime — ScreenDefinition, Readiness, AgentContract, ActionRuntime.
---

# Mask Runtime API — Entwicklerreferenz

Kanonischer Architekturstand: [Universal Mask Runtime Status](../architecture/uix/universal-mask-runtime-status.md)

## Backend-Endpunkte

| Methode | Pfad | Zweck |
|---------|------|-------|
| GET | `/api/v1/masks/{mask_id}/screen-definition` | Native `ScreenDefinition` JSON |
| GET | `/api/v1/masks/{mask_id}/agent-contract` | `AgentMaskContract` (Human + Agent) |
| GET | `/api/v1/masks/{mask_id}/readiness` | Generator-Readiness-Report |
| GET | `/api/v1/masks/{mask_id}/entity/{entity_id}` | Generischer Kopf-Stub für Wave-2-SDs ohne Domain-Entity-API |
| GET | `/api/v1/mask-rollouts/{screen_id}/{entity_id}/screen-summary` | Rollout Summary + `tab_endpoints` |
| GET | `/api/v1/mask-rollouts/.../tabs/{tab_key}` | Lazy Tab mit Query-Parametern |

### Tab-Query-Parameter

```text
page, limit (max 50), q, sort, sort_dir, filter_plan (JSON)
```

- Sort/Filter nur gegen Whitelist aus `ScreenDefinition` (`get_sortable_columns`, `get_filterable_columns`).
- Ungültiges `filter_plan` → **422**.

### FilterPlan (JSON)

Operatoren: `eq`, `neq`, `contains`, `lt`, `lte`, `gt`, `gte`, `in`, `between`.

Beispiel:

```json
{
  "logic": "and",
  "conditions": [
    { "column": "status", "op": "eq", "value": "offen" }
  ]
}
```

## Readiness-Gates

Implementierung:

- Backend: `app/api/v1/endpoints/mask_screen_definition.py` → `_check_readiness()`
- Frontend: `packages/frontend-web/src/components/mask-builder/runtime/generatorReadiness.ts`

**Mandatory** (blockieren `generatorReady`):

`schema_valid`, `non_temporary`, `data_sources`, `table_data_source_bound`, `table_columns_complete`, `actions_classified`

**Advisory** (Score 0–1, warnen nur):

`sort_whitelist`, `filter_columns`, `agent_contract`, `workflow_declared`, `stable_test_selectors`, `table_query_contract`

## Frontend-Runtime

| Modul | Pfad |
|-------|------|
| Master-Hook | `runtime/useUniversalMaskRuntime.ts` |
| Form State | `runtime/useUniversalFormState.ts` |
| Actions | `runtime/useActionRuntime.ts` |
| Workflow | `runtime/useWorkflowState.ts` |
| Agent Contract | `runtime/generateAgentMaskContract.ts` |
| Readiness | `runtime/generatorReadiness.ts` |

### ActionRuntime-Modi

| Modus | Body-Feld | Verhalten |
|-------|-----------|-----------|
| validate | `_mode: "validate"` | Nur Validierung |
| dryRun | `_mode: "dryRun"` | Simulation ohne Persistenz |
| propose | `_mode: "propose"` | Vorschlag für Human Approval |
| execute | (default) | Persistenz + Audit |

Zusatzfelder: `_auditReason`, `_idempotencyKey`

Beispiel CRM: `POST /api/v1/crm/customers/{id}/actions/create_activity`

## Tests

```bash
pytest tests/test_agent_mask_contract.py
pytest tests/test_uix035_action_runtime_crm.py
pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/mask-builder/runtime/generatorReadiness.test.ts
```

## ScreenDefinition registrieren

1. `build_*_screen_definition()` in `app/core/screen_definitions.py`
2. Registry: `SCREEN_DEFINITION_BUILDERS`
3. Readiness prüfen: `GET /api/v1/masks/{id}/readiness`
4. Parity-Matrix unter `docs/architecture/domains/{domain}/`

## Verweise

- [RenderPlan Architecture](../architecture/uix/render-plan-architecture.md)
- [ADR-011 UI-Maskenstrategie](../adr/adr-011-ui-maskenstrategie.md)
- [Agent-Runbook](../agent-docs/runbooks/mask-runtime-agent-modus.md)
- [Agent-Handbuch](../agent-handbuch/index.md) — generierte Prozessketten, Masken-API-Katalog, MCP/Events
