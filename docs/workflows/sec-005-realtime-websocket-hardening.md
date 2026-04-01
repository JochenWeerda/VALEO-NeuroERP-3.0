# SEC-005 - Realtime-WebSocket-Hardening

## Ziel

Die generischen Realtime-WebSockets fuer POS, Workflow und Policy sollen nicht mehr anonym erreichbar sein und keine offensichtlichen Tenant-Leaks ueber gemeinsame Broadcast- oder Cache-Namensraeume behalten.

## Umsetzung

- `app/api/v1/endpoints/websocket.py`
  - POS- und Workflow-WebSockets verlangen jetzt explizite Bearer-Tokens
  - `tenant_id` wird aus Query oder Header gelesen und an die Session gebunden
  - POS-Verbindungen werden intern ueber `tenant_id:terminal_id` gruppiert statt nur ueber `terminal_id`
  - Workflow-Status liest jetzt `workflow:{tenant_id}:{workflow_id}:status` statt tenant-freier Cache-Keys
- `app/policy/router.py`
  - Policy-WebSocket verlangt jetzt expliziten Bearer-Token
  - fuer echte JWTs werden `admin`/`manager` Rollen verlangt; der explizite Dev-Token bleibt fuer lokale Entwicklung zulaessig
- `tests/test_security_realtime_websockets.py`
  - deckt Token-Pflicht fuer alle drei WS-Pfade ab
  - prueft tenant-getrennte POS-Registrierung und tenant-scoped Workflow-Status-Lookup

## Ergebnis

- drei vorher anonyme Realtime-Pfade sind jetzt geschlossen
- POS-Broadcasts teilen sich keinen tenant-fremden Registry-Key mehr
- Workflow-Status kann nicht mehr ueber einen globalen Cache-Key tenant-fremd gelesen werden

## Restpunkte

- weitere fachspezifische WS-/SSE-Pfade ausserhalb dieses Slices koennen aehnliche Haertung noch brauchen
- fuer produktive Browser-WS bleibt Query-Token ein Zwischenstand bis ein zentraler Cookie-/Subprotocol-Ansatz existiert
