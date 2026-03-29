# NC-F5 — Copilot Pipeline Integration

**Lane:** NC-F (Copilot Backend)
**Prioritaet:** P1 (abhaengig von Lane A)
**Status:** umgesetzt

## Kontext
Der Copilot WebSocket (NC-F3) hatte bisher nur einen Stub-Response.
NC-F5 integriert die vollstaendige Neuro-Core Pipeline: Chat-Eingabe
wird klassifiziert, ein Plan generiert, verifiziert und ausgefuehrt.

## Loesung
`copilot_ws.py` ruft jetzt `run_pipeline()` auf und streamt das
formatierte Ergebnis als Chunks zurueck. Zusaetzlich wird das rohe
Pipeline-Ergebnis als `pipeline_result` Event gesendet.

## Dateien
- `app/api/v1/endpoints/copilot_ws.py` — Copilot WS mit Pipeline
