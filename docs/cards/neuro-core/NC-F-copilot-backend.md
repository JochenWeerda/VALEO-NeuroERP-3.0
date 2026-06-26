# NC-F — Copilot Backend + Interaction State

**Lane:** Neuro-Core (Lane F)
**Prioritaet:** P2
**Status:** umgesetzt (F1–F5; NC-F5 Copilot-Pipeline abgeschlossen)

## Kontext
Der VALEO Copilot braucht Echtzeit-Streaming statt Request/Response.
WebSocket mit Token-Auth und Reconnect fuer stabile Sessions.

## Loesung
WebSocket-Endpoint ws://host/api/v1/copilot/chat mit chunked Streaming.
Frontend-Hook useCopilotStream mit automatischem Reconnect.
Interaction State FSM (NC-002) fuer Session-Zustandsverwaltung.

## Dateien
- `app/api/v1/endpoints/copilot_ws.py` — WebSocket-Endpoint
- `packages/frontend-web/src/features/copilot/useCopilotStream.ts` — React Hook
- `app/services/interaction_state_manager.py` — FSM (via NC-002)
