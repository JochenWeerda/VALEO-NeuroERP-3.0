# Phase 2 Completion Report — Finance P1 + CRM P0/P1

**Datum:** 2026-03-05
**Referenz:** `.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md`
**Maturity-Fortschritt:** ~50% → ~65%

---

## 1. Finance P1 (12 Capabilities)

### 1.1 FIBU-GL-01 — Kontenplan Hierarchie

**Status:** Bereits vollständig implementiert.

- **ORM-Modell:** `Account` mit `parent_account_id` (Self-FK) in `app/infrastructure/models/__init__.py`
- **Hierarchie-Endpoint:** `GET /accounts/hierarchy` in `app/api/v1/endpoints/accounts.py`
  - Baut Baum aus `parent_account_id`
  - Fallback: Longest-Prefix-Match auf `account_number` (z. B. 1400 → 140 → 14 → 1)
  - Sortierung nach Kontonummer
- **Frontend:** `finance/kontenplan.tsx`, `fibu/kontenplan.tsx`, `finance/chart-of-accounts.tsx`

### 1.2 FIBU-GL-02 — Belegprinzip und Nummernkreise

**Status:** Ergänzt.

**Vorher:**
- `NumberingServicePG` mit `next_number()`, `peek()`, `reset()` (thread-safe via `FOR UPDATE`)
- Router: `/api/numbering/next`, `/status`, `/reset`, `/init-year`

**Neu implementiert:**
- **Belegpflicht-Validierung:** Journal Entries erfordern jetzt zwingend ein `reference`-Feld (`app/api/v1/endpoints/journal_entries.py`)
- **Nummernkreis-CRUD:**
  - `GET /api/numbering/series` — Alle Nummernkreise eines Mandanten auflisten
  - `POST /api/numbering/series` — Nummernkreis anlegen oder Prefix/Width ändern
  - Schema: `NumberSeriesConfig`, `NumberSeriesListItem` in `app/routers/numbering_router.py`

### 1.3 FIBU-AR-01 — Debitorenstamm

**Status:** Ergänzt.

**Vorher:** Vollständiger CRUD (`app/api/v1/endpoints/debtors.py`) mit USt-ID-Validierung (9 EU-Länder).

**Neu implementiert:**
- **company_name-Update:** `PUT /debtors/{id}` aktualisiert jetzt auch den Firmennamen
- **OP-Saldo-Endpoint:** `GET /debtors/{id}/balance` — Offener Saldo, Anzahl OPs, ältestes Fälligkeitsdatum

### 1.4 FIBU-AP-01 — Kreditorenstamm + IBAN-Validierung

**Status:** Ergänzt.

**Vorher:** Vollständiger CRUD (`app/api/v1/endpoints/creditors.py`) mit USt-ID- und IBAN-Mod97-Validierung.

**Neu implementiert:**
- **company_name-Update:** `PUT /creditors/{id}` aktualisiert jetzt auch den Firmennamen
- **OP-Saldo-Endpoint:** `GET /creditors/{id}/balance` — Offener Saldo, Anzahl OPs, ältestes Fälligkeitsdatum

### 1.5 FIBU-AR-02 — Ausgangsrechnungen GL-Buchung/OP

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/finance_invoices.py`.

- `_create_gl_booking_and_op()` erzeugt:
  - GL-Buchung (JournalEntry) mit Debit-Forderung/Credit-Umsatz/Credit-USt
  - Offenen Posten mit Fälligkeitsdatum
  - Periodenprüfung (gesperrte Perioden blockiert)
  - GoBD Audit-Trail + SHA256-Artifact
- Tax-Resolver: Reverse-Charge, Länderzuordnung, Kontenfindung

### 1.6 FIBU-AR-05 + AP-05 — OP-Verwaltung beidseitig

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/open_items.py`.

- CRUD für Debitoren- und Kreditoren-OPs
- Ausgleich (Settlement) mit GL-Buchung
- Sammelausgleich (Batch-Settlement)
- Storno (Reversal) mit GoBD-Pflichtbegründung (min. 10 Zeichen)
- Statusmaschine: offen → teilweise → geschlossen (nur offen/teilweise editierbar)
- Mahnstufen, Skonto, Kreditlimit, Sperrgründe, Valuta

### 1.7 FIBU-BNK-01 — Bankstamm-UI

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/bank_accounts.py`.

- CRUD für Bankkonten mit IBAN-Mod97-Validierung
- Kontenplan-Verknüpfung (Gegenkonto)
- Frontend: `finance/bankkonten-stamm.tsx`, `finance/bank-stamm.tsx`

### 1.8 FIBU-BNK-02 — Kontoauszugsimport (CAMT/MT940/CSV)

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/bank_statement_import.py`.

- Multi-Format-Parser: CAMT.053/052, MT940, CSV
- Automatisches Statement-Line-Matching
- Import-Ergebnis mit Fehlerprotokoll

### 1.9 FIBU-BNK-04 — Bankabstimmung Saldoabgleich

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/bank_reconciliation.py`.

- Saldovergleich Bank vs. Buchhaltung
- Differenz-Analyse (UNMATCHED_STATEMENT, UNMATCHED_ACCOUNTING, AMOUNT_MISMATCH)
- Auto-Reconciliation mit konfigurierbaren Matching-Regeln
- Suggested-Actions pro Differenzposten

### 1.10 FIBU-TAX-01 — Steuerschlüssel-System

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/tax_keys.py`.

- CRUD für Steuerschlüssel mit Multi-Country-Support
- Felder: code, Steuersatz, UStVA-Position, Intracom/Export/Reverse-Charge
- Gültigkeitszeiträume, Debit/Credit-Konten
- Frontend: `finance/steuerschluessel.tsx`

### 1.11 FIBU-CLS-02 — Nebenbuch-Abstimmung

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py`.

- Abgleich Debitoren/Kreditoren-Nebenbuch vs. Hauptbuch
- Drilldown auf Einzelposten
- CSV-Export der Abstimmungsergebnisse
- Frontend: `finance/nebenbuch-abstimmung.tsx`

### 1.12 FIBU-REP-01 — Standardreports (Bilanz/GuV/BWA)

**Status:** Bereits vollständig implementiert in `app/api/v1/endpoints/financial_reports.py`.

- Bilanz (Balance Sheet), GuV (Profit & Loss), BWA
- Periodenselektion und Vergleich
- CSV/Excel-Export
- Frontend: `finance/reports.tsx` mit Sub-Komponenten

---

## 2. CRM P0/P1 (4 Capabilities)

### 2.1 CRM-OPP-01 — Opportunities / Sales Pipeline (Kanban)

**Status:** Neu implementiert.

**Backend** (`app/crm/router.py`):
- `GET /crm/opportunities/stages` — Pipeline-Stage-Definitionen (9 Stages: Akquise → Gewonnen/Verloren)
- `POST /crm/opportunities` — Opportunity erstellen (Auto-Probability aus Stage)
- `GET /crm/opportunities` — Liste mit Filter (stage, assigned_to)
- `GET /crm/opportunities/{id}` — Einzelabruf
- `PUT /crm/opportunities/{id}` — Update mit Stage-Transition + Auto-Probability
- `DELETE /crm/opportunities/{id}` — Soft-Delete
- `GET /crm/opportunities/pipeline/summary` — Pipeline-Übersicht (Count, Value, Weighted Value pro Stage)

**ORM-Modell:** `Opportunity` in `app/domains/crm/models.py` (Schema: `domain_crm.crm_opportunities`)

**Schemas** (`app/crm/schemas.py`):
- `OpportunityStage` (Enum mit 9 Stages)
- `STAGE_PROBABILITY` (Mapping Stage → Default-Wahrscheinlichkeit)
- `OpportunityCreate`, `OpportunityUpdate`, `Opportunity`, `PipelineStageInfo`

**Frontend:** `opportunities-kanban.tsx` (Drag-and-Drop Kanban), `opportunities-liste.tsx`, `opportunity-detail.tsx`, `opportunities-forecast.tsx`

### 2.2 CRM-CNS-01 — Opt-in/Opt-out und Consent Log

**Status:** Neu implementiert.

**Backend** (`app/crm/router.py`):
- `POST /crm/consents` — Einwilligung erfassen (DSGVO Art. 6/7)
- `GET /crm/consents` — Liste mit Filter (partner_id, channel)
- `POST /crm/consents/{id}/revoke` — Einwilligung widerrufen (Opt-out)

**DB-Tabelle:** `domain_crm.crm_consents` (Felder: partner_id, channel, purpose, granted, source, ip_address, granted_at, revoked_at)

**Schemas:** `ConsentChannel` (Enum: email, phone, sms, post, all), `ConsentCreate`, `ConsentResponse`

### 2.3 CRM-CNS-02 — DSGVO-Funktionen (Auskunft/Löschung)

**Status:** Neu implementiert.

**Backend** (`app/crm/router.py`):
- `GET /crm/gdpr/data-export/{partner_id}` — **DSGVO Art. 15 Auskunftsrecht:** Exportiert alle Daten eines Partners (Business-Partner, Consents, Activities, Offene Posten)
- `POST /crm/gdpr/anonymize/{partner_id}` — **DSGVO Art. 17 Recht auf Löschung:** Anonymisiert Partnerdaten, widerruft alle Consents, protokolliert Begründung

### 2.4 MKT-SEG-01 — Segmente und Zielgruppen

**Status:** Neu implementiert.

**Backend** (`app/crm/router.py`):
- `POST /crm/segments` — Segment erstellen (Name, Beschreibung, Kriterien, Typ)
- `GET /crm/segments` — Liste aller Segmente
- `GET /crm/segments/{id}` — Einzelabruf
- `PUT /crm/segments/{id}` — Update
- `DELETE /crm/segments/{id}` — Löschen
- `POST /crm/segments/{id}/members` — Mitglied hinzufügen (Upsert)
- `GET /crm/segments/{id}/members` — Mitglieder auflisten

**DB-Tabellen:** `domain_crm.crm_segments`, `domain_crm.crm_segment_members`

**Frontend:** `segments.tsx`, `segment-detail.tsx` (mit Members- und Performance-Tabs)

---

## 3. Migration

Neue Alembic-Migration: `alembic/versions/crm_consent_segments_20260305.py`

Erstellt:
- `domain_crm.crm_consents` — Consent-Log
- `domain_crm.crm_segments` — Segmente
- `domain_crm.crm_segment_members` — Segment-Mitglieder
- `domain_crm.crm_opportunities` — Opportunities

Alle mit `CREATE TABLE IF NOT EXISTS` und `CREATE SCHEMA IF NOT EXISTS domain_crm`.

---

## 4. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `app/crm/router.py` | +250 Zeilen: Opportunities, Consent, GDPR, Segments Endpoints |
| `app/crm/schemas.py` | +150 Zeilen: Opportunity, Consent, Segment Schemas |
| `app/api/v1/endpoints/journal_entries.py` | Belegpflicht-Validierung (reference-Pflichtfeld) |
| `app/api/v1/endpoints/debtors.py` | company_name-Update + `GET /{id}/balance` |
| `app/api/v1/endpoints/creditors.py` | company_name-Update + `GET /{id}/balance` |
| `app/routers/numbering_router.py` | Nummernkreis-CRUD (`GET/POST /series`) |
| `alembic/versions/crm_consent_segments_20260305.py` | **NEU** — CRM-Tabellen-Migration |

---

## 5. Nächste Schritte

→ **Phase 3: Sales Domain komplett** (31 Capabilities, Wochen 31–42)
