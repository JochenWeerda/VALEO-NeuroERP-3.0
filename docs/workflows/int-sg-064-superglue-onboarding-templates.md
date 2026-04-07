# INT-SG-064 - Superglue Onboarding Templates

## Ziel

Direkt aus dem Onboarding-Pack `.env`- und Vault-nahe Templates rendern.

## Umgesetzt

- `app/integrations/services/superglue_onboarding_templates.py` rendert `json`, `env` und `vault`.
- Die Templates enthalten nur Key-Kandidaten und Policy-Werte.

## Verifikation

- `python scripts/superglue/export-onboarding-pack.py --tenant ci-tenant --format env`
- `python scripts/superglue/export-onboarding-pack.py --tenant ci-tenant --format vault`
