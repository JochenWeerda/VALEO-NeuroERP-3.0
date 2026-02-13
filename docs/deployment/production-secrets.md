# Production Secrets Checklist

Diese Datei standardisiert die fuer Deployments benoetigten GitHub Actions Secrets.

## Pflicht-Secrets
- `DATABASE_URL`
- `SECRET_KEY`
- `ENCRYPTION_KEY`
- `REDIS_URL`
- `OIDC_ISSUER_URL`
- `OIDC_JWKS_URL`
- `OIDC_CLIENT_ID`
- `OIDC_CLIENT_SECRET`

## Verifikation in CI
1. Workflow mit Environment `production` ausfuehren.
2. Preflight-Job prueft, ob alle Variablen vorhanden sind.
3. Deployment-Job nur bei erfolgreichem Preflight freigeben.

## Rotation
- Quartalsweise Rotation fuer App-Secrets.
- Sofortrotation bei Security Incident.
