# Monitoring Dashboard Verifikation

## Pflicht-Dashboards
- API Errors (5xx)
- API Latency (p95/p99)
- DB Connections / Slow Queries
- Worker/Outbox Queue Backlog
- Host CPU/RAM/Disk

## Sollwerte
- 5xx-Rate < 1%
- p95 < 500ms (kritische Endpunkte)
- Outbox Backlog stabil bzw. ruecklaeufig
- Keine dauerhaften DB-Pool-Exhaustion Events

## Freigabekriterium
Release nur freigeben, wenn in den letzten 30 Minuten alle Dashboards im gruennen Bereich sind.
