---
title: Buchungen Audit-Pfad (GoBD)
type: reference
audience: [security, tenant-admin, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Zentraler Audit-Pfad für Buchungen (GoBD-Nachvollziehbarkeit)

## Übersicht

Jede Erstellung oder inhaltliche Änderung einer Buchung (`domain_erp.journal_entries`) muss in `domain_shared.audit_logs` nachvollziehbar sein. Dafür wird durchgängig **ein zentraler Mechanismus** genutzt: **`log_fibu_audit()`** aus `app.core.fibu_audit`.

- **Aufruf:** `log_fibu_audit(db, tenant_id, "create"|"update"|"post"|"reverse"|"delete", "journal_entry", entry_id, changes_dict, request=...)`
- **Tabelle:** Einträge landen in `domain_shared.audit_logs` (Spalten: `entity_type`, `entity_id`, `action`, `changes`, `timestamp`, …).

Neue Buchungspfade (neue Features, neue Connector, neue Importe) **müssen** unmittelbar nach dem Anlegen/Ändern der Buchung ebenfalls `log_fibu_audit(..., "journal_entry", entry_id, ...)` aufrufen.

---

## Pfade, die Buchungen anlegen (Stand: dokumentiert)

| Pfad | Datei / Ort | Audit-Aufruf |
|------|-------------|--------------|
| **Journal-API (CRUD)** | `app/api/v1/endpoints/journal_entries.py` | create, update, post, reverse, delete → je `log_fibu_audit(..., "journal_entry", ...)` |
| **OP-Settle** | `app/api/v1/endpoints/open_items.py` | Nach INSERT Buchung + Zeilen → `log_fibu_audit("create", "journal_entry", journal_entry_id, ...)` |
| **Connector (Import)** | `app/core/connectors/workflow.py` | Pro erstellter Buchung im Lauf → `log_fibu_audit("create", "journal_entry", entry_id, ...)`; Storno analog für `rev_id` |
| **Buchungsvorlage anwenden** | `app/api/v1/endpoints/booking_templates.py` | Nach INSERT Buchung + Zeilen → `log_fibu_audit("create", "journal_entry", entry_id, ...)` |
| **Bulk-Import (CSV)** | `app/api/v1/endpoints/bulk_journal_import.py` | Pro erfolgreich importierter Buchung (wenn nicht dry_run) → `log_fibu_audit("create", "journal_entry", entry_id, ...)` |
| **Bankabgleich Auto-Buchung** | `app/api/v1/endpoints/bank_reconciliation.py` | Pro erstellter Buchung → `log_fibu_audit("create", "journal_entry", journal_entry_id, ...)` |
| **Lagergebühren** | `app/domains/inventory/api/storage_fees.py` | In `_post_storage_fee_to_ledger` nach Buchung + Zeilen → `log_fibu_audit("create", "journal_entry", entry_id, ...)` |
| **AP-Eingangsrechnung (GL)** | `app/api/v1/endpoints/ap_invoices.py` | Nach `entry_repo.create(...)` → `log_fibu_audit("create", "journal_entry", je_id, ...)` |

---

## Checkliste für neue Buchungspfade

- [ ] Buchung wird über **einen** der oben genannten Pfade oder einen **neu hinzugefügten** Pfad angelegt/geändert.
- [ ] Unmittelbar nach Anlegen/Ändern wird **`log_fibu_audit(db, tenant_id, action, "journal_entry", entry_id, changes, request=...)`** aufgerufen.
- [ ] `action` z. B. `"create"`, `"update"`, `"post"`, `"reverse"`; `changes` enthält z. B. `source`, `entry_number` oder andere relevante Metadaten.
- [ ] **Kein** direkter INSERT nur in `journal_entries`, ohne anschließenden Audit-Aufruf.

---

## Hash-Kette (GoBD)

Zusätzlich zur Nachvollziehbarkeit über `audit_logs` wird die **Hash-Kette** in `journal_entries` geführt (`hash_prev`, `hash_current`, `sequence_number`). Diese wird durch einen **DB-Trigger** beim INSERT befüllt (siehe Migration `gobd_journal_hash_chain_trigger_*`), so dass alle Buchungspfade automatisch in die Kette aufgenommen werden.

**Betriebsprüfungsfeste Prozessjournalisierung (Gap 010):** Die Tabelle `domain_shared.audit_logs` hat ebenfalls eine Hash-Kette (`prev_hash`, `hash`). Ein DB-Trigger befüllt diese beim INSERT automatisch – pro Tenant wird jeder Eintrag mit dem Hash des vorherigen verkettet. Migration: `add_audit_logs_hash_chain_20260306`.

---

## Siehe auch

- `app/core/fibu_audit.py` – Implementierung von `log_fibu_audit`
- `docs/GOBD-COMPLIANCE.md` – GoBD-Anforderungen und Zuordnung
- `app/finance/gobd.py` – Endpunkte Hash-Chain, Buchungslog, Nachvollziehbarkeit
