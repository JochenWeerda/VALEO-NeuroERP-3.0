# First Install And L3 Cutover

Dieses Runbook schliesst den repo-seitig vorbereitbaren Teil einer jungfraeulichen Erstinstallation von VALEO NeuroERP inklusive Datenuebernahme aus einer bestehenden `service-erp`-/L3-Installation.

## Ziel

Am Ende dieses Pfads liegen vor:

- gebootstrapte VALEO-Datenbank
- exportierte Superglue-/Ops-Onboarding-Artefakte
- validierte L3-Quelldaten
- roh geladene Legacy-Daten in `l3_staging`
- nachvollziehbare Import-Run-Historie in `app_control.l3_import_runs`

## 1. Bundle vorbereiten

```bash
python scripts/prepare_first_install.py \
  --tenant default \
  --output-dir runtime/first-install/bundle
```

Pruefen:

- `runtime/first-install/bundle/install-context.json`
- `runtime/first-install/bundle/README.md`
- `runtime/first-install/bundle/superglue-onboarding.json`
- `runtime/first-install/bundle/superglue-onboarding.env`
- `runtime/first-install/bundle/superglue-onboarding.vault`

## 2. Externe Ops-Werte setzen

Vor dem Live-Cutover ausserhalb des Repos bereitstellen:

- Tenant-Secrets
- produktive Zielsystem-URLs
- Environment-spezifische Alerting-, Retention- und Policy-Werte
- vollstaendige L3-/service-erp-Exportdateien

## 3. Datenbank bootstrapen

```bash
python scripts/bootstrap_db.py \
  --seed \
  --superglue-tenant default \
  --report-json runtime/first-install/bootstrap-report.json
```

Force-Reset nur bei bewusstem Neuaufsetzen:

```bash
python scripts/bootstrap_db.py \
  --force \
  --confirm DELETE-DEVELOPMENT \
  --backup-before-force \
  --allow-prod-force
```

## 4. L3-Dry-Run

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --report-json runtime/first-install/l3-dry-run-report.json
```

Optional fuer Delta-/Vorbereitungslaeufe:

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --since 2026-03-01 \
  --since-column UPDATED_AT
```

## 5. Execute in die Landing Zone

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --execute \
  --backup-before-execute \
  --report-json runtime/first-install/l3-execute-report.json
```

Erwartetes Ergebnis:

- `l3_staging.<legacy_table>` ist gefuellt
- `app_control.l3_import_runs` dokumentiert den Lauf
- `logs/db/import_l3.log` enthaelt den Nachweis

## 6. Finance / FIBU nach dem Rohimport

Der Repo-Stand bereitet die FIBU-Migration vor, fuehrt sie aber nicht blind fachlich aus.

Verfuegbar sind:

- `domain_erp.journal_entries`
- `domain_erp.journal_entry_lines`
- UStVA-Vorberechnung unter `GET /api/v1/vat-return/vorberechnung`

Empfohlener Cutover:

1. Legacy-FIBU zunaechst roh ueber `l3_staging` nachvollziehbar laden
2. Konten-/Steuer-/Perioden-Mapping mit Finance fachlich freigeben
3. erst dann transformiert in `domain_erp` uebernehmen
4. UStVA-/Saldo-/OP-Abgleich fahren

## 7. Was offen bleibt

Dieses Runbook schliesst den repo-internen Vorbereitungsstand. Offen bleiben nur externe oder fachlich freigabepflichtige Punkte:

- Live-Secrets
- produktive Zielsysteme
- finale Environment-Policies
- echte Exportdumps aus dem bisherigen Produktivsystem
- fachliches Konten-/Beleg-/Steuer-Mapping fuer FIBU
