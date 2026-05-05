# Integration Bootstrap Readiness

Stand: `2026-04-12`

## Zweck

Repo-seitige Referenz fuer Integrationen, die bei frischen GitHub-Spiegeln oder neuen Umgebungen regelmaessig an fehlenden Secrets, Zielsystem-URLs oder Betriebsparametern scheitern.

## Repo-seitig jetzt vorhanden

- `.env.example` enthaelt die zentralen Variablen fuer:
  - OIDC
  - NATS Event Bus
  - Superglue
  - Vault / Secret-Provider
  - CRM-Downstream-URLs
- `python scripts/check_integration_bootstrap.py` liefert einen kompakten Readiness-Bericht.
- `python scripts/check_integration_bootstrap.py --strict` bricht bei fehlenden Pflichtvoraussetzungen ab.
- `python scripts/check_integration_bootstrap.py --probe-plan` gibt den daraus abgeleiteten Live-Probe-Plan aus.
- `python scripts/check_integration_bootstrap.py --strict-live` bricht ab, wenn eine Integration nicht bereit fuer einen echten Live-Probe ist.

## Live-Probe-Plan

Der Readiness-Bericht enthaelt jetzt zusaetzlich `probe_plan`.
Dieser Plan fuehrt keine Live-Requests automatisch aus, sondern benennt pro Integration:

- `status`: `ready`, `blocked`, `disabled` oder `manual`
- `probe_kind`: z. B. `http_get`, `http_get_authenticated`, `nats_connect` oder `provider_smoke`
- `target`: Ziel-URL oder Provider-Ziel, soweit aus der Umgebung ableitbar
- `command_hint`: konkreter Startpunkt fuer den produktionsnahen Smoke-Test
- `blocked_by`: fehlende Variablen oder Secrets

Damit bleibt CI deterministisch, waehrend Ops in einer echten Umgebung dieselben Checks gegen reale Zielsysteme ausfuehren kann.

## Gepruefte Integrationsbereiche

### OIDC

- erwartet `OIDC_CLIENT_ID` oder `KEYCLOAK_CLIENT_ID`
- erwartet `OIDC_ISSUER_URL` oder `KEYCLOAK_URL`
- Dev-Bypass ueber `API_DEV_TOKEN` bleibt fuer lokale Entwicklung moeglich, ersetzt aber keine tenant-sichere Produktivkonfiguration

### NATS Event Bus

- Dev-Compose startet NATS jetzt automatisch
- Backend nutzt in Docker-Dev standardmaessig:
  - `EVENT_BUS_ENABLED=true`
  - `EVENT_BUS_PROVIDER=nats`
  - `EVENT_BUS_NATS_URL=nats://nats:4222`
- Live-Probe: `nats server check --server <EVENT_BUS_NATS_URL>` oder aequivalenter JetStream-Client.

### Superglue

- Readiness prueft:
  - `SUPERGLUE_ENABLED`
  - `SUPERGLUE_BASE_URL` oder `SUPERGLUE_REST_URL`
  - `SUPERGLUE_AUTH_TOKEN` direkt oder ueber Secret-Provider
- Tenant-spezifische Secrets bleiben fuer echte Produktivnutzung weiterhin ops-seitig notwendig
- Live-Probe: authentifizierter HTTP-Health-Check gegen die konfigurierte Superglue-Basis-URL.

### Voice

- Browser-Fallback ist moeglich
- Serverseitige Provider benoetigen i. d. R. `OPENAI_API_KEY` bzw. provider-spezifische Secrets

### CRM Downstream

- Readiness prueft:
  - `CRM_CORE_BASE_URL`
  - `CRM_SALES_BASE_URL`
  - `CRM_SERVICE_BASE_URL`
- Live-Probe: HTTP-Health-Checks gegen alle drei Downstream-URLs im gleichen Tenant-/Netzwerkkontext.

## Was repo-seitig nicht geloest werden kann

- produktive Tenant-Secrets
- produktive Zielsystem-URLs
- produktive Alerting-, Retention- und Betriebsparameter
- fachlich freigegebene Cutover-Mappings fuer L3/FIBU

## Verweis

- [Open Gaps and Known Issues](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
