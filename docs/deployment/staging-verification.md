# Staging Verification Runbook

## Ziel
Schnelle Verifikation nach jedem Staging-Deployment.

## Checks
1. Health: `/healthz`, `/readyz`
2. OpenAPI: `/docs`, `/api/v1/openapi.json`
3. Kernmodule: CRM, Einkauf, Finance (Smoke)
4. Eventbus/Outbox: keine stuck events
5. Fehlerquote/Latency: innerhalb SLO

## Beispiel
```bash
curl -fsS https://staging.example.com/healthz
curl -fsS https://staging.example.com/readyz
curl -fsS https://staging.example.com/api/v1/openapi.json > /dev/null
```
