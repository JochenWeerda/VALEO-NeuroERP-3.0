# Journal-Entrées: Eine Tabelle für Liste + Connector

## Klärung (Stand 2026-03-01)

- **Bisher:** Connector schrieb in `domain_erp.journal_entries`, die Journal-Liste (ORM) nutzte `domain_erp.finance_journal_entries` → zwei getrennte Tabellen möglich, Referenz-Filter traf ggf. keine Connector-Buchungen.
- **Jetzt:** Es gibt nur noch **eine** fachliche Tabelle: `domain_erp.journal_entries` (Zeilen: `domain_erp.journal_entry_lines`).

## Änderungen

1. **ORM** (`app/infrastructure/models/__init__.py`)
   - `JournalEntry` → `__tablename__ = "journal_entries"` (vorher `finance_journal_entries`).
   - `JournalEntryLine` → `__tablename__ = "journal_entry_lines"` (vorher `finance_journal_entry_lines`).
   - FK Zeilen: `chart_of_accounts` (wie in 001), Storno: `journal_entries.id`.

2. **Connector** (`app/core/connectors/workflow.py`)
   - INSERT in `journal_entries` (unverändert) und `journal_entry_lines` mit Spalten **debit/credit** (nicht debit_amount/credit_amount), ohne tenant_id/updated_at auf Zeilen (entspricht 001).
   - Storno: Lese/Insert mit gleichen Spalten; `source = 'connector'`.

3. **Migration** `journal_entries_unify_20260301`
   - Falls nur `finance_journal_entries` existiert: Umbenennung zu `journal_entries` / `journal_entry_lines`, danach Spalten ergänzen.
   - Falls `journal_entries` schon existiert (z. B. aus 001): nur Spalten ergänzen.
   - Neue Spalten: `source` (optional, Default `'manual'`), `reversed_entry_id` (FK auf `journal_entries.id`).

4. **Weitere Stellen**
   - `gobd_archiv.py`, `chart_of_accounts.py`, `finance/router.py`, `finance/gobd.py`: Tabellenname auf `journal_entries` bzw. `journal_entry_lines` und Spalten `debit`/`credit` wo nötig umgestellt.
   - GoBD-Tests: Prüfung auf `journal_entries`.

## Nach der Migration

- Connector-Buchungen und manuelle Buchungen stehen in derselben Tabelle.
- Referenz-Filter im Buchungsjournal (run_id) trifft Connector-Importläufe.
- **Migration ausführen:** `alembic upgrade head`  
  Bei fehlgeschlagener vorheriger Ausführung ggf. einmal `alembic downgrade -1` und danach erneut `alembic upgrade head`.
