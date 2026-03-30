# NC-A6 - Neuro Tool Broker

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt

## Kontext

Der Execute-Pfad der Neuro-Core-Pipeline war bisher ein Platzhalter: Schritte wurden nur als `executed` oder `delegated` markiert. Ein zentraler Broker fuer Tool-Auswahl, Preconditions, Retry-/Rollback-Vorbereitung und Step-Trace fehlte.

## Umsetzung

- `NeuroToolBroker` als zentraler Orchestrator eingefuehrt.
- Plan-Schritte werden typisiert auf MCP-Contracts, Business-Commands, Capability-Delegation oder Human Gates gebunden.
- Step-Verifikation und State-Transition-Summary sind in den Broker integriert.
- Pipeline nutzt jetzt Broker-Output fuer `executed_steps`, `tool_trace`, `state_summary` und `rollback_plan`.

## Verifikation

- `pytest tests/test_neuro_tool_broker.py tests/test_neuro_pipeline.py -q --no-cov`
- `python -m py_compile app/services/neuro_tool_broker.py app/agents/neuro_pipeline.py`

## Offene Folgearbeit

- echter Tool-Client fuer MCP-/OpenAPI-Aufrufe
- persistente State-Graph-Mutationen nach erfolgreicher Tool-Execution
- per-Step-Persistenz im Decision Trace
