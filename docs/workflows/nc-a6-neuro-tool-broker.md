# NC-A6 - Neuro Tool Broker + Pipeline-Integration

## Ziel

Den bisherigen Platzhalter-Execute-Pfad der Neuro-Core-Pipeline durch einen zentralen Broker ersetzen, der Plan-Schritte typisiert auf Tools, Commands, Capability-Delegation und Human Gates aufloest.

## Ablauf

1. Pipeline klassifiziert den Input und erzeugt einen `ExecutionPlan`.
2. `NeuroToolBroker` resolved jeden `PlanStep` auf einen zentralen Binding-Typ:
   - `mcp_tool`
   - `command`
   - `capability`
   - `gate`
   - `generic`
3. Vor jedem Step laeuft eine Step-Verifikation mit Verification Engine.
4. Bei vorhandener State-Graph-Context-Info wird ein geplanter Transition-Kandidat erzeugt.
5. Schreibende Commands laufen ueber `ActionExecutionService` mit Idempotency-Key pro Step.
6. Approval-Step oder High-Risk-Plan stoppt kontrolliert mit `awaiting_approval`.
7. Pipeline liefert `tool_trace`, `state_summary` und optionalen `rollback_plan` zurueck.

## Betroffene Dateien

- `app/services/neuro_tool_broker.py`
- `app/agents/neuro_pipeline.py`
- `tests/test_neuro_tool_broker.py`
- `tests/test_neuro_pipeline.py`

## Ergebnis

- Tool-Auswahl ist nicht mehr ueber Pipeline, MCP-Registry und Command-Layer verstreut.
- Step-Level-Approval ist sichtbar, auch wenn der Gesamtplan nicht global auf `requires_human_approval` steht.
- Der Pipeline-Response enthaelt jetzt nachvollziehbare Broker-Trace-Daten statt rein synthetischer `executed`-Marker.

## Bekannte Restgrenzen

- MCP-Tools werden aktuell kontraktbasiert orchestriert, aber noch nicht real ueber einen produktiven Tool-Client ausgefuehrt.
- State-Graph-Integration erzeugt derzeit nur Transition-Kandidaten im Response, keine persistente Graph-Mutation.
- Decision Protocol speichert weiterhin den Plan und die globale Verification; per-Step-Trace ist vorerst nur im Pipeline-Response verfuegbar.
