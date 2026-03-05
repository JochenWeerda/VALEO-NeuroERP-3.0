# FIBU Connectoren Lohn & VALEO Suite Anlagen (Asset Ledger) – Status und Blueprint

## Klarstellung: VALEO Suite Anlagen (Asset Ledger) = Anlagenbuchhaltung

**VALEO Suite Anlagen (Asset Ledger)** bündelt die **Anlagenbuchhaltung**: Stammdaten, Anlagevermögen, Abschreibungen, Umbuchungen, Abgänge. Die Anlagen-UI (`/fibu/anlagen`) existiert bereits; die Suite-Seite (`/fibu/anlagen-suite`) vereint Anlagenverwaltung und Import/Connector. Intern wird der Connector-Typ **ASSET_LEDGER** verwendet (kein geschützter Markenname im System).

---

## Bereits entwickelt (Stand vor Blueprint)

### Backend
| Komponente | Status | Datei / Tabelle |
|------------|--------|------------------|
| Lohn-Connector API | Stub | `app/api/v1/endpoints/lohn_connector.py` – Runs CRUD, Trigger (erzeugt nur Run, keine echten Buchungen) |
| Asset Ledger API | Stub | `app/api/v1/endpoints/asset_ledger_connector.py` – Config CRUD, Sync (Stub); Bezeichnung: VALEO Suite Anlagen |
| Lohn-Import-Runs Tabelle | ✅ | `domain_erp.lohn_import_runs` (period, source, status, journal_entry_count, totals, message) |
| Connector-Configs | ✅ | `domain_erp.connector_configs` (tenant, connector_code, name, config_json, is_active) – 1 pro Mandant+Code |
| FIBU-Audit | ✅ | `app/core/fibu_audit.py` – `log_fibu_audit()` |
| GoBD-Artefakt (docflow) | ✅ | `app/core/gobd_artifact.py` – `register_artifact()`; Tabelle `domain_docflow.document_artifacts` (FK auf `document_headers`) |
| Bulk-Journal-Import | ✅ | `app/api/v1/endpoints/bulk_journal_import.py` – CSV-Parse, Validierung, sofortige Buchung (kein Run/Preview/Artefakt) |
| Journal Entries | ✅ | `domain_erp.journal_entries` / `journal_entry_lines`; Repository + CRUD; **kein** `source_system`/`source_ref` in DB |
| Anlagen (Fixed Assets) | ✅ | Frontend `fibu/anlagen.tsx` + API (Anlagennr, AfA, Buchwert) |

### Frontend
| Komponente | Status |
|------------|--------|
| Lohn-Connector Seite | ✅ `pages/fibu/lohn-connector.tsx` – Periode, Trockenlauf, Runs-Tabelle, Trigger, Delete (implementiert: handleDelete + deleteRun.mutate, Stand 2025-03-05) |
| VALEO Suite Anlagen | ✅ `pages/fibu/anlagen-suite.tsx` – Anlagenverwaltung + Import/Connector; `/fibu/quadriga-connector` → Weiterleitung auf Suite |
| Schnittstellen-Center | ✅ Lohn + VALEO Suite Anlagen (Asset Ledger) als „Aktiv“, Link `/fibu/anlagen-suite` |
| Navigation | ✅ Lohn-Connector, VALEO Suite Anlagen (Asset Ledger) unter FIBU |

---

## Was fehlt (Blueprint)

1. **Einheitliches Connector-Framework**
   - Tabellen: **Profile** (pro Typ, mit settings/mapping), **Runs** (Status: DRAFT→PARSED→VALIDATED→POSTED/FAILED/CANCELLED/REVERSED), **Run-Items** (Zeilen mit payload + validation_errors + posted_entity_id).
   - Idempotency pro Run (`idempotency_key` unique pro Tenant+Connector).
   - Artefakte: Original-Upload + Protokoll (Hash + storage_key). Da `document_artifacts` FK auf `document_headers` hat: Artefakt-Metadaten auf Run speichern (storage_key, sha256, file_name) oder eigene Tabelle ohne FK.

2. **Workflow**
   - Upload → Parse → Validate → Post (→ optional Reverse). Kein sofortiges Buchen wie beim Bulk-Import; Preview und Fehlerbehandlung pro Run.

3. **Parser/Mapping**
   - Konfigurierbarer Parser (CSV/ASC) mit Profil (Delimiter, Encoding, Spalten-Mapping, Konto-/Steuerschlüssel-Maps).
   - Payroll-DTO: booking_date, document_no, text, lines (account, contra_account, dc, amount, tax_code, cost_center).
   - Asset-Ledger-DTO: wie Payroll + optional asset_no, asset_name, posting_type (depr/acq/disposal).

4. **Journal-Verdrahtung**
   - Beim Post: Journal Entries anlegen mit **source_system** (PAYROLL/ASSET_LEDGER) und **source_ref** (run_id). Dazu Spalten in `domain_erp.journal_entries` ergänzen (falls nicht vorhanden).
   - Reverse: Gegenbuchungen erzeugen, Run-Status REVERSED; kein Löschen.

5. **Audit + GoBD**
   - Jede Transition (upload, parse, validate, post, cancel, reverse) → `log_fibu_audit(entity_type="connector_run", ...)`.
   - Beim Upload: Artefakt-Metadaten (Hash + storage_key) am Run speichern; optional Protokoll nach Post.

6. **Frontend**
   - Connector Home (letzte Runs, Buttons Import / Profile / Runs).
   - Profile Manager (CRUD, Default, settings/mapping).
   - Import-Wizard: Upload → Preview → Validate → Post → Ergebnis (Link Journal).
   - Run Details: Status, Counts/Totals, Fehler-Items, Download Original/Protokoll, Reverse wenn POSTED.

7. **Tests**
   - Parser-Unit-Tests (Fixtures CSV/Asset Ledger), Workflow-Integration, Idempotency, GoBD (posted nur reverse, kein delete).

---

## Was sofort verdrahtet werden kann

- **Schnittstellen-Center**: VALEO Suite Anlagen (Asset Ledger) – Anlagenbuchhaltung; Pfad `/fibu/anlagen-suite`. `/fibu/quadriga-connector` zeigt dieselbe Suite.
- **Bestehende Lohn/Asset-Ledger-Endpoints** beibehalten und schrittweise durch das neue Framework ergänzen: zuerst neue Tabellen + API unter `/api/v1/fibu/connectors/` (Profile, Imports, parse/validate/post/reverse); Frontend kann dann Wizard und Run-Details an die neue API anbinden; alte Lohn-/Quadriga-Routen für Übergangszeit parallel lassen.
- **Bulk-Journal-Import**: Logik (CSV-Parse, Validierung, Kontenprüfung) als Referenz für konfigurierbaren Parser und Validierung im Workflow nutzen; kein Ersetzen, sondern neues Modul „FIBU Connectors“.

---

## Empfohlene Reihenfolge

1. **DB-Migration**: `domain_erp.fibu_connector_profiles`, `fibu_connector_runs`, `fibu_connector_run_items` (+ Artefakt-Felder auf Run).
2. **Backend**: Parser-Interface + Payroll/Asset-Ledger-Parser (Stub/minimal), Workflow-Service (upload→parse→validate→post→reverse), API `fibu_connectors.py` (Profile CRUD, Import-Run-Endpoints).
3. **Journal**: Spalten `source_system`, `source_ref` in `journal_entries` (Migration), beim Post setzen; Filter in Journal-UI.
4. **Frontend**: Connector Home, Profile Manager, Import-Wizard, Run-Details; API-Client für neue Endpoints.
5. **Schnittstellen-Center**: Beschreibung Quadriga = Anlagen; ggf. Pfade auf Suite-Struktur umstellen.

---

## Umgesetzt (diese Session)

- **Migration** `fibu_connector_framework_20260301`: `domain_erp.fibu_connector_profiles`, `fibu_connector_runs`, `fibu_connector_run_items` (inkl. Idempotency-Index, Artefakt-Felder auf Run).
- **Backend** `app/core/connectors/`: Parser-Interface + DTOs (`base.py`), `PayrollParser`, `AssetLedgerParser`, Workflow (`workflow.py`: create_run, set_run_artifact, parse_run, validate_run, post_run, cancel_run, reverse_run).
- **API** `app/api/v1/endpoints/fibu_connectors.py`: Profile CRUD, `POST /{PAYROLL|ASSET_LEDGER}/imports` (Upload+Parse), `GET /imports/{run_id}`, `GET /imports/{run_id}/items`, `POST .../validate`, `.../post`, `.../cancel`, `.../reverse`. Router unter `/api/v1/finance/connectors`.
- **Schnittstellen-Center**: VALEO Suite Anlagen (Asset Ledger); Anlagenbuchhaltung gebündelt. Migration `fibu_connector_asset_ledger_rename_20260301`: QUADRIGA → ASSET_LEDGER.
- **Journal**: Beim Post wird `reference = run_id` gesetzt (Drilldown im Journal über Beleg/Referenz). Spalte `source_system` in `journal_entries` optional später ergänzbar.

## Nächster konkreter Schritt

Frontend: Connector Home, Import-Wizard (Upload → Preview → Validate → Post), Profile Manager, Run-Details an die neue API `/api/v1/finance/connectors` anbinden. Migration ausführen: `alembic upgrade head`.
