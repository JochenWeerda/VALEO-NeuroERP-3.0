# NC-A — Neuro-Core Kernel (Intent Engine + Planner)

**Lane:** Neuro-Core (Lane A — Kern-Lane)
**Prioritaet:** P1 (hoechste)
**Status:** umgesetzt (A1-A5)

## Kontext
Lane A ist die Kern-Lane des Neuro-Core. Alle anderen Lanes (D4, F5, H4, H5)
haengen von der Intent Engine und dem Planner ab. Ohne Intent-Klassifikation
und Plan-Generierung kann keine AI-gesteuerte Aktion ausgefuehrt werden.

## Loesung
Intent Engine mit 11 deutschen Intent-Patterns und Capability-Matching auf die
6 bestehenden NeuroASSIST-Capabilities. Planner mit 9 vordefinierten Plan-Templates
und typisierten Schritten (validation, query, command, gate, notification).
Vollstaendige Pipeline: Classify -> Plan -> Verify -> Execute mit Decision Protocol.

## Dateien
- `app/agents/neuro_intent_engine.py` — Intent Engine (A1/A2)
- `app/agents/neuro_planner.py` — Planner (A3/A4)
- `app/agents/neuro_pipeline.py` — Pipeline (A5)
- `app/api/v1/endpoints/neuro_pipeline.py` — REST-API
- `docs/workflows/nc-a-neuro-core-kernel.md` — Workflow-Doku

## Abhaengigkeiten
- Verification Engine (NC-001) fuer Plan-Pruefung
- Decision Protocol (NC-D3) fuer Audit
- NeuroASSIST Capability Registry (bestehend)
