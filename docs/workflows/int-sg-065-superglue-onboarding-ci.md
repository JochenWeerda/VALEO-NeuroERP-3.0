# INT-SG-065 - Superglue Onboarding CI

## Ziel

Die neuen Onboarding-Artefakte im bestehenden Superglue-Infra-Workflow automatisch rendern.

## Umgesetzt

- `.github/workflows/superglue-infra.yml` richtet Python ein, installiert Dependencies und rendert `json`, `env` und `vault` fuer einen Beispiel-Tenant.

## Verifikation

- Workflow `Superglue Infra`
