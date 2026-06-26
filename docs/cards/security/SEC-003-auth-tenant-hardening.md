# SEC-003 - Metrics und Copilot-WebSocket haerten

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_metrics_and_copilot_ws.py, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

## Ziel

Bestaetigte Security-Funde fuer Copilot-WebSocket und Metrics-Surface mit kleinem Dateibesitz schliessen.

## Scope

- `app/api/v1/endpoints/copilot_ws.py`
- `app/api/v1/endpoints/system_metrics.py`
- `packages/frontend-web/src/features/copilot/useCopilotChat.ts`
- `packages/frontend-web/src/features/copilot/useCopilotStream.ts`
- `tests/test_security_metrics_and_copilot_ws.py`

## Abnahme

- Copilot-WebSocket akzeptiert keine anonymen Verbindungen mehr
- `tenant_id` aus dem Handshake bleibt fuer die Session verbindlich
- Metrics surfacen Tenant-/User-Kontext und filtern Business-KPIs tenant-spezifisch
- Regressionstests sind gruen

## Risiken

- andere WebSocket-/Realtime-Pfade ausserhalb dieses Slices koennen aehnliche Auth-Luecken behalten
- Query-Token im Browser ist nur ein Zwischenstand bis ein produktiveres WS-Auth-Schema vorliegt
