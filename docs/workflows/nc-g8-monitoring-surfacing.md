# NC-G8 - Monitoring Surfacing

## Ziel

Die bereits vorhandene Event-Bus-Observability soll als leicht konsumierbares REST-Surfacing fuer Betrieb und Incident-Analyse bereitstehen.

## Umsetzung

- neue REST-Endpunkte:
  - `GET /api/v1/neuro/event-bus/metrics`
  - `GET /api/v1/neuro/event-bus/health`
  - `GET /api/v1/neuro/event-bus/errors`
- Surfacing basiert direkt auf `event_bus_observer`

## Ergebnis

- Betriebsmetriken, Health und Fehlerhistorie sind ohne direkten Codezugriff abrufbar
- Monitoring kann jetzt an Dashboards, Admin-Flows oder Alerting angedockt werden
