---
title: Production-Readiness Runbook
type: runbook
audience: [betrieb, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Fail-closed Freigabemodell, simulierte Prüferprofile, externe Gates für VALEO NeuroERP Go-Live.
---

# Production Readiness Runbook

Stand: 2026-06-09

## Freigabeprinzip

VALEO verwendet ein fail-closed Freigabemodell. Ein fehlender, nicht
ausgefuehrter oder nur dokumentierter Nachweis gilt nicht als bestanden.

Die simulierten Prueferprofile sind eine interne Vorabnahme mit mindestens den
Anforderungen der referenzierten offiziellen Standards. Sie ersetzen keine:

- Steuerberater- oder Wirtschaftsprueferfreigabe
- Kassen-Nachschau, TSE-Hersteller- oder DSFinV-K-Pruefwerkzeugabnahme
- Datenschutzfreigabe, AVV oder DSFA-Unterschrift
- BSI-/ISO-Zertifizierung
- Hardware-, Eich- oder Wiederanlaufabnahme im Zielbetrieb

## Kanonischer Releasepfad

1. `quality-gate.yml` prueft Code, Tests, Abhaengigkeiten, SBOM und
   Produktionsvertrag.
2. `security-scan.yml` blockiert High/Critical-Befunde aus ZAP, Trivy, Grype,
   Bandit, pip-audit und pnpm audit.
3. `deploy-staging.yml` baut getrennte, unveraenderliche Backend- und
   Frontend-Images `sha-<git-sha>`, migriert die Staging-Datenbank, deployt
   atomar und prueft `/healthz` sowie `/readyz`.
4. Die Staging-Abnahme dokumentiert den getesteten vollen Commit-SHA.
5. `valeo-erp-deployment.yml` wird manuell mit genau diesem 40-stelligen SHA
   gestartet. Das GitHub-Environment `production` muss Reviewer erzwingen.
6. Vor dem Rollout laeuft erneut die volle Release-Pruefung und danach ein
   separater Migrationsjob.
7. Helm deployed mit `--atomic`; fehlgeschlagene Smokes loesen zusaetzlich ein
   Rollback aus.

Ressourcenintensive lokale Gates laufen seriell. Insbesondere werden
Voll-Pytest, Frontend-Build, Dependency-Audits und Auditor-Simulation nicht
gleichzeitig in einem Windows-Prozessraum gestartet. CI darf sie parallel nur
in voneinander isolierten Jobs mit eigenen Runner-Ressourcen ausfuehren.

Abhaengigkeits-, Vertrags- und Major-Upgrade-Regeln:
[Dependency and Compatibility Maintenance](dependency-and-compatibility-maintenance.md).

## Pflicht-Secrets

GitHub-Environment `staging`:

- `KUBE_CONFIG` als Base64-kodierte kubeconfig
- `STAGING_URL`
- `STAGING_HOST`

GitHub-Environment `production`:

- `KUBE_CONFIG` als Base64-kodierte kubeconfig
- `PRODUCTION_URL`

Im Cluster:

- `valeo-erp-runtime`: `DATABASE_URL`, `OIDC_ISSUER_URL`, `OIDC_CLIENT_ID`
  und erforderliche Provider-Secrets
- `valeo-erp-database`: Schluessel `password` fuer Backup und Restore-Test

## Production Preflight

```bash
python scripts/check_production_readiness.py \
  --environment production \
  --compose-file docker-compose.production.yml \
  --helm-values k8s/helm/valeo-erp/values-production.yaml \
  --contract-only
```

Im Zielprozess wird `--contract-only` entfernt. Blockiert werden:

- `API_DEV_TOKEN`
- `DEBUG=true`, Demo-Modus, `--reload`, `start-dev`
- Wildcard-Hosts
- Default-/Beispiel-Secrets
- Inline-Secrets statt Secret-Injection
- mutable Image-Tags
- fehlendes produktives Frontend oder ein Vite-Entwicklungsserver im Image
- deaktivierte Backups oder Restore-Tests
- hostexponierte Datenbank-, Redis- oder NATS-Ports

## Simulierte externe Pruefer

```bash
python scripts/simulate_external_assessors.py \
  --output-json artifacts/production-readiness-assessment.json \
  --output-markdown artifacts/production-readiness-assessment.md
```

Profile:

- Steuerberater/GoBD
- KassenSichV/DSFinV-K
- BSI/ISO-27001 Informationssicherheit
- Datenschutz
- Betrieb/Notfallmanagement

VALEO fordert zusaetzlich automatisierte Repository-Evidenz, blockierende
Security-Scans, negative Tenant-Tests, unveraenderliche Images und
regelmaessige Restore-Proben. Ein Profil bleibt `conditional`, solange reale
Live-Evidenz oder eine externe Freigabe fehlt.

Die UI wird als statischer Build ueber einen nicht privilegierten Nginx
ausgeliefert. Helm routet `/api`, `/healthz` und `/readyz` zum Backend und alle
UI-/Deep-Link-Pfade zum Frontend mit SPA-Fallback. Ein Backend-only-Release ist
damit kein gueltiger Produktionsrelease.

## Rollback und Notfall

- Applikationsrollback: `helm rollback <release> -n <namespace> --wait`
- Datenbankmigrationen werden nicht blind downgraded. Bei inkompatibler
  Migration gilt der dokumentierte Kompensations-/Restorepfad.
- Vor risikoreichen Migrationen muss ein aktuelles Backup vorhanden sein.
- Der woechentliche Restore-Test ist ein Produktions-Gate.
- Fehlgeschlagener Restore, unerreichbarer Alarmkanal oder offene
  High/Critical-Schwachstellen blockieren neue Releases.

## Offizielle Mindestquellen

- GoBD-Aenderung vom 14.07.2025:
  https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2025-07-14-GoBD-2-aenderung.html
- KassenSichV, zuletzt geaendert am 14.01.2026:
  https://www.gesetze-im-internet.de/kassensichv/BJNR351500017.html
- DSFinV-K 2.4:
  https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Weitere-Steuerthemen/Abgabenordnung/2025-07-24-dsfinvk-2-4.html
- BSI IT-Grundschutz:
  https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html
- DSGVO:
  https://eur-lex.europa.eu/eli/reg/2016/679/oj

## Release-Evidence-Gate (RELEASE-EVIDENCE-GATE-001)

### Überblick

Vor jedem Staging- oder Produktions-Release aggregiert `scripts/release_evidence_report.py`
alle Qualitätsdimensionen in einem maschinenlesbaren Report.

### Dimensionen

| Dimension | Tool | Blockierend |
|---|---|---|
| drift | `doc_drift_report.py --fail-over 0` | ja (fail) |
| openapi | `generate_openapi.py --check` | ja (fail) |
| inventories | Datei-Existenz-Check | ja (fail) |
| coverage | `check_critical_backend_coverage.py` | nein (warn) |
| slice_harness | `valeo_slice.py list` | nein (warn) |
| external | `artifacts/production-readiness-assessment.json` | nein (warn) |

### Lokal ausführen

```bash
python scripts/release_evidence_report.py --fail-on-red
# → artifacts/release_evidence.json
# → artifacts/release_evidence.md
```

### CI-Integration

Läuft als letzter Step in `.github/workflows/release-gates.yml`.
`--fail-on-red`: Exit 1 wenn mindestens eine Dimension `fail` hat.
WARN-Dimensionen blockieren nicht, erscheinen aber im Report.
