# SEC-028 - Security Observability

## Ziel

Blockierte Security-Ereignisse sollen nicht nur lokal in Exceptions enden, sondern zentral sichtbar werden.

## Umsetzung

- neuer zentraler In-Memory-Recorder `security_observability.py`
- neue REST-Surface `GET /security/monitoring/{metrics,health,events}`
- Verdrahtung in:
  - `outbound_security.py` fuer blockierte SSRF-/Egress-Ziele
  - `tenant_isolation_guard.py` fuer denied und verbund-erlaubte Cross-Tenant-Entscheidungen

## Abnahme

- dedizierte Regressionen fuer Metrics, Health und Event-Filter
- bestehende SSRF- und Tenant-Isolation-Tests bleiben gruen

## Restrisiko

- aktuell rein In-Memory; keine Langzeitpersistenz oder externes Alerting
