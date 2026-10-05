# Lasttests — Erntepeak-Szenario (Gap 037)

Ziel: 500 gleichzeitige Nutzer während Ernte-Hochphase, P95-Antwortzeit < 800ms.

## Voraussetzungen

```bash
# k6 installieren (https://k6.io/docs/getting-started/installation/)
choco install k6        # Windows
brew install k6         # macOS
apt install k6          # Debian/Ubuntu
```

## Szenarien

| Script | Zweck | Dauer | Max VU |
|--------|-------|-------|--------|
| `health-check.js` | Pre-deploy-Gate | < 60s | 1 |
| `harvest-peak.js` | Erntepeak (`PROFILE=full`) | ~20 min | 800 |
| `harvest-peak.js` | Lokal (`PROFILE=local`) | ~2,5 min | 50 |
| `harvest-peak.js` | Smoke (`PROFILE=smoke`) | 30 s | 5 |

## Profile (SPEC-P1-10)

| PROFILE | Wann |
|---------|------|
| `full` | Staging / Peak (Default, CI Schedule) |
| `local` | Gegen docker-compose / `localhost:8000` |
| `smoke` | Schneller Smoke nach Deploy lokal |

## Ausführen

```bash
# Health-Check (CI/CD-Gate)
k6 run tests/load/health-check.js

# Lokal reproduzierbar (wartet auf Health, schreibt Summary)
pwsh scripts/loadtest/run_harvest_peak_local.ps1
# oder: ./scripts/loadtest/run_harvest_peak_local.sh [local|smoke]

# Manuell mit Profil
k6 run -e PROFILE=local -e BASE_URL=http://127.0.0.1:8000 tests/load/harvest-peak.js

# Gegen Staging-Umgebung (Vollprofil)
k6 run \
  --env PROFILE=full \
  --env BASE_URL=https://staging.valeo-erp.de \
  --env API_DEV_TOKEN=<token> \
  --env TENANT_ID=tenant-staging \
  tests/load/harvest-peak.js

# Mit JSON-Report
k6 run --out json=results/harvest-peak.json tests/load/harvest-peak.js
```

## SLA-Schwellwerte (Thresholds)

| Metrik | Schwelle |
|--------|----------|
| `http_req_duration p95` | < 800ms |
| `http_req_duration p99` | < 2000ms |
| `http_req_failed` | < 2% |
| `annahme_duration_ms p95` | < 600ms |
| `qualitaet_duration_ms p95` | < 700ms |
| `einlagerung_duration_ms p95` | < 600ms |
| `warteschlange_duration_ms p95` | < 400ms |

## Kern-Workflow (Erntepeak)

```
Nutzer → Warteschlange lesen
      → LKW registrieren (POST /api/v1/annahme/warteschlange)
      → Qualitätsprüfung (POST /api/v1/agrar/quality-protocols)
      → Einlagerung buchen (POST /api/v1/lager/einlagerung)
```

## Last-Stufen

| Phase | VUs | Dauer |
|-------|-----|-------|
| Normalbetrieb | 50 | 5 min |
| Erntepeak-Rampe | 50 → 500 | 4 min |
| Erntepeak-Sustained | 500 | 5 min |
| Spike | 800 | 2 min |
| Abklingen | → 0 | 1 min |

## GitHub Actions

Der Workflow `.github/workflows/load-test.yml` läuft:
- Täglich 04:00 UTC gegen Staging
- Bei Push auf `main` (Health-Check-Gate)
- Manuell via `workflow_dispatch`
