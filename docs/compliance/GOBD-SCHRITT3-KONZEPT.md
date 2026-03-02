# GoBD Schritt 3 – Konzept & umgesetzte Maßnahmen

**Bezug:** GoBD-VORGEHENSPLAN.md, Docflow (domain_docflow), E-Rechnung ab 01.01.2025.

Dieses Dokument beschreibt die **umgesetzten** Punkte von Schritt 3 sowie die **Konzept-Grundlagen** für Nummernkreise, Archiv, Betriebsprüfung und E-Rechnung (spätere Implementierung).

---

## 1. Umgesetzt (Schritt 3)

### 1.1 Doppelbelege & „Save macht POST“

- **Idempotency bei Create (POST):** Tabelle `domain_docflow.create_request_idempotency` (tenant_id, idempotency_key → doc_id). Optionaler Request-Parameter `idempotency_key` (8–120 Zeichen); bei Wiederholung wird das bestehende Dokument zurückgegeben.
- **Docflow-Link UNIQUE:** Tabelle `domain_docflow.document_header_links` mit UNIQUE(tenant_id, from_header_id, relation_type). Verhindert mehrere Ziele pro Quelle und Relation (z. B. nur ein Lieferschein pro Auftrag).
- **Frontend:** Bei bestehendem `id` wird PUT verwendet, bei neuem Beleg nur POST; beim POST (Rechnung erstellen) wird optional `idempotency_key` (z. B. `crypto.randomUUID()`) mitgesendet.

### 1.2 Replace Items nur im DRAFT

- **Positionen ersetzen (DELETE + INSERT)** ist nur erlaubt, wenn `status = draft`. Bei freigegebenen/verbuchten Belegen: 409 mit Hinweis auf Storno/Berichtigung.
- **Storno:** Bereits über `DocflowReverseRequest.reason` und Endpoint reverse abgedeckt (Begründung + Referenz).

### 1.3 Statusmodell: „Printed“ / „Exported“ als Ereignis

- **document_headers:** Felder `printed_at`, `printed_by`, `print_count`; `exported_at`, `exported_by` (Migration `docflow_print_event_20260301`).
- **Endpoints:**
  - `POST /api/v1/docflow/{doc_id}/record-print` mit optionalem `printed_by`: setzt `printed_at = NOW()`, erhöht `print_count`.
  - `POST /api/v1/docflow/{doc_id}/record-export` mit optionalem `exported_by`: setzt `exported_at = NOW()`.
- Kein Status „printed“/„exported“ als Sperre; Druck/Export sind reine Event-Logs. **Frontend:** Nach tatsächlichem Druck/Export eines Docflow-Dokuments sollte der jeweilige Endpoint aufgerufen werden (z. B. nach PDF-Download oder Druckdialog).

### 1.4 Docflow-Drift (Konzept, teils vorbereitet)

- **Event-getriebene Projektion:** Outbox/Events bereits bei Convert; Snapshot/Hash bei released/posted ist für spätere Phasen vorgesehen (siehe Abschnitt 5).

---

## 2. Nummernkreise (Konzept)

- **Nummer erst bei „released“ vergeben;** im Entwurf nur UUID. Minimiert Lücken und Missbrauch.
- Falls Nummer bereits im Draft vergeben wird: **kein DELETE**, sondern `voided` + Grund + Zeitstempel.
- Technisch: `domain_docflow.number_series` (tenant_id, doc_type, year, counter) wird bei Convert/Freigabe genutzt; konsequente Nutzung nur bei released ist Ziel.

---

## 3. Unveränderbare Aufbewahrung (Archiv/DMS)

**Umgesetzt** (Migration `gobd_archiv_erechnung_20260301`, Endpoint-Modul `gobd_archiv.py`):

- Tabelle `domain_docflow.document_artifacts`: speichert Belegartefakte (PDF/XML/HTML) mit `content_hash_sha256` (SHA-256), `storage_key` (externer DMS-Pfad), `artifact_type`, `created_at`, `created_by`.
- **Endpoints:**
  - `POST /api/v1/gobd/artifacts` — Artefakt registrieren (Hash + Storage-Key)
  - `GET /api/v1/gobd/artifacts?header_id=…` — Artefakte eines Belegs auflisten
  - `GET /api/v1/gobd/artifacts/{id}/verify?provided_hash=…` — Integritätsprüfung: gespeicherter Hash vs. übergebenem Hash; Status `verified` | `mismatch` | `unchecked`
  - `GET /api/v1/gobd/artifacts/{id}/veri4` — Hash-Metadaten für Veri4-konforme Signaturprüfung
- **Hinweis:** Write-Once / Object-Lock muss auf Storage-Ebene (S3/MinIO-Bucket-Policy) konfiguriert werden; die DB speichert nur den unveränderlichen Hash-Record.
- **Referenz:** GoBD Aufbewahrung, Anhang 33.

---

## 4. Betriebsprüfung: Z1/Z2/Z3 / Datenüberlassung

**Umgesetzt** (Endpoint `GET /api/v1/gobd/audit-package`):

ZIP-Download mit standardisierter Z1/Z2/Z3-Struktur für die Betriebsprüfung (§ 147 AO / GoBD Rz. 156–164):

| Ordner | Inhalt |
|--------|--------|
| `Z1/data_dictionary.txt` | Export-Metadaten, Zeitraum, Tenant |
| `Z1/docflow_headers.csv` | Belegköpfe (Stammdaten, Nummern, Status) |
| `Z2/audit_logs.csv` | Audit-Log mit `old_values` / `new_values` |
| `Z2/journal_entries.csv` | Buchungssätze aus `domain_erp.finance_journal_entries` |
| `Z2/docflow_items.csv` | Belegpositionen (Artikel, Mengen, Preise) |
| `Z3/artifact_hashes.csv` | SHA-256-Hashes aller Belegartefakte |
| `integrity_manifest.csv` | SHA-256 pro ZIP-Datei zur Manipulation­serkennung |

- Query-Parameter: `from_date`, `to_date`, `tenant_id`
- Alle CSV-Exporte greifen ausschließlich auf unveränderliche GoBD-relevante Tabellen zu; bei DB-Fehler (fehlende Spalten/Schema) werden leere Header-Zeilen geschrieben (graceful degradation).
- **Referenz:** GoBD Datenzugriff, maschinelle Auswertbarkeit, BMF-Schreiben 2014 Rz. 155–164.

---

## 5. E-Rechnung ab 01.01.2025

**Umgesetzt** (Migration `gobd_archiv_erechnung_20260301`, Endpoint-Modul `gobd_archiv.py`):

- Tabelle `domain_docflow.invoice_xml_store`: speichert das führende XML-Original (XRechnung/ZUGFeRD) mit `content_hash_sha256`, `format_type`, `validation_status` (`pending` | `valid` | `invalid`), `validation_errors` (JSONB).
- **UNIQUE-Constraint** `uq_invoice_xml_header (tenant_id, header_id)`: pro Beleg nur ein führendes XML. Upsert-Logik: neues XML ersetzt altes und setzt `validation_status = pending`.
- **Endpoints:**
  - `POST /api/v1/gobd/e-invoice-xml` — XML als führendes Original speichern (XRechnung/ZUGFeRD)
  - `GET /api/v1/gobd/e-invoice-xml/{header_id}` — XML-Metadaten + Validierungsstatus abrufen
  - `PATCH /api/v1/gobd/e-invoice-xml/{header_id}/validate` — Validierungsergebnis setzen (`valid`|`invalid`|`pending` + optionale XSD-Fehlerdetails)
- **ZUGFeRD-Generierung:** `modules/agrar/services/self_billing_service.py` → `generate_einvoice_zugferd()` bettet XRechnung-XML via `factur-x` in PDF/A-3 ein.
- **Referenz:** GoBD 2. Änderung 2025, § 14 UStG, EN16931.

---

## 6. Architektur-Entscheidungen („KI-ERP“)

- **Event-Log + Projektion (Outbox/CDC):** Konsistente Daten, Auditspur, KI kann Ereignisse erklären.
- **Explainable Audit:** Jeder Statuswechsel/Convert mit menschenlesbarer Begründung im Auditlog.
- **Strikte State-Machine + DB-Constraints:** GoBD-Konformität technisch erzwungen (z. B. UNIQUE Docflow-Links, Replace nur DRAFT).

---

## 7. Migrationsübersicht (Schritt 3)

| Revision | Inhalt |
|----------|--------|
| `docflow_create_idemp_20260301` | create_request_idempotency, document_header_links (UNIQUE) |
| `docflow_print_event_20260301` | document_headers: printed_at, printed_by, print_count, exported_at, exported_by |
| `merge_heads_20260301` | Merge aller Branch-Heads (Agrar, Einkauf RE-Workflow, Docflow) → ein gemeinsamer Head |
| `gobd_archiv_erechnung_20260301` | domain_docflow.document_artifacts + invoice_xml_store (führendes XML, UNIQUE per Header) |
| `gobd_aufbewahrungsfristen_20260301` | domain_finance.aufbewahrungsfristen + 5 Seed-Datensätze (§147 AO / §257 HGB) |

**Hinweis:** Die Docflow-Migrationen hängen von `docflow_core_20260215` ab (Schema `domain_docflow`, Tabellen `document_headers` usw.).

---

## 8. Release / Neuinstallation (DB-Setup)

- **Alle Migrationen durchführen:** `alembic upgrade head` (führt bis zum einzigen Head `merge_heads_20260301` aus).
- **Init-Routine:** `scripts/init_db.py` führt `command.upgrade(alembic_cfg, "head")` aus (mit Retry bei Verbindungsfehlern). Für CI/Release wird das so aufgerufen.
- **Entrypoint (Backend-Container):** `entrypoint.sh` führt vor dem Start des Servers `alembic upgrade head` aus; bei Fehler wird der Container mit Exit-Code 1 beendet, damit Release/Neuinstallation nicht mit halb angewendeten Migrationen starten.
- **Voraussetzung:** Die Datenbank ist entweder leer (dann werden alle Migrationen in korrekter Reihenfolge angewendet) oder alle Vorgänger-Revisionen sind bereits angewendet. Ist die Tabelle `alembic_version` inkonsistent (z. B. Revision eingetragen, aber zugehörige Tabellen fehlen), muss der Zustand zuerst bereinigt werden (z. B. fehlende Tabellen anlegen oder Revision zurücksetzen).

### Tabellen manuell anlegen (bei inkonsistentem Zustand)

Wenn `alembic_version` bereits eine Docflow-Revision enthält (z. B. `docflow_core_20260215`), die Tabellen in `domain_docflow` aber fehlen:

1. **Tabellen anlegen** (Schema + alle Docflow-Tabellen bis inkl. docflow_pos_admin_dsfinvk, idempotent):
   - **Mit Python (empfohlen, nutzt DATABASE_URL aus .env):**
     ```bash
     python scripts/run_docflow_manual_tables.py
     ```
   - **Oder mit psql:**
     ```bash
     psql "$DATABASE_URL" -f scripts/sql/docflow_manual_create_tables.sql
     ```
     bzw. mit expliziter Verbindung:
     ```bash
     psql -h localhost -p 5432 -U valeo_dev -d valeo_neuro_erp -f scripts/sql/docflow_manual_create_tables.sql
     ```
2. **Anschließend:** `alembic upgrade head` ausführen (wendet die restlichen Migrationen an: create_request_idempotency, document_header_links, printed_at/print_count, Merge).

---

## 9. Nächste Schritte (optional)

- **Frontend:** In allen Masken, die Docflow-Dokumente drucken oder exportieren (z. B. Rechnungs-Editor, Belegfluss), nach erfolgreichem Druck/Export `POST /api/v1/docflow/{doc_id}/record-print` bzw. `record-export` mit optionalem `printed_by`/`exported_by` (z. B. aus User-Kontext) aufrufen, damit die Event-Felder gesetzt werden.
- **Nummernkreise:** Perspektivisch `doc_number` erst bei Übergang in „released” vergeben (heute kann das Frontend beim Create eine Nummer mitschicken); dann Draft nur mit interner UUID führen.
- **Storage / Object-Lock:** Bucket-Policy für `document_artifacts`-Storage auf Write-Once setzen (S3/MinIO Retention Mode). Integrity-Check-Job (Cronjob) einplanen: Hash aus Storage neu berechnen, mit `content_hash_sha256` aus DB vergleichen, Alarm bei Abweichung.
- **Prüfer-Zugang Z1 (UI):** Read-Only-Rolle für Betriebsprüfer mit Zugriff auf die GoBD-Endpoints (Artifacts, Audit-Package). Kein Schreibzugriff; separate RBAC-Rolle `auditor`.
