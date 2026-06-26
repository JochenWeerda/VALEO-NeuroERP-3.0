# L3 -> VALEO NeuroERP Import Pipeline

Dieses Dokument beschreibt den aktuellen repo-seitigen Stand fuer die Migration aus einer bestehenden `service-erp`-/L3-Installation in VALEO NeuroERP.

Der Fokus liegt bewusst auf sicherer Erstinstallation und belastbarer Cutover-Vorbereitung:

- Dry-Run ist Standard.
- Legacy-Daten landen zunaechst roh in `l3_staging`.
- Jeder Execute-Lauf wird in `app_control.l3_import_runs` protokolliert.
- Destruktive Bootstrap-Schritte brauchen explizite Bestaetigung.
- Repo-seitig vorbereitbare Ops-Artefakte fuer Superglue/Erstinstallation werden direkt mit erzeugt.

Das Dokument beschreibt nicht die spaeteren fachlichen Transformationsregeln je Domäne. Diese folgen nach Domain-Owner-Review auf Basis des Stagings.

## 1. Zielbild

Fuer eine saubere Erstinstallation mit Altbestandsuebernahme besteht der Sollpfad aus vier Schritten:

1. Datenbankschema und Basiskonfiguration reproduzierbar bootstrapen.
2. Externe Ops-Werte vorbereiten: Secrets, Zielsystem-URLs, Policy-/Retention-Werte.
3. Legacy-L3-Exporte vertraglich pruefen und roh in `l3_staging` laden.
4. Fachliche Transformations- und Cutover-Schritte je Domäne getrennt darauf aufsetzen.

## 2. Verfuegbare Repo-Werkzeuge

### 2.1 Erstinstallations-Bundle

```bash
python scripts/prepare_first_install.py \
  --tenant default \
  --mapping config/l3_mapping.yaml \
  --raw docs/data/l3/raw_tables.json \
  --output-dir runtime/first-install/bundle
```

Das Bundle enthaelt:

- `install-context.json`
- `README.md`
- `superglue-onboarding.json`
- `superglue-onboarding.env`
- `superglue-onboarding.vault`

Damit sind alle repo-seitig vorbereitbaren Artefakte fuer eine jungfraeuliche Erstinstallation sofort verfuegbar.

### 2.2 Datenbank-Bootstrap

```bash
python scripts/bootstrap_db.py \
  --seed \
  --superglue-tenant default \
  --report-json runtime/first-install/bootstrap-report.json
```

Wichtige Eigenschaften:

- erkennt die Laufzeitumgebung ueber `VALEO_ENV` bzw. `settings.APP_ENV`
- bricht auf nicht-leerer DB standardmaessig ab
- `--force` ist nur mit exaktem Token `DELETE-<ENV>` zulaessig
- produktionsaehnliche Umgebungen brauchen zusaetzlich `--allow-prod-force`
- optionaler Backup-Pfad vor destruktivem Reset:

```bash
python scripts/bootstrap_db.py \
  --force \
  --confirm DELETE-DEVELOPMENT \
  --backup-before-force \
  --backup-dir logs/db/backups
```

- optionaler Export der repo-lokalen Superglue-Onboarding-Artefakte:
  - `superglue-onboarding.json`
  - `superglue-onboarding.env`
  - `superglue-onboarding.vault`

### 2.3 Mapping- und Quelldatenvalidierung

```bash
python scripts/validate_mapping.py \
  --mapping config/l3_mapping.yaml \
  --raw docs/data/l3/raw_tables.json
```

Der Validator bleibt die Source of Truth fuer Mapping- und Vertragspruefung gegen die L3-Metadaten.

### 2.4 L3-Rohimport in die Landing Zone

Dry-Run:

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --report-json runtime/first-install/l3-dry-run-report.json
```

Execute-Lauf:

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --execute \
  --backup-before-execute \
  --report-json runtime/first-install/l3-execute-report.json
```

Wichtige Eigenschaften:

- Dry-Run ist implizit, solange `--execute` nicht gesetzt ist
- unterstuetzte Formate: `csv`, `tsv`, `json`
- jeder Execute-Lauf schreibt Metadaten nach `app_control.l3_import_runs`
- Legacy-Rohdaten werden tabellenweise in `l3_staging.<legacy_table>` geladen
- Quellspalten werden zusaetzlich in `_payload` gesichert
- Logging landet standardmaessig in `logs/db/import_l3.log`
- vor Execute kann automatisch ein `pg_dump` erstellt werden

Optionale inkrementelle Vorbereitung:

```bash
python scripts/import_l3.py \
  --mapping config/l3_mapping.yaml \
  --source data/l3_export \
  --since 2026-03-01T00:00:00Z \
  --since-column UPDATED_AT
```

Unterstuetzt werden bevorzugte Legacy-Zeitspalten wie `UPDATED_AT`, `MODIFIED_AT`, `AENDERUNGSDATUM`, `CHANGE_DATE`, `DTAENDERUNG` oder `DATUM`.

## 3. Erwartete Quelldaten aus service-erp / L3

Fuer einen echten Execute-Cutover werden extern bereitgestellt:

- vollstaendige Exportdateien je L3-Tabelle im Verzeichnis `data/l3_export`
- die zugehoerige Tabellen-/Spaltenbeschreibung in `docs/data/l3/raw_tables.json`
- bei Delta-Cutover: belastbare Aenderungszeitspalten oder fachlich freigegebene Extraktionskriterien

Die Dateien koennen als CSV, TSV oder JSON vorliegen. Pro gemappter L3-Tabelle wird eine Datei mit passendem Tabellennamen erwartet.

## 4. FIBU- und Journal-Migration

Repo-seitig ist der vorbereitete Stand wie folgt:

- Finanzjournal-Modelle liegen in `domain_erp.journal_entries` und `domain_erp.journal_entry_lines`.
- Die UStVA-/VAT-Sicht kann fuer Plausibilisierung und Vorab-Abgleich ueber `GET /api/v1/vat-return/vorberechnung` genutzt werden.
- Der aktuelle L3-Import fuehrt noch keine fachliche Buchungslogik in `domain_erp` aus, sondern erzeugt bewusst erst eine nachvollziehbare Roh-Landing-Zone in `l3_staging`.

Das ist Absicht. Fuer FIBU-Daten aus einer bisherigen `service-erp`-Installation gilt:

1. zuerst Rohuebernahme nach `l3_staging`
2. dann fachliches Mapping auf Konten, Steuerkennzeichen, Perioden und Belegarten
3. danach kontrollierte Uebernahme in `domain_erp` mit Finance-Owner-Freigabe
4. abschliessend Abstimmung gegen UStVA-/Saldo-/Offene-Posten-Sichten

Damit ist die technische Migrationsvorbereitung im Repo geschlossen, ohne ungesicherte Annahmen ueber die Alt-FIBU zu erzwingen.

## 5. Erstinstallations- und Cutover-Reihenfolge

Die empfohlene Reihenfolge fuer eine jungfraeuliche Erstinstallation mit Altmigration ist:

1. `python scripts/prepare_first_install.py`
2. externe Ops-Werte ausserhalb des Repos setzen:
   - Tenant-Secrets
   - produktive Zielsystem-URLs
   - Environment-spezifische Policy-/Retention-Werte
3. `python scripts/bootstrap_db.py --seed --superglue-tenant <tenant>`
4. `python scripts/import_l3.py ...` ohne `--execute`
5. Findings mit Fachbereichen pruefen
6. `python scripts/import_l3.py ... --execute --backup-before-execute`
7. domänenspezifische Transformations- und Cutover-Schritte auf Basis von `l3_staging`
8. Finance-/FIBU-Abstimmung gegen UStVA- und Journalsichten

## 6. Verbleibende externe Blocker

Nicht repo-seitig abschliessbar bleiben:

- echte produktive Tenant-Secrets
- produktive Zielsystem-URLs je Environment
- finale Alerting-/Retention-/Policy-Werte je Umgebung
- vollstaendige L3-/service-erp-Quelldumps fuer den Execute-Lauf

## 7. Verweis

Das konsolidierte Runbook fuer Erstinstallation und Cutover steht zusaetzlich in [first-install-and-l3-cutover.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/db/first-install-and-l3-cutover.md).
