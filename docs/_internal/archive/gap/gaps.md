# GAP-Analyse FiBU - Identifizierte LÃ¼cken

**Datum:** 2025-11-24
**Basis:** FiBU Capability Model v1.0 + Finance Module Exploration
**Status:** Complete
**PrioritÃ¤t:** MUSS/SOLL/KANN basierend auf Lastenheft

## Zusammenfassung

**Gesamt:** 33 Capabilities analysiert
- **Yes (VollstÃ¤ndig):** 1 (3%)
- **Partial (Teilweise):** 15 (45%)
- **No (Fehlend):** 17 (52%)

**Nach PrioritÃ¤t:**
- **MUSS:** 15 Capabilities
  - Yes: 0
  - Partial: 7
  - No: 8
- **SOLL:** 13 Capabilities
  - Yes: 1
  - Partial: 5
  - No: 7
- **KANN:** 5 Capabilities
  - Yes: 0
  - Partial: 0
  - No: 5

## P0 - Kritisch (MUSS, PrioritÃ¤t 1)

### FIBU-AR-03: ZahlungseingÃ¤nge & Matching
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Payment-Match-UI gefunden, keine Bankimport-FunktionalitÃ¤t. OP-Status kann nicht korrekt verwaltet werden.
- **Impact:** Hohe - OP-Verwaltung nicht mÃ¶glich
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Payment-Match-UI + Bankimport implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Payment-Matching-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-AP-02: Eingangsrechnungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Eingangsrechnungen-Seite/API gefunden. Kreditoren kÃ¶nnen keine Rechnungen erfassen.
- **Impact:** Hohe - AP-Prozess nicht mÃ¶glich
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Eingangsrechnungen-Modul implementieren (Ã¤hnlich wie Ausgangsrechnungen)
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige AP-Invoice-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-GL-05: Periodensteuerung âœ…
- **Status:** Ja (Tabelle + API + UI)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Tabelle `finance_accounting_periods`, API `/finance/periods` (CRUD, close), Frontend `periods.tsx`, SperrprÃ¼fung in journal_entries/ap_invoices/bulk_journal_import.
- **Impact:** GoBD-Compliance
- **Evidence:** Migration add_audit_logs_and_accounting_periods_20260304, accounting_periods.py, periods.tsx
- **LÃ¶sung:** Umgesetzt
- **Owner:** Backend + Frontend

### FIBU-COMP-01: GoBD / Audit Trail âœ…
- **Status:** Ja (Tabelle + API + UI)
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** domain_shared.audit_logs, log_fibu_audit, API /audit/logs und /audit/stats, Frontend audit-trail.tsx (Filter, Export CSV).
- **Impact:** GoBD-Compliance
- **Evidence:** Migration add_audit_logs_and_accounting_periods_20260304, audit.py, audit-trail.tsx
- **LÃ¶sung:** Umgesetzt
- **Owner:** Frontend + Backend

---

## P1 - Hoch (MUSS, PrioritÃ¤t 2)

### FIBU-GL-01: Kontenplan & Kontenstamm
- **Status:** Partial (Hierarchie umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Kontenplan-Seite (chart-of-accounts.tsx) mit Tabellen- und **Hierarchie-Tab**. API GET `/api/v1/accounts/hierarchy` baut Baum aus `parent_account_id`; Fallback: Parent aus lÃ¤ngstem existierendem Kontonummern-PrÃ¤fix (z.â€¯B. 1400 â†’ 14 â†’ 1). TreeView zeigt Hierarchie; Sortierung nach Kontonummer.
- **Impact:** Mittel - FunktionalitÃ¤t vorhanden, aber unvollstÃ¤ndig
- **Evidence:** accounts.py (hierarchy), chart-of-accounts.tsx (Tab â€žHierarchieâ€œ, TreeView)
- **LÃ¶sung:** Hierarchie-API + Fallback und UI vorhanden; Reports mit Hierarchie-Summen optional
- **Vergleich:** Community ERP-Ã¤hnlich
- **Owner:** Frontend

### FIBU-GL-02: Belegprinzip & Nummernkreise
- **Status:** Partial (Storno-Dialog umgesetzt)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Nummernkreise in documents/router.py. **Storno:** POST `/api/v1/journal-entries/{id}/reverse`, StornoDialog (Grund min. 10 Zeichen); in Buchungserfassung und **Buchungsjournal** (Storno-Button pro Zeile) integriert. Belegprinzip dokumentieren bleibt optional.
- **Impact:** Mittel - FunktionalitÃ¤t teilweise vorhanden
- **Evidence:** journal_entries.py (reverse), StornoDialog.tsx, buchungserfassung.tsx, buchungsjournal.tsx
- **LÃ¶sung:** Storno-Dialog in Journal-Liste ergÃ¤nzt; Belegprinzip-Doku optional
- **Vergleich:** Basic
- **Owner:** Backend + Frontend

### FIBU-AR-01: Debitorenstamm
- **Status:** Partial (Stammdaten + Dublettencheck umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** **debitoren-stamm.tsx**: Stammdaten (Debitorennummer, Firma, Ansprechpartner), Adresse (StraÃŸe, PLZ, Ort, Land), Kontakt (Telefon, E-Mail), **USt-ID (vat_id)**, Steuernummer, Bankverbindung (IBAN inkl. Validierung + optional IBAN-Lookup), **Kreditlimit** und Konditionen (Zahlungsziel, Skonto). Zod-Pflichtfelder; Backend **Dublettencheck** bei Create (debtor_number pro Tenant). API `/api/v1/finance/debtors` CRUD; debitoren-liste.tsx mit Kreditlimit/Auslastung/Mahnstufe.
- **Impact:** Mittel - Stammdaten und Dublettencheck vorhanden
- **Evidence:** debitoren-stamm.tsx, debitoren-liste.tsx, debtors.py (duplicate check, address JSONB, USt-ID-Format), lib/utils/vat-validator.ts
- **LÃ¶sung:** Stammdaten, USt-ID, Kreditlimit und Dublettencheck implementiert; **USt-ID-Format-Validierung (EU)** in Frontend (vat-validator.ts, Debitoren-/Kreditoren-Stamm) und Backend (debtors.py) umgesetzt.
- **Vergleich:** Basic+
- **Owner:** Frontend + Backend

### FIBU-AR-02: Ausgangsrechnungen
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Invoices-Liste und Create Invoice vorhanden; `finance_invoices.py` erzeugt bei Status != `ENTWURF` jetzt GL-Buchung in `domain_erp.journal_entries` + `journal_entry_lines` sowie Debitoren-OP in `offene_posten` (idempotent, PeriodenprÃ¼fung aktiv).
- **Impact:** Mittel - Kernintegration vorhanden, weitere fachliche Vertiefung (z. B. Kontierungsregeln/Freigabeprozesse) offen
- **Evidence:** Screenshots: 20251124_095105_04_invoices_list.png, 20251124_095108_05_create_invoice_form.png; Backend: `app/api/v1/endpoints/finance_invoices.py`
- **LÃ¶sung:** NÃ¤chster Schritt: Kontierungs-/SteuerschlÃ¼ssel-Mapping und engere Abstimmung mit Zahlungsabgleich
- **Vergleich:** Community ERP-Ã¤hnlich
- **Owner:** Backend

### FIBU-AR-05: OP-Verwaltung & Ausgleich
- **Status:** Partial (Ausgleich + Audit-Trail vorhanden)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** op-debitoren.tsx mit OP-Liste; Backend: Einzelausgleich POST `/{op_id}/settle`, Sammelausgleich (FIBU-AP-05) fÃ¼r Kreditoren. **Audit-Trail:** `log_fibu_audit` bei settle/reverse, optional `infrastructure.audit_log`, GET `/{op_id}/settlements` liefert Ausgleichshistorie. Storno: POST `/{op_id}/reverse-settlement`.
- **Impact:** Mittel - Kernfunktion und Audit vorhanden, UI-Tiefe ausbaubar
- **Evidence:** open_items.py (settle, reverse_settlement, get_settlements, log_fibu_audit), op-debitoren.tsx (Tab Ausgleichshistorie)
- **LÃ¶sung:** Ausgleich und Audit-Trail implementiert; **OP Debitoren** zeigt Ausgleichshistorie (Tab â€žAusgleichshistorieâ€œ, GET `/{op_id}/settlements`) in op-debitoren.tsx.
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-AP-01: Kreditorenstamm
- **Status:** Partial (API + IBAN + USt-ID + Dublettencheck)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** **API** `/api/v1/finance/creditors` (CRUD): Create mit **Dublettencheck** (creditor_number pro Tenant), USt-ID- und IBAN-Format-Validierung. Frontend **kreditoren-stamm.tsx**: Stammdaten, IBAN (validateIBAN, useIbanLookup), USt-ID (validateVatIdFormat); **toApiCreditor/fromApiCreditor** mappen Formular â†” API. Stammdaten-Felder und Dublettencheck umgesetzt.
- **Impact:** Mittel - API und Validierung vorhanden
- **Evidence:** creditors.py, kreditoren-stamm.tsx, lib/utils/iban-validator.ts, lib/utils/vat-validator.ts
- **LÃ¶sung:** Kreditoren-API mit CRUD + Dublettencheck; Frontend-Mapping und Validierung implementiert
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-AP-05: OP-Verwaltung & Ausgleich
- **Status:** Partial (Sammelausgleich umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** OP-Kreditoren-Maske mit Liste, Summen, Suche, CRUD und Einzelausgleich; **Sammelausgleich**: POST `/api/v1/finance/open-items/batch-settle`, UI Mehrfachauswahl + Dialog â€žAlle ausgleichenâ€œ. Offen: Zahlungsfreigaben, OP-Import/Abstimmung.
- **Impact:** Mittel - Kernfunktion vorhanden, fachliche Tiefe ausbaufÃ¤hig
- **Evidence:** open_items.py (batch-settle), op-kreditoren.tsx (Checkboxen, Sammelausgleich-Button/Dialog)
- **LÃ¶sung:** Sammelausgleich umgesetzt; weitere Workflow-Erweiterung optional
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-BNK-01: Bankkontenstamm
- **Status:** Partial (API + UI + IBAN-Validierung)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** API `/api/v1/finance/bank-accounts` (List, Get, Create, Update). Beim Anlegen wird bei Bedarf ein Kontenplan-Eintrag (Gegenkonto) angelegt. UI `bank-stamm.tsx`: Liste, Anlegen, Bearbeiten (Kontonummer, Bankname, IBAN, BIC, WÃ¤hrung, Aktiv). **IBAN:** Frontend prÃ¼ft vor Submit (validateIBAN, formatIBAN); Backend `_validate_iban` (Mod-97) bei Create/Update. Nav: â€žBankkonten (Bankstamm)â€œ.
- **Impact:** Mittel - Schema, UI und IBAN-Validierung vorhanden
- **Evidence:** bank_accounts.py (_validate_iban), bank-stamm.tsx (validateIBAN, formatIBAN), Nav â€žBankkonten (Bankstamm)â€œ
- **LÃ¶sung:** Umgesetzt inkl. IBAN-Validierung (Frontend + Backend)
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-02: Kontoauszugsimport
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Import fÃ¼r CAMT/MT940/CSV vorhanden (`bank_statement_import.py`) inkl. RÃ¼ckgabe `import_errors`; UI `bank-abgleich.tsx` zeigt Import-Protokoll/Zeilenfehler jetzt explizit an.
- **Impact:** Mittel - Formate und Fehlertransparenz vorhanden, weitere Parser-Robustheit bleibt ausbaubar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/bank_statement_import.py`; Frontend: `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
- **LÃ¶sung:** NÃ¤chster Schritt: Parser-Validierung je Bankprofil und strukturierte Fehlercodes
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-04: Bankabstimmung
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `bank_reconciliation.py` liefert Saldovergleich, Differenzliste, BuchungsvorschlÃ¤ge und `line_counts`; Auto-Book schreibt Journal + markiert Statement-Lines als `MATCHED`. Frontend `bank-abgleich.tsx` kann Reconcile-Daten inkl. `line_counts` jetzt korrekt verwerten.
- **Impact:** Mittel - Kernabstimmung nutzbar, weitere Tiefe (Regelwerk, Bulk-Workflow, bessere GegenkontovorschlÃ¤ge) offen
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/bank_reconciliation.py`
- **LÃ¶sung:** NÃ¤chster Schritt: Matching-Regeln ausbauen und manuelle Differenzbuchungen als Workflow-Maske ergÃ¤nzen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-TAX-01: SteuerschlÃ¼ssel-System
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Tax-Keys API mit CRUD, LÃ¤nderfilter und zusÃ¤tzlicher Validierung (ISO-Landcode, GÃ¼ltigkeitszeitraum, Reverse-Charge nur bei 0%) aktiv. UI `steuerschluessel.tsx` zeigt Steuerart/Reverse-Charge transparent und erlaubt Neuanlage inkl. Intracom/Export/Reverse-Charge. AR/AP-Posting nutzt nun zentralen Tax-Resolver (`app/finance/tax_resolver.py`) mit Country-/EU-/Export-Kontext und Fallback auf DE.
- **Impact:** Mittel - Stammdatenpflege belastbarer, tiefe Steuerlogik (z. B. automatische Kontierung je Belegkontext) bleibt ausbaubar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/tax_keys.py`; Frontend: `packages/frontend-web/src/pages/finance/steuerschluessel.tsx`
- **LÃ¶sung:** Steuerfindung in AR/AP-Buchungsfluss je Land/Steuerart angebunden; nÃ¤chster Schritt: tieferes Mapping je Beleg-/Steuerart (inkl. OSS/ZM)
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-CLS-02: Nebenbuch-Abstimmung
- **Status:** Partial (AR/AP/Bank umgesetzt, FA nicht in Scope)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API `/api/v1/finance/subsidiary-ledger-reconciliation` fachlich korrigiert (reales Schema fÃ¼r Journal/OP) mit Endpunkten fÃ¼r AR/AP/Bank, summary, details und CSV-Export je Ledger/Periode. UI `nebenbuch-abstimmung.tsx`: Perioden-/Ledger-Filter, Saldenvergleich, Drilldown und Export-Button.
- **Impact:** Mittel - Erforderlich fÃ¼r Abschluss
- **Evidence:** `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py`, `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx`, Nav â€žNebenbuch-Abstimmungâ€œ
- **LÃ¶sung:** Umgesetzt fÃ¼r AR/AP/Bank inkl. Export; FA bei Bedarf spÃ¤ter
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Nebenbuch-Abstimmung
- **Owner:** Backend + Frontend

### FIBU-REP-01: Standardreports
- **Status:** Partial (Bilanz/GuV/BWA + Landingpage)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** API `/api/v1/finance/financial-reports`: balance-sheet, profit-loss, bwa, **export/{report_type}?format=pdf|excel|json**. Export liefert PDF (reportlab) oder Excel (openpyxl) als Download; JSON unverÃ¤ndert. Frontend: fibu/bilanz, fibu/guv, fibu/bwa; **finance/reports.tsx** als Landingpage.
- **Impact:** Mittel - Dashboard und Report-Export (PDF/Excel) nutzbar
- **Evidence:** financial_reports.py (export_report, _report_to_rows), finance/reports.tsx
- **LÃ¶sung:** PDF- und Excel-Export fÃ¼r Bilanz/GuV/BWA umgesetzt
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

---

## P2 - Mittel (SOLL, PrioritÃ¤t 3)

### FIBU-GL-04: Sammel-/Massenbuchungen
- **Status:** Partial (CSV-Import + Fehler pro Zeile)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API POST `/api/v1/bulk-journal-import/csv` mit Dry-Run und Import; RÃ¼ckgabe `ImportResult` inkl. `errors[]` (row_number, field, error_message, row_data). Frontend **buchungsimport.tsx**: 3 Schritte (Datei wÃ¤hlen â†’ Vorschau â†’ Ergebnis), Fehlertabelle pro Zeile in Vorschau und Ergebnis. Excel/API-Stapel optional.
- **Impact:** Niedrig - CSV-Import nutzbar, Excel/API ausbaubar
- **Evidence:** bulk_journal_import.py (ImportError, ImportResult), buchungsimport.tsx, Nav/Schnittstellen-Center â€žBuchungsimportâ€œ
- **LÃ¶sung:** CSV-Import-Screen und Fehler pro Zeile umgesetzt; Excel/weitere Formate optional
- **Vergleich:** Basic
- **Owner:** Backend + Frontend

### FIBU-AR-04: Mahnwesen / Dunning
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** mahnwesen.tsx und dunning-editor.tsx vorhanden, aber Mahnstufen/GebÃ¼hren/Sperrlogik unklar. Mahnstufen laufen mÃ¶glicherweise nicht regelbasiert.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **LÃ¶sung:** Mahnstufen/GebÃ¼hren/Sperrlogik prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-AP-03: PrÃ¼f-/Freigabeworkflow
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Workflow-Setup/UI gefunden. 2/3/4-Augen je Betrag/Warengruppe nicht mÃ¶glich. Ohne Freigabe kein Zahlungsstatus â€žfreigegeben".
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Workflow-Setup + UI implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Workflow-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-AP-04: ZahlungslÃ¤ufe / SEPA
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** zahlungslauf-kreditoren.tsx vorhanden, aber SEPA XML Export/Status/RÃ¼cklÃ¤ufer unklar. Lauf erzeugt mÃ¶glicherweise keinen OP-Ausgleich bei Erfolg.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **LÃ¶sung:** SEPA XML Export implementieren, Status/RÃ¼cklÃ¤ufer prÃ¼fen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-03: Automatisches Matching
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Match-UI/regelbasiertes Matching gefunden. Regelbasiertes OP-Matching nicht mÃ¶glich. Trefferquote nicht nachvollziehbar, manuell nicht Ã¼bersteuerbar.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Match-UI + regelbasiertes Matching implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Matching-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-TAX-02: USt-Voranmeldung / ZM / OSS
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** ustva.tsx vorhanden, aber Export BehÃ¶rdenformat (ELSTER) unklar. Summen stimmen mÃ¶glicherweise nicht mit GL Ã¼berein.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **LÃ¶sung:** Export BehÃ¶rdenformat (ELSTER) implementieren, Summen-Validierung prÃ¼fen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-CLS-01: Abschlusschecklisten
- **Status:** Partial (API + Cockpit-UI)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API `/api/v1/finance/closing-checklists`: Templates, CRUD, cockpit/summary, GET `/{checklist_id}`, POST `/{checklist_id}/items/{item_code}/complete`. Frontend **abschluss-cockpit.tsx**: Ãœbersicht, Link â€žDetailsâ€œ pro Checkliste. **abschluss-checklist-detail.tsx**: Detail-UI mit Aufgabenliste und â€žErledigenâ€œ-Button pro Aufgabe.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** closing_checklists.py, abschluss-cockpit.tsx, abschluss-checklist-detail.tsx, Route fibu/abschluss-checklist-detail/:id
- **LÃ¶sung:** API + Cockpit + Detail-UI mit Aufgaben-Erledigen umgesetzt
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Checklist-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-CLS-03: Abgrenzungen / RÃ¼ckstellungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Accruals-Flow gefunden. Periodisierung/Wiederkehrbuchungen nicht mÃ¶glich. Automatischer Lauf nicht mÃ¶glich.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Accruals-Flow implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Accruals-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-REP-02: Drilldown & Analyse
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Drilldown-Trace gefunden. Bericht â†’ Konto â†’ Beleg â†’ Position â†’ Ursprung nicht mÃ¶glich. 3-Klick-Regel bis Beleg nicht erfÃ¼llt.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Drilldown-FunktionalitÃ¤t implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Drilldown-FunktionalitÃ¤t
- **Owner:** Frontend + Backend

---

## P3 - Niedrig (SOLL, PrioritÃ¤t 3-4)

### FIBU-GL-06: FremdwÃ¤hrung & Wechselkurse
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine WÃ¤hrungssetup/FX-Buchung gefunden. Kursarten (ECB, manuell, Vertragskurs) nicht verfÃ¼gbar. Kursdifferenzen werden nicht automatisch gebucht.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** WÃ¤hrungssetup + FX-Buchung implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige FX-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-GL-07: Automatische Buchungsschemata
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Schema-Setup/Auto-Post gefunden. Steuerbuchungen/Skonto/Rundungen/Umlagen nicht automatisch. Regelbasierte Kontierung nicht mÃ¶glich.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Schema-Setup + Auto-Post implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Schema-FunktionalitÃ¤t
- **Owner:** Backend

### FIBU-TAX-03: E-Rechnung (ZUGFeRD/XRechnung)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine E-Invoice-UI/Import/Export gefunden. Import/Export/Validierung nicht mÃ¶glich. Validierungsfehler werden nicht angezeigt.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** E-Invoice-UI + Import/Export implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige E-Invoice-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

---

## P4 - Optional (KANN, PrioritÃ¤t 4-5)

### FIBU-GL-08: Kostenrechnung-Integrationspunkte
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Dimensionen (Kostenstellen/KostentrÃ¤ger) gefunden. Kontierung mit Dimension nicht mÃ¶glich. Dimensionen sind nicht filter-/summierbar.
- **Impact:** Sehr niedrig - Optional
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Dimensionen (Kostenstellen/KostentrÃ¤ger) implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige CO-Integration
- **Owner:** Backend + Frontend

### FIBU-FA-01 bis FIBU-FA-05: Anlagenbuchhaltung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Alle FA-FunktionalitÃ¤ten fehlen (Anlageklassen, ZugÃ¤nge, Abschreibungslauf, AbgÃ¤nge, Anlagenspiegel).
- **Impact:** Sehr niedrig - Optional (nur falls Anlagen in Scope)
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Komplettes FA-Modul implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige FA-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

### FIBU-IC-01 bis FIBU-IC-02: Intercompany
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Alle IC-FunktionalitÃ¤ten fehlen (IC-Partner, Konten, Verrechnung, Eliminierung).
- **Impact:** Sehr niedrig - Optional (je Scope)
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Komplettes IC-Modul implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige IC-FunktionalitÃ¤t
- **Owner:** Backend + Frontend

---

## Zusammenfassung nach LÃ¶sungstyp

### Typ A (Konfig/Verdrahtung): 0 GAPs
- Keine reinen Konfigurations-GAPs identifiziert

### Typ B (Integration/Adapter): 1 GAP
- FIBU-AR-02: Ausgangsrechnungen (GL-Buchung/OP-Erzeugung)

### Typ C (Neues Feature/Modul): 21 GAPs
- Die meisten fehlenden Features erfordern neue Module

### Typ D (UX/Edge-Case/Reifegrad): 10 GAPs
- Viele vorhandene Seiten benÃ¶tigen FunktionalitÃ¤ts-Erweiterungen

## NÃ¤chste Schritte

1. **P0-Status: abgeschlossen (PrioritÃ¤t 1):**
   - FIBU-AR-03: ZahlungseingÃ¤nge & Matching âœ…
   - FIBU-AP-02: Eingangsrechnungen âœ…
   - FIBU-GL-05: Periodensteuerung âœ…
   - FIBU-COMP-01: GoBD / Audit Trail âœ…

2. **P1-GAPs beheben (PrioritÃ¤t 2):**
   - Alle Partial-Status GAPs prÃ¼fen und vervollstÃ¤ndigen
   - FIBU-AP-05: OP-Verwaltung & Ausgleich (Kreditoren)
   - FIBU-CLS-02: Nebenbuch-Abstimmung (AR/AP/Bank + Drilldown umgesetzt; FA optional)

3. **P2-GAPs beheben (PrioritÃ¤t 3):**
   - SOLL-Features nach Bedarf implementieren

4. **P3/P4-GAPs (Optional):**
   - Nach Bedarf und Ressourcen

## Referenzen

- FiBU Capability Model: User-Query (Lastenheft)
- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- JSON Summary: `evidence/screenshots/finance/finance_mission_2025-11-24T08-51-19.344194.json`
- Screenshots: `evidence/screenshots/finance/`
- Matrix: `gap/matrix.csv`


