# AGRAR-PERF-01 Lasttest (Wiegeschein / Abrechnung)

## Ziel

Lasttest für die kritischen Agrar-APIs:
- `GET /api/v1/weighing-tickets`
- `POST /api/v1/weighing-tickets`
- `POST /api/v1/agrar/settlements/billing-weight/preview`

## Voraussetzungen

1. Backend läuft und ist erreichbar.
2. Testmandant existiert.
3. `k6` ist installiert.

## Ausführung

PowerShell:

```powershell
./scripts/run-agrar-loadtest.ps1 `
  -BaseUrl "http://localhost:8000" `
  -ApiToken "dev-token" `
  -TenantId "00000000-0000-0000-0000-000000000001"
```

Direkt mit `k6`:

```bash
BASE_URL=http://localhost:8000 \
API_TOKEN=dev-token \
TENANT_ID=00000000-0000-0000-0000-000000000001 \
k6 run tests/performance/agrar-core-loadtest.js
```

## Thresholds

- `http_req_failed < 2%`
- `http_req_duration p(95) < 900ms`
- `http_req_duration p(99) < 1500ms`
- `agrar_billing_preview_duration p(95) < 1000ms`

## Ergebnisartefakt

`reports/performance/agrar-perf-summary.json`

Dieses JSON ist der Nachweis für:
- erreichte Last
- Fehlerrate
- p95/p99-Latenz

## Bewertung

`AGRAR-PERF-01` gilt als bestanden, wenn alle Thresholds grün sind und keine systematischen 5xx-Fehler auftreten.
