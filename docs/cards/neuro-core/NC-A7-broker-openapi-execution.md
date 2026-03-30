# NC-A7 - Broker OpenAPI Execution Adapter

**Lane:** NC-A
**Prioritaet:** P1
**Status:** umgesetzt
**Abhaengigkeit:** NC-A6 (Neuro Tool Broker)

## Kontext

NC-A6 hat den Broker-Rahmen geschaffen, aber MCP-Tool-Aufrufe wurden nur simuliert (`_simulate_tool_call`). State-Graph-Transitionen blieben im Status `planned` ohne DB-Persistenz, und der Execution-Pfad erzeugte keinen per-Step Audit Trail.

## Umsetzung

### 1. Fallback-Handling fuer OpenAPI-Execution

`_execute_tool_contract()` in `neuro_tool_broker.py` unterscheidet jetzt:

- `mode: openapi_internal` (HTTP 2xx) → `step_status: executed`
- `mode: fallback_contract` + HTTP 5xx → `step_status: failed` (Plan bricht ab)
- `mode: fallback_contract` + HTTP 4xx / Transport-Error → `step_status: degraded` (Plan laeuft weiter)

### 2. State-Graph-Mutations-Persistenz

Neue Methode `_persist_state_transition()`:

- Nach erfolgreicher Execution (`executed` oder `delegated`) wird die Transition in die DB geschrieben
- `StateNodeRecord` wird aktualisiert oder neu angelegt
- `StateTransitionRecord` wird append-only geschrieben
- Status wechselt von `planned` → `committed`
- Ohne DB-Session: graceful skip

### 3. Per-Step Audit Trace

Neue Methode `_record_step_audit()`:

- Jeder Step schreibt einen Audit-Eintrag in `domain_shared.neuro_step_audit_trace`
- Felder: plan_id, step_id, action, binding_kind, binding_target, step_status, execution_detail (JSON)
- Ohne DB-Session: silent skip

## Dateien

| Datei | Aenderung |
|-------|-----------|
| `app/services/neuro_tool_broker.py` | Fallback-Handling, `_persist_state_transition()`, `_record_step_audit()`, `_build_state_summary()` erweitert |
| `tests/test_neuro_tool_broker.py` | 9 neue Tests (13 gesamt) |
| `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md` | Neuro Tool Broker auf 90%, Completion Plan |
| `docs/project-context/open-gaps-and-known-issues.md` | NC-A7 Status, 4-Wave-Plan |
| `docs/agent-ops/active-workboard.md` | NC-A7 abgeschlossen |

## Verifikation

```bash
pytest tests/test_neuro_tool_broker.py -v --no-cov   # 13 passed
pytest tests/test_neuro_pipeline.py tests/test_neuro_planner.py tests/test_neuro_intent_engine.py -v --no-cov  # 64 passed
```

## Offene Folgearbeit

- **Wave 2:** Verification + Policy Engine Integration (check_policy_conformity → evaluate_policy_set)
- **Wave 2:** State-Transition-Checks unifizieren (Verification Engine → StateGraphService)
- **Wave 3:** Decision Trace Hash-Chain Tamper-Detection (NC-D5)
- Echter HTTP-Client fuer externe Services (aktuell TestClient intern)
