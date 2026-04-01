# SEC-003 - Auth-/Tenant-Hardening fuer Metrics und Copilot-WebSocket

## Ziel

Die bestaetigten Security-Funde fuer den Copilot-WebSocket und die Metrics-Surface sollen auf einen belastbaren Minimalstandard gezogen werden:

- kein anonymer Copilot-WebSocket mehr
- kein Tenant-Spoofing ueber WebSocket-Nachrichtenkontext
- Metrics liefern nur noch tenant-gebundene Business-KPIs

## Umsetzung

- `app/api/v1/endpoints/copilot_ws.py`
  - akzeptiert nur noch explizite Bearer-Tokens (Query `token` oder `Authorization`-Header)
  - bindet die Session an den authentifizierten `tenant_id`
  - ignoriert nachgelieferte `tenant_id`-/`user_id`-/`roles`-Overrides im Nachrichtenkontext
- `app/api/v1/endpoints/system_metrics.py`
  - nutzt explizite Auth-/Tenant-Dependencies
  - surfact `tenant_id` und `user_id` im Response
  - filtert Outbox- und Approval-KPIs tenant-spezifisch
- `packages/frontend-web/src/features/copilot/useCopilotChat.ts`
  - reicht vorhandenen Access-Token und Tenant an den WebSocket weiter
- `packages/frontend-web/src/features/copilot/useCopilotStream.ts`
  - schreibt `token` und `tenant_id` in den WebSocket-Handshake

## Tests

- `tests/test_security_metrics_and_copilot_ws.py`
  - Metrics liefern Tenant-/User-Kontext nur mit gueltigem Token
  - Copilot-WebSocket lehnt fehlende Tokens mit Policy-Violation ab
  - Tenant-Spoofing im Nachrichtenkontext ueberschreibt die authentifizierte Session nicht

## Ergebnis

- der bestaetigte unauthentifizierte Copilot-WS-Pfad ist geschlossen
- Copilot-Sessions bleiben an den Handshake-Tenant gebunden
- tenant-uebergreifende Business-Metrics-Leaks sind fuer diese Surface beseitigt

## Restpunkte

- weitere SAST-Funde ausserhalb dieses Slices bleiben offen, insbesondere breite API-Auth-/Tenant-Pruefung in fachlichen Routern
- Browser-WebSockets bleiben auf Query-Token angewiesen, solange kein Cookie-/Subprotocol-basiertes Auth-Muster eingefuehrt ist
