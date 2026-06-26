# Production Readiness Runbook

## Zweck

Dieses Runbook ist die aktive operative Evidence fuer Release-, Betriebs- und
Pruefer-Gates. Historische Langfassungen liegen unter `docs/_internal/archive/`;
dieses Dokument bleibt der aktuelle Einstieg fuer CI, externe Pruefersimulation
und Go-live-Entscheidungen.

## Harte Repo-Gates

Vor einem produktiven Release muessen lokal und in CI gruen sein:

- TypeScript, Lint, Backendtests und migrationsnahe Tests.
- `python scripts/check_openapi_docs.py --threshold 0`.
- `node scripts/docs-governance-check.cjs`.
- `node scripts/docs-code-sync-check.cjs`.
- Security Scan mit blockierenden High/Critical-Funden.
- SBOM-Erzeugung und Artefakt-Upload.

## Externe Gates

Folgende Punkte bleiben blockierend, bis reale Evidenz vorliegt:

- Steuerberater-Abnahme der konkreten Verfahrensdokumentation.
- Hersteller-/Pruefwerkzeug-Abnahme mit produktiver TSE.
- DSB-/Rechtsfreigabe inklusive AVV/DSFA.
- Betriebsuebung mit realem Cluster und Alarmkanal.
- Beobachteter Restore-/Incident-Drill im produktionsnahen Cluster.

## Deployment-Ablauf

1. Release-Artefakte unveraenderlich mit `sha-${GITHUB_SHA}` bauen.
2. Migration in eigenem Preflight ausfuehren.
3. Helm-Deployment mit `--atomic --wait` ausrollen.
4. `/readyz` und fachliche Smoke-Routen pruefen.
5. Bei negativem Smoke kein manuelles Weiterdruecken; Rollback ausfuehren.

## Rollback

- Anwendung: `helm rollback` auf die letzte bekannte gute Revision.
- Datenbank: nur dokumentierte Alembic-Downgrades oder vorbereiteter Forward-Fix.
- Bei nicht rueckwaerts-kompatiblem Datenvertrag: Deployment stoppen und
  Incident-Runbook aktivieren.

## Wiederanlauf und Nachweis

- Backup-/Restore-Drill dokumentieren.
- Alarmweg und Bereitschaft pruefen.
- Smoke-, Rollback- und Restore-Ergebnisse als Release-Evidence ablegen.
- Offene externe Gates in `docs/project-context/open-gaps-and-known-issues.md`
  sichtbar halten.
