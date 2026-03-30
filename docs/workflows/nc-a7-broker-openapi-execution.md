# NC-A7 — Broker OpenAPI Execution Adapter

## Ziel

Die MCP-Tool-Simulation im Neuro Tool Broker durch echte OpenAPI-Execution ersetzen, State-Graph-Mutationen nach Execution persistieren und per-Step Audit Traces schreiben.

## Vorbedingung

- NC-A6 (Neuro Tool Broker) abgeschlossen
- `NeuroToolExecutionService` in `app/services/neuro_tool_execution.py` vorhanden
- State-Graph-Modelle (`StateNodeRecord`, `StateTransitionRecord`) in DB-Schema `domain_shared`

## Ablauf

```mermaid
sequenceDiagram
    participant P as Pipeline
    participant B as ToolBroker
    participant E as ExecutionService
    participant API as FastAPI (TestClient)
    participant DB as PostgreSQL

    P->>B: execute_plan(plan, db)
    loop Fuer jeden Step
        B->>B: _resolve_binding(step)
        B->>B: _verify_step(step)
        B->>B: _build_state_transition(step)
        alt MCP Tool Binding
            B->>E: execute_contract(contract, params)
            E->>API: HTTP Request (GET/POST)
            API-->>E: HTTP Response
            E-->>B: {mode, http_status, response}
            alt mode == openapi_internal
                B->>B: step_status = executed
            else mode == fallback_contract, 5xx
                B->>B: step_status = failed
            else mode == fallback_contract, 4xx
                B->>B: step_status = degraded
            end
        else Command Binding
            B->>B: _dispatch_command(step)
        end
        alt Step erfolgreich (executed/delegated)
            B->>DB: _persist_state_transition()
        end
        B->>DB: _record_step_audit()
    end
    B-->>P: {status, executed_steps, tool_trace, state_summary}
```

## Status

| Schritt | Status |
|---------|--------|
| Fallback-Handling (5xx/4xx/transport) | abgeschlossen |
| State-Graph-Persistenz nach Execution | abgeschlossen |
| Per-Step Audit Trace | abgeschlossen |
| Tests (13/13 gruen) | abgeschlossen |
| Card + Workflow-Doku | abgeschlossen |

## Naechste Schritte

→ Wave 2: Verification + Policy Integration
