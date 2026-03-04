# GAP-Analyse FiBU - Identifizierte Lücken

**Datum:** 2025-11-24  
**Basis:** FiBU Capability Model v1.0 + Finance Module Exploration  
**Status:** Complete  
**Priorität:** MUSS/SOLL/KANN basierend auf Lastenheft

## Zusammenfassung

**Gesamt:** 33 Capabilities analysiert
- **Yes (Vollständig):** 1 (3%)
- **Partial (Teilweise):** 15 (45%)
- **No (Fehlend):** 17 (52%)

**Nach Priorität:**
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

## P0 - Kritisch (MUSS, Priorität 1)

### FIBU-AR-03: Zahlungseingänge & Matching
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Payment-Match-UI gefunden, keine Bankimport-Funktionalität. OP-Status kann nicht korrekt verwaltet werden.
- **Impact:** Hohe - OP-Verwaltung nicht möglich
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Payment-Match-UI + Bankimport implementieren
- **Vergleich:** SAP/Odoo haben vollständige Payment-Matching-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-AP-02: Eingangsrechnungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Eingangsrechnungen-Seite/API gefunden. Kreditoren können keine Rechnungen erfassen.
- **Impact:** Hohe - AP-Prozess nicht möglich
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Eingangsrechnungen-Modul implementieren (ähnlich wie Ausgangsrechnungen)
- **Vergleich:** SAP/Odoo haben vollständige AP-Invoice-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-GL-05: Periodensteuerung ✅
- **Status:** Ja (Tabelle + API + UI)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Tabelle `finance_accounting_periods`, API `/finance/periods` (CRUD, close), Frontend `periods.tsx`, Sperrprüfung in journal_entries/ap_invoices/bulk_journal_import.
- **Impact:** GoBD-Compliance
- **Evidence:** Migration add_audit_logs_and_accounting_periods_20260304, accounting_periods.py, periods.tsx
- **Lösung:** Umgesetzt
- **Owner:** Backend + Frontend

### FIBU-COMP-01: GoBD / Audit Trail ✅
- **Status:** Ja (Tabelle + API + UI)
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** domain_shared.audit_logs, log_fibu_audit, API /audit/logs und /audit/stats, Frontend audit-trail.tsx (Filter, Export CSV).
- **Impact:** GoBD-Compliance
- **Evidence:** Migration add_audit_logs_and_accounting_periods_20260304, audit.py, audit-trail.tsx
- **Lösung:** Umgesetzt
- **Owner:** Frontend + Backend

---

## P1 - Hoch (MUSS, Priorität 2)

### FIBU-GL-01: Kontenplan & Kontenstamm
- **Status:** Partial (Hierarchie umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Kontenplan-Seite (chart-of-accounts.tsx) mit Tabellen- und **Hierarchie-Tab**. API GET `/api/v1/accounts/hierarchy` baut Baum aus `parent_account_id`; Fallback: Parent aus längstem existierendem Kontonummern-Präfix (z. B. 1400 → 14 → 1). TreeView zeigt Hierarchie; Sortierung nach Kontonummer.
- **Impact:** Mittel - Funktionalität vorhanden, aber unvollständig
- **Evidence:** accounts.py (hierarchy), chart-of-accounts.tsx (Tab „Hierarchie“, TreeView)
- **Lösung:** Hierarchie-API + Fallback und UI vorhanden; Reports mit Hierarchie-Summen optional
- **Vergleich:** Odoo-ähnlich
- **Owner:** Frontend

### FIBU-GL-02: Belegprinzip & Nummernkreise
- **Status:** Partial (Storno-Dialog umgesetzt)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Nummernkreise in documents/router.py. **Storno:** POST `/api/v1/journal-entries/{id}/reverse`, StornoDialog (Grund min. 10 Zeichen); in Buchungserfassung und **Buchungsjournal** (Storno-Button pro Zeile) integriert. Belegprinzip dokumentieren bleibt optional.
- **Impact:** Mittel - Funktionalität teilweise vorhanden
- **Evidence:** journal_entries.py (reverse), StornoDialog.tsx, buchungserfassung.tsx, buchungsjournal.tsx
- **Lösung:** Storno-Dialog in Journal-Liste ergänzt; Belegprinzip-Doku optional
- **Vergleich:** Basic
- **Owner:** Backend + Frontend

### FIBU-AR-01: Debitorenstamm
- **Status:** Partial (Stammdaten + Dublettencheck umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** **debitoren-stamm.tsx**: Stammdaten (Debitorennummer, Firma, Ansprechpartner), Adresse (Straße, PLZ, Ort, Land), Kontakt (Telefon, E-Mail), **USt-ID (vat_id)**, Steuernummer, Bankverbindung (IBAN inkl. Validierung + optional IBAN-Lookup), **Kreditlimit** und Konditionen (Zahlungsziel, Skonto). Zod-Pflichtfelder; Backend **Dublettencheck** bei Create (debtor_number pro Tenant). API `/api/v1/finance/debtors` CRUD; debitoren-liste.tsx mit Kreditlimit/Auslastung/Mahnstufe.
- **Impact:** Mittel - Stammdaten und Dublettencheck vorhanden
- **Evidence:** debitoren-stamm.tsx, debitoren-liste.tsx, debtors.py (duplicate check, address JSONB, USt-ID-Format), lib/utils/vat-validator.ts
- **Lösung:** Stammdaten, USt-ID, Kreditlimit und Dublettencheck implementiert; **USt-ID-Format-Validierung (EU)** in Frontend (vat-validator.ts, Debitoren-/Kreditoren-Stamm) und Backend (debtors.py) umgesetzt.
- **Vergleich:** Basic+
- **Owner:** Frontend + Backend

### FIBU-AR-02: Ausgangsrechnungen
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Invoices-Liste und Create Invoice vorhanden; `finance_invoices.py` erzeugt bei Status != `ENTWURF` jetzt GL-Buchung in `domain_erp.journal_entries` + `journal_entry_lines` sowie Debitoren-OP in `offene_posten` (idempotent, Periodenprüfung aktiv).
- **Impact:** Mittel - Kernintegration vorhanden, weitere fachliche Vertiefung (z. B. Kontierungsregeln/Freigabeprozesse) offen
- **Evidence:** Screenshots: 20251124_095105_04_invoices_list.png, 20251124_095108_05_create_invoice_form.png; Backend: `app/api/v1/endpoints/finance_invoices.py`
- **Lösung:** Nächster Schritt: Kontierungs-/Steuerschlüssel-Mapping und engere Abstimmung mit Zahlungsabgleich
- **Vergleich:** Odoo-ähnlich
- **Owner:** Backend

### FIBU-AR-05: OP-Verwaltung & Ausgleich
- **Status:** Partial (Ausgleich + Audit-Trail vorhanden)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** op-debitoren.tsx mit OP-Liste; Backend: Einzelausgleich POST `/{op_id}/settle`, Sammelausgleich (FIBU-AP-05) für Kreditoren. **Audit-Trail:** `log_fibu_audit` bei settle/reverse, optional `infrastructure.audit_log`, GET `/{op_id}/settlements` liefert Ausgleichshistorie. Storno: POST `/{op_id}/reverse-settlement`.
- **Impact:** Mittel - Kernfunktion und Audit vorhanden, UI-Tiefe ausbaubar
- **Evidence:** open_items.py (settle, reverse_settlement, get_settlements, log_fibu_audit), op-debitoren.tsx (Tab Ausgleichshistorie)
- **Lösung:** Ausgleich und Audit-Trail implementiert; **OP Debitoren** zeigt Ausgleichshistorie (Tab „Ausgleichshistorie“, GET `/{op_id}/settlements`) in op-debitoren.tsx.
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-AP-01: Kreditorenstamm
- **Status:** Partial (API + IBAN + USt-ID + Dublettencheck)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** **API** `/api/v1/finance/creditors` (CRUD): Create mit **Dublettencheck** (creditor_number pro Tenant), USt-ID- und IBAN-Format-Validierung. Frontend **kreditoren-stamm.tsx**: Stammdaten, IBAN (validateIBAN, useIbanLookup), USt-ID (validateVatIdFormat); **toApiCreditor/fromApiCreditor** mappen Formular ↔ API. Stammdaten-Felder und Dublettencheck umgesetzt.
- **Impact:** Mittel - API und Validierung vorhanden
- **Evidence:** creditors.py, kreditoren-stamm.tsx, lib/utils/iban-validator.ts, lib/utils/vat-validator.ts
- **Lösung:** Kreditoren-API mit CRUD + Dublettencheck; Frontend-Mapping und Validierung implementiert
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-AP-05: OP-Verwaltung & Ausgleich
- **Status:** Partial (Sammelausgleich umgesetzt)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** OP-Kreditoren-Maske mit Liste, Summen, Suche, CRUD und Einzelausgleich; **Sammelausgleich**: POST `/api/v1/finance/open-items/batch-settle`, UI Mehrfachauswahl + Dialog „Alle ausgleichen“. Offen: Zahlungsfreigaben, OP-Import/Abstimmung.
- **Impact:** Mittel - Kernfunktion vorhanden, fachliche Tiefe ausbaufähig
- **Evidence:** open_items.py (batch-settle), op-kreditoren.tsx (Checkboxen, Sammelausgleich-Button/Dialog)
- **Lösung:** Sammelausgleich umgesetzt; weitere Workflow-Erweiterung optional
- **Vergleich:** Basic+
- **Owner:** Backend + Frontend

### FIBU-BNK-01: Bankkontenstamm
- **Status:** Partial (API + UI + IBAN-Validierung)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** API `/api/v1/finance/bank-accounts` (List, Get, Create, Update). Beim Anlegen wird bei Bedarf ein Kontenplan-Eintrag (Gegenkonto) angelegt. UI `bank-stamm.tsx`: Liste, Anlegen, Bearbeiten (Kontonummer, Bankname, IBAN, BIC, Währung, Aktiv). **IBAN:** Frontend prüft vor Submit (validateIBAN, formatIBAN); Backend `_validate_iban` (Mod-97) bei Create/Update. Nav: „Bankkonten (Bankstamm)“.
- **Impact:** Mittel - Schema, UI und IBAN-Validierung vorhanden
- **Evidence:** bank_accounts.py (_validate_iban), bank-stamm.tsx (validateIBAN, formatIBAN), Nav „Bankkonten (Bankstamm)“
- **Lösung:** Umgesetzt inkl. IBAN-Validierung (Frontend + Backend)
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-02: Kontoauszugsimport
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Import für CAMT/MT940/CSV vorhanden (`bank_statement_import.py`) inkl. Rückgabe `import_errors`; UI `bank-abgleich.tsx` zeigt Import-Protokoll/Zeilenfehler jetzt explizit an.
- **Impact:** Mittel - Formate und Fehlertransparenz vorhanden, weitere Parser-Robustheit bleibt ausbaubar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/bank_statement_import.py`; Frontend: `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
- **Lösung:** Nächster Schritt: Parser-Validierung je Bankprofil und strukturierte Fehlercodes
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-04: Bankabstimmung
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `bank_reconciliation.py` liefert Saldovergleich, Differenzliste, Buchungsvorschläge und `line_counts`; Auto-Book schreibt Journal + markiert Statement-Lines als `MATCHED`. Frontend `bank-abgleich.tsx` kann Reconcile-Daten inkl. `line_counts` jetzt korrekt verwerten.
- **Impact:** Mittel - Kernabstimmung nutzbar, weitere Tiefe (Regelwerk, Bulk-Workflow, bessere Gegenkontovorschläge) offen
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/bank_reconciliation.py`
- **Lösung:** Nächster Schritt: Matching-Regeln ausbauen und manuelle Differenzbuchungen als Workflow-Maske ergänzen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-TAX-01: Steuerschlüssel-System
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Tax-Keys API mit CRUD, Länderfilter und zusätzlicher Validierung (ISO-Landcode, Gültigkeitszeitraum, Reverse-Charge nur bei 0%) aktiv. UI `steuerschluessel.tsx` zeigt Steuerart/Reverse-Charge transparent und erlaubt Neuanlage inkl. Intracom/Export/Reverse-Charge. AR/AP-Posting nutzt nun zentralen Tax-Resolver (`app/finance/tax_resolver.py`) mit Country-/EU-/Export-Kontext und Fallback auf DE.
- **Impact:** Mittel - Stammdatenpflege belastbarer, tiefe Steuerlogik (z. B. automatische Kontierung je Belegkontext) bleibt ausbaubar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png; Backend: `app/api/v1/endpoints/tax_keys.py`; Frontend: `packages/frontend-web/src/pages/finance/steuerschluessel.tsx`
- **Lösung:** Steuerfindung in AR/AP-Buchungsfluss je Land/Steuerart angebunden; nächster Schritt: tieferes Mapping je Beleg-/Steuerart (inkl. OSS/ZM)
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-CLS-02: Nebenbuch-Abstimmung
- **Status:** Partial (AR/AP/Bank umgesetzt, FA nicht in Scope)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API `/api/v1/finance/subsidiary-ledger-reconciliation` fachlich korrigiert (reales Schema für Journal/OP) mit Endpunkten für AR/AP/Bank, summary, details und CSV-Export je Ledger/Periode. UI `nebenbuch-abstimmung.tsx`: Perioden-/Ledger-Filter, Saldenvergleich, Drilldown und Export-Button.
- **Impact:** Mittel - Erforderlich für Abschluss
- **Evidence:** `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py`, `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx`, Nav „Nebenbuch-Abstimmung“
- **Lösung:** Umgesetzt für AR/AP/Bank inkl. Export; FA bei Bedarf später
- **Vergleich:** SAP/Odoo haben vollständige Nebenbuch-Abstimmung
- **Owner:** Backend + Frontend

### FIBU-REP-01: Standardreports
- **Status:** Partial (Bilanz/GuV/BWA + Landingpage)
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** API `/api/v1/finance/financial-reports`: balance-sheet, profit-loss, bwa, **export/{report_type}?format=pdf|excel|json**. Export liefert PDF (reportlab) oder Excel (openpyxl) als Download; JSON unverändert. Frontend: fibu/bilanz, fibu/guv, fibu/bwa; **finance/reports.tsx** als Landingpage.
- **Impact:** Mittel - Dashboard und Report-Export (PDF/Excel) nutzbar
- **Evidence:** financial_reports.py (export_report, _report_to_rows), finance/reports.tsx
- **Lösung:** PDF- und Excel-Export für Bilanz/GuV/BWA umgesetzt
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

---

## P2 - Mittel (SOLL, Priorität 3)

### FIBU-GL-04: Sammel-/Massenbuchungen
- **Status:** Partial (CSV-Import + Fehler pro Zeile)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API POST `/api/v1/bulk-journal-import/csv` mit Dry-Run und Import; Rückgabe `ImportResult` inkl. `errors[]` (row_number, field, error_message, row_data). Frontend **buchungsimport.tsx**: 3 Schritte (Datei wählen → Vorschau → Ergebnis), Fehlertabelle pro Zeile in Vorschau und Ergebnis. Excel/API-Stapel optional.
- **Impact:** Niedrig - CSV-Import nutzbar, Excel/API ausbaubar
- **Evidence:** bulk_journal_import.py (ImportError, ImportResult), buchungsimport.tsx, Nav/Schnittstellen-Center „Buchungsimport“
- **Lösung:** CSV-Import-Screen und Fehler pro Zeile umgesetzt; Excel/weitere Formate optional
- **Vergleich:** Basic
- **Owner:** Backend + Frontend

### FIBU-AR-04: Mahnwesen / Dunning
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** mahnwesen.tsx und dunning-editor.tsx vorhanden, aber Mahnstufen/Gebühren/Sperrlogik unklar. Mahnstufen laufen möglicherweise nicht regelbasiert.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Mahnstufen/Gebühren/Sperrlogik prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-AP-03: Prüf-/Freigabeworkflow
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Workflow-Setup/UI gefunden. 2/3/4-Augen je Betrag/Warengruppe nicht möglich. Ohne Freigabe kein Zahlungsstatus „freigegeben".
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Workflow-Setup + UI implementieren
- **Vergleich:** SAP/Odoo haben vollständige Workflow-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-AP-04: Zahlungsläufe / SEPA
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** zahlungslauf-kreditoren.tsx vorhanden, aber SEPA XML Export/Status/Rückläufer unklar. Lauf erzeugt möglicherweise keinen OP-Ausgleich bei Erfolg.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** SEPA XML Export implementieren, Status/Rückläufer prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-03: Automatisches Matching
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Match-UI/regelbasiertes Matching gefunden. Regelbasiertes OP-Matching nicht möglich. Trefferquote nicht nachvollziehbar, manuell nicht übersteuerbar.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Match-UI + regelbasiertes Matching implementieren
- **Vergleich:** SAP/Odoo haben vollständige Matching-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-TAX-02: USt-Voranmeldung / ZM / OSS
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** ustva.tsx vorhanden, aber Export Behördenformat (ELSTER) unklar. Summen stimmen möglicherweise nicht mit GL überein.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Export Behördenformat (ELSTER) implementieren, Summen-Validierung prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-CLS-01: Abschlusschecklisten
- **Status:** Partial (API + Cockpit-UI)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** API `/api/v1/finance/closing-checklists`: Templates, CRUD, cockpit/summary, GET `/{checklist_id}`, POST `/{checklist_id}/items/{item_code}/complete`. Frontend **abschluss-cockpit.tsx**: Übersicht, Link „Details“ pro Checkliste. **abschluss-checklist-detail.tsx**: Detail-UI mit Aufgabenliste und „Erledigen“-Button pro Aufgabe.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** closing_checklists.py, abschluss-cockpit.tsx, abschluss-checklist-detail.tsx, Route fibu/abschluss-checklist-detail/:id
- **Lösung:** API + Cockpit + Detail-UI mit Aufgaben-Erledigen umgesetzt
- **Vergleich:** SAP/Odoo haben vollständige Checklist-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-CLS-03: Abgrenzungen / Rückstellungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Accruals-Flow gefunden. Periodisierung/Wiederkehrbuchungen nicht möglich. Automatischer Lauf nicht möglich.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Accruals-Flow implementieren
- **Vergleich:** SAP/Odoo haben vollständige Accruals-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-REP-02: Drilldown & Analyse
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Drilldown-Trace gefunden. Bericht → Konto → Beleg → Position → Ursprung nicht möglich. 3-Klick-Regel bis Beleg nicht erfüllt.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Drilldown-Funktionalität implementieren
- **Vergleich:** SAP/Odoo haben vollständige Drilldown-Funktionalität
- **Owner:** Frontend + Backend

---

## P3 - Niedrig (SOLL, Priorität 3-4)

### FIBU-GL-06: Fremdwährung & Wechselkurse
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Währungssetup/FX-Buchung gefunden. Kursarten (ECB, manuell, Vertragskurs) nicht verfügbar. Kursdifferenzen werden nicht automatisch gebucht.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Währungssetup + FX-Buchung implementieren
- **Vergleich:** SAP/Odoo haben vollständige FX-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-GL-07: Automatische Buchungsschemata
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Schema-Setup/Auto-Post gefunden. Steuerbuchungen/Skonto/Rundungen/Umlagen nicht automatisch. Regelbasierte Kontierung nicht möglich.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Schema-Setup + Auto-Post implementieren
- **Vergleich:** SAP/Odoo haben vollständige Schema-Funktionalität
- **Owner:** Backend

### FIBU-TAX-03: E-Rechnung (ZUGFeRD/XRechnung)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine E-Invoice-UI/Import/Export gefunden. Import/Export/Validierung nicht möglich. Validierungsfehler werden nicht angezeigt.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** E-Invoice-UI + Import/Export implementieren
- **Vergleich:** SAP/Odoo haben vollständige E-Invoice-Funktionalität
- **Owner:** Backend + Frontend

---

## P4 - Optional (KANN, Priorität 4-5)

### FIBU-GL-08: Kostenrechnung-Integrationspunkte
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Dimensionen (Kostenstellen/Kostenträger) gefunden. Kontierung mit Dimension nicht möglich. Dimensionen sind nicht filter-/summierbar.
- **Impact:** Sehr niedrig - Optional
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Dimensionen (Kostenstellen/Kostenträger) implementieren
- **Vergleich:** SAP/Odoo haben vollständige CO-Integration
- **Owner:** Backend + Frontend

### FIBU-FA-01 bis FIBU-FA-05: Anlagenbuchhaltung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Alle FA-Funktionalitäten fehlen (Anlageklassen, Zugänge, Abschreibungslauf, Abgänge, Anlagenspiegel).
- **Impact:** Sehr niedrig - Optional (nur falls Anlagen in Scope)
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Komplettes FA-Modul implementieren
- **Vergleich:** SAP/Odoo haben vollständige FA-Funktionalität
- **Owner:** Backend + Frontend

### FIBU-IC-01 bis FIBU-IC-02: Intercompany
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Alle IC-Funktionalitäten fehlen (IC-Partner, Konten, Verrechnung, Eliminierung).
- **Impact:** Sehr niedrig - Optional (je Scope)
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Komplettes IC-Modul implementieren
- **Vergleich:** SAP/Odoo haben vollständige IC-Funktionalität
- **Owner:** Backend + Frontend

---

## Zusammenfassung nach Lösungstyp

### Typ A (Konfig/Verdrahtung): 0 GAPs
- Keine reinen Konfigurations-GAPs identifiziert

### Typ B (Integration/Adapter): 1 GAP
- FIBU-AR-02: Ausgangsrechnungen (GL-Buchung/OP-Erzeugung)

### Typ C (Neues Feature/Modul): 21 GAPs
- Die meisten fehlenden Features erfordern neue Module

### Typ D (UX/Edge-Case/Reifegrad): 10 GAPs
- Viele vorhandene Seiten benötigen Funktionalitäts-Erweiterungen

## Nächste Schritte

1. **P0-Status: abgeschlossen (Priorität 1):**
   - FIBU-AR-03: Zahlungseingänge & Matching ✅
   - FIBU-AP-02: Eingangsrechnungen ✅
   - FIBU-GL-05: Periodensteuerung ✅
   - FIBU-COMP-01: GoBD / Audit Trail ✅

2. **P1-GAPs beheben (Priorität 2):**
   - Alle Partial-Status GAPs prüfen und vervollständigen
   - FIBU-AP-05: OP-Verwaltung & Ausgleich (Kreditoren)
   - FIBU-CLS-02: Nebenbuch-Abstimmung (AR/AP/Bank + Drilldown umgesetzt; FA optional)

3. **P2-GAPs beheben (Priorität 3):**
   - SOLL-Features nach Bedarf implementieren

4. **P3/P4-GAPs (Optional):**
   - Nach Bedarf und Ressourcen

## Referenzen

- FiBU Capability Model: User-Query (Lastenheft)
- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- JSON Summary: `evidence/screenshots/finance/finance_mission_2025-11-24T08-51-19.344194.json`
- Screenshots: `evidence/screenshots/finance/`
- Matrix: `gap/matrix.csv`

