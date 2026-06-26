# SEC-005 - Realtime-WebSockets haerten

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_realtime_websockets.py

## Ziel

Anonyme Realtime-Endpunkte fuer POS, Workflow und Policy schliessen und die groebsten tenant-fremden Leak-Pfade beseitigen.

## Scope

- `app/api/v1/endpoints/websocket.py`
- `app/policy/router.py`
- `tests/test_security_realtime_websockets.py`
- `docs/workflows/sec-005-realtime-websocket-hardening.md`

## Abnahme

- POS-, Workflow- und Policy-WebSockets akzeptieren keine anonymen Verbindungen mehr
- POS-Terminal-Raeume sind tenant-getrennt
- Workflow-Status liest tenant-scoped Cache-Keys
- Regressionstests sind gruen

## Risiken

- andere Realtime-Pfade ausserhalb dieses Slices koennen noch nachziehen muessen
- Query-Token im Browser ist weiterhin nur ein pragmatischer Zwischenstand
