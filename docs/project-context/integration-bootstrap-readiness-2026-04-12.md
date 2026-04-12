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

### Superglue

- Readiness prueft:
  - `SUPERGLUE_ENABLED`
  - `SUPERGLUE_BASE_URL` oder `SUPERGLUE_REST_URL`
  - `SUPERGLUE_AUTH_TOKEN` direkt oder ueber Secret-Provider
- Tenant-spezifische Secrets bleiben fuer echte Produktivnutzung weiterhin ops-seitig notwendig

### Voice

- Browser-Fallback ist moeglich
- Serverseitige Provider benoetigen i. d. R. `OPENAI_API_KEY` bzw. provider-spezifische Secrets

### CRM Downstream

- Readiness prueft:
  - `CRM_CORE_BASE_URL`
  - `CRM_SALES_BASE_URL`
  - `CRM_SERVICE_BASE_URL`

## Was repo-seitig nicht geloest werden kann

- produktive Tenant-Secrets
- produktive Zielsystem-URLs
- produktive Alerting-, Retention- und Betriebsparameter
- fachlich freigegebene Cutover-Mappings fuer L3/FIBU

## Verweis

- [Open Gaps and Known Issues](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/open-gaps-and-known-issues.md)
- [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
