# GoBD Compliance Documentation

## Legal Foundation

This document maps VALEO NeuroERP FiBu (Financial Accounting) functions to German GoBD (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff) requirements.

### Official Sources

- **BMF GoBD**: [Bundesfinanzministerium - GoBD](https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2024-03-11-aenderung-gobd.html)
- **GoBD PDF**: [Finanzamt Bayern - GoBD Neufassung 28.11.2019](https://www.finanzamt.bayern.de/Informationen/download.php?url=Informationen%2FSteuerinfos%2FWeitere%2FThemen%2FAussenpruefung%2F2019-11-28-GoBD-1.pdf)

### Legal References

| Area | Law | Section | Description |
|------|-----|---------|-------------|
| Orderliness | AO | §146 | Complete, correct, timely, organized records |
| Retention | AO | §147 | Retention obligations + data access during audit |
| POS Systems | AO | §146a | Electronic recording systems (if applicable) |
| Bookkeeping | HGB | §238 | Bookkeeping obligation |
| Retention | HGB | §257 | Retention of documents |
| Invoices | UStG | §14b | Invoice retention |

---

## Requirements → System Functions Mapping

### 1. Nachvollziehbarkeit / Traceability (§146 AO)

| Requirement | VALEO NeuroERP Implementation |
|------------|------------------------------|
| Every transaction traceable to source document | Audit trail in `domain_shared.audit_logs` |
| User actions logged | `gobd.py` - Journal endpoint |
| Original document preservation | Document management (DMS) |
| Complete audit trail | Hash chain verification |

**Implemented in:**
- `app/finance/gobd.py` - `/gobd/journal` endpoint
- `app/api/v1/endpoints/audit.py` - Audit log queries

### 2. Unveränderbarkeit / Immutability (§146 AO, §147 AO)

| Requirement | VALEO NeuroERP Implementation |
|------------|------------------------------|
| No overwriting of original data | Storno (reversal) instead of delete |
| Hash chain for each entry | `hash_current`, `hash_prev` in journal entries |
| WORM storage for archives | Archive service integration |
| Change history | Audit logs with old/new values |

**Implemented in:**
- `app/finance/gobd.py` - `/gobd/hash-chain/verify` endpoint
- Hash fields in `domain_erp.finance_journal_entries`

### 3. Vollständigkeit / Completeness (§146 AO)

| Requirement | VALEO NeuroERP Implementation |
|------------|------------------------------|
| All documents numbered sequentially | `entry_number` with sequence |
| No gaps in numbering | Gap detection in `/gobd/belegnummern` |
| All transactions recorded | Period blocking (`finance_accounting_periods`) |
| Mandatory fields validation | Pydantic schemas |

**Implemented in:**
- `app/finance/gobd.py` - `/gobd/belegnummern` endpoint
- `app/api/v1/endpoints/accounting_periods.py` - Period control

### 4. Zeitnahme / Timeliness (§146 AO)

| Requirement | VALEO NeuroERP Implementation |
|------------|------------------------------|
| Same-day booking preferred | Real-time journal entry creation |
| Period closing controls | Accounting period status (OPEN/CLOSED) |
| Backdating prevention | Business day validation |

**Implemented in:**
- `app/api/v1/endpoints/journal_entries.py` - Period validation
- `app/api/v1/endpoints/accounting_periods.py` - Period management

### 5. Richtigkeit / Accuracy (§146 AO)

| Requirement | VALEO NeuroERP Implementation |
|------------|------------------------------|
| Balance verification (Soll/Haben) | Double-entry validation in journal entry creation |
| Automatic tax calculation | Tax keys integration |
| Account assignment validation | Chart of accounts checks |
| Foreign currency handling | Exchange rate integration |

**Implemented in:**
- `app/api/v1/endpoints/journal_entries.py` - Balance check
- `app/finance/router.py` - Exchange rates
- `app/api/v1/endpoints/tax_keys.py` - Tax keys

---

## FiBu Module Coverage

### Journal (Journalbuch)

| Feature | Status | GoBD Relevance |
|---------|--------|----------------|
| Create entries | ✅ Implemented | §146 - Complete records |
| Hash chain | ✅ Implemented | §147 - Immutable |
| Audit trail | ✅ Implemented | §146 - Traceable |
| Period control | ✅ Implemented | §146 - Timely |
| Balance validation | ✅ Implemented | §146 - Accurate |

### Open Items (Offene Posten)

| Feature | Status | GoBD Relevance |
|---------|--------|----------------|
| AR/AP management | ✅ Implemented | §146 - Complete |
| Payment matching | ✅ Implemented | §146 - Traceable |
| Dunning | ✅ Implemented | §146 - Documented |

### Invoices (Rechnungen)

| Feature | Status | GoBD Relevance |
|---------|--------|----------------|
| Invoice creation | ✅ Implemented | §14b UStG |
| VAT handling | ✅ Implemented | §14b UStG |
| Sequential numbering | ✅ Implemented | §146 - Ordered |
| Archive | ✅ Implemented | §147 - Retention |

---

## API Endpoints

### GoBD Compliance

| Endpoint | Description |
|----------|-------------|
| `GET /finance/gobd/status` | Overall GoBD compliance score |
| `GET /finance/gobd/journal` | Audit trail for journal entries |
| `POST /finance/gobd/hash-chain/verify` | Verify hash chain integrity |
| `GET /finance/gobd/belegnummern` | Check for gaps in document numbers |
| `GET /finance/gobd/nachvollziehbarkeit` | Traceability report |
| `GET /finance/gobd/verfahrensdokumentation` | Procedure documentation |

### Financial Core

| Endpoint | Description |
|----------|-------------|
| `GET /finance/journal-entries` | Journal entry list |
| `POST /finance/journal-entries` | Create journal entry |
| `GET /finance/periods` | Accounting periods |
| `GET /finance/accounts` | Chart of accounts |
| `GET /finance/open-items` | Open items |
| `GET /finance/wechselkurse` | Exchange rates |

---

## Testing

### GoBD Compliance Tests

```python
# Test hash chain integrity
# POST /finance/gobd/hash-chain/verify
# Expected: gueltig=True, fehlerhafte_buchungen=[]

# Test document number gaps
# GET /finance/gobd/belegnummern?jahr=2026
# Expected: status="ORDNUNGSGEMAESS"

# Test audit trail
# GET /finance/gobd/journal?von_datum=2026-01-01
# Expected: List of all changes with user attribution
```

---

## References

- BMF GoBD: https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2024-03-11-aenderung-gobd.html
- §146 AO: https://www.gesetze-im-internet.de/ao_1977/__146.html
- §147 AO: https://www.gesetze-im-internet.de/ao_1977/__147.html
- §146a AO: https://www.gesetze-im-internet.de/ao_1977/__146a.html
- §238 HGB: https://www.gesetze-im-internet.de/hgb/__238.html
- §257 HGB: https://www.gesetze-im-internet.de/hgb/__257.html
- §14b UStG: https://www.gesetze-im-internet.de/ustg_1980/__14b.html
