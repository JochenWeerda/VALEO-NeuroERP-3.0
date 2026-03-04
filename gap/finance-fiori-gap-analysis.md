# GAP-Analyse VALEO NeuroERP Finanz Suite (SAP Fiori Referenz)

**Stand:** 2026-03-04  
**Autor:** Codex-Analyse  
**SOLL-Referenz:** SAP Fiori Apps Reference Library + SAP Help (Finance/Controlling)  
**IST-Basis:** `gap/gaps.md`, `gap/capability-model.md`, `docs/specs/fibu_architektur_spezifikation.md`, `docs/compliance/gobd-checklist.md`, `docs/GOBD-VORGEHENSPLAN.md`, `docs/FIBU-SUITE-TODO.md`, `app/api/v1/api.py`, `packages/frontend-web/src/app/navigation/manifest.tsx`

---

## 1) Zielbild (SOLL) und Bewertungslogik

Diese Analyse verknüpft SAP-Fiori-Referenzfunktionen pro Functional Area mit dem VALEO-IST.

**Bewertungsschema pro Funktion:**
- `Ja`: fachlich und technisch in VALEO Ende-zu-Ende vorhanden
- `Teilweise`: API oder UI vorhanden, aber Prozesskette/Integration/UX/Compliance nicht vollständig
- `Nein`: fachliche Kernfunktion nicht vorhanden

**Gap-Typen:**
- `Kritisch (P0)`: Compliance/Abschluss-/Kernprozessrisiko
- `Strategisch (P1)`: Skalierung, Wettbewerbsfähigkeit, Effizienz
- `Optional (P2)`: Komfort, Reifegrad, erweiterte Analytics

---

## 2) SOLL→IST Gap-Tabelle (A–D)

| Bereich | Fiori App / Capability (SOLL) | Business Zweck | VALEO vorhanden | Gap-Typ | Priorität | Empfohlene VALEO-Modulbezeichnung |
|---|---|---|---|---|---|---|
| A Core Financials | Post General Journal Entries (`F0717A`) | Manuelle GL-Buchung mit Validierung | Teilweise | Kritisch | P0 | `FiBu.Buchungserfassung2` |
| A Core Financials | Manage Journal Entries (`F0718`) | Journalbearbeitung, Korrektur, Nachvollzug | Teilweise | Strategisch | P1 | `FiBu.Buchungsjournal2` |
| A Core Financials | Display G/L Account Balances (`F2217`) | Salden-/Kontenmonitoring | Teilweise | Strategisch | P1 | `FiBu.GL-Saldenmonitor` |
| A Core Financials | Trial Balance (`F0996`) | Abschlussnahe Saldenprüfung | Teilweise | Kritisch | P0 | `FiBu.Abschluss.TrialBalance` |
| A Core Financials | Manage Posting Periods (`F2548`) | Perioden öffnen/schließen/sperren | Teilweise | Kritisch | P0 | `FiBu.Periodenverwaltung` |
| A Core Financials | Manage Supplier Line Items (`F1060` family) | Kreditorenposten prüfen/ausgleichen | Teilweise | Kritisch | P0 | `FiBu.OP.Kreditoren` |
| A Core Financials | Manage Customer Line Items (`F0764`) | Debitorenposten prüfen/ausgleichen | Teilweise | Strategisch | P1 | `FiBu.OP.Debitoren+Matching` |
| A Core Financials | Verify General Journal Entries (`F0711`) | Freigabe-/Prüfworkflow für Buchungen | Teilweise | Strategisch | P1 | `FiBu.Buchungsfreigabe` |
| A Core Financials | Manage Fixed Assets (`F3066`) | Anlagenstamm + Lebenszyklus | Teilweise | Strategisch | P1 | `FiBu.Anlagenbuchhaltung` |
| A Core Financials | Asset Accounting Jobs / Depreciation | AfA-Läufe, Abgang/Umbuchung | Teilweise | Strategisch | P1 | `FiBu.Anlagen.AfALauf` |
| A Core Financials | Reprocess Bank Statements (`F1520`) | Bankimport, Fehlerbearbeitung, Abstimmung | Teilweise | Kritisch | P0 | `FiBu.Bankabgleich2` |
| A Core Financials | Cash/Bank Position | Liquiditätsübersicht, kurzfristige Steuerung | Nein | Strategisch | P1 | `FiBu.Treasury.CashPosition` |
| A Core Financials | Credit Management Apps | Kreditlimitprüfung/Exposure/Dispute | Teilweise | Strategisch | P1 | `FiBu.CreditManagement` |
| A Core Financials | Revenue Recognition / IFRS15 | Periodengerechte Umsatzabgrenzung | Nein | Strategisch | P1 | `FiBu.RevenueAccounting` |
| B Controlling | Manage Cost Centers (`F1600`) | Kostenstellenstamm + Verantwortungen | Teilweise | Strategisch | P1 | `CO.Kostenstellen` |
| B Controlling | Manage Internal Orders | projekt-/auftragsspezifische Kostensteuerung | Nein | Strategisch | P1 | `CO.Innenauftraege` |
| B Controlling | Profit Center Accounting | Ergebnissteuerung nach Profit Centern | Nein | Strategisch | P1 | `CO.ProfitCenter` |
| B Controlling | Margin Analysis | Deckungsbeitrags-/Margenanalyse | Nein | Strategisch | P1 | `CO.MarginAnalysis` |
| B Controlling | Product Cost Controlling | Herstellkosten, Kalkulation, Abweichungen | Nein | Strategisch | P1 | `CO.ProductCosting` |
| C GRC | Audit Log Viewer | revisionssichere Änderungs-/Prozesshistorie | Teilweise | Kritisch | P0 | `Compliance.AuditTrailWorkbench` |
| C GRC | Segregation of Duties / Access Review | Rollen-/Berechtigungsprüfung | Teilweise | Strategisch | P1 | `Compliance.AccessControlCenter` |
| C GRC | Financial Compliance Cockpit | Compliance-Status (GoBD/HGB) | Teilweise | Kritisch | P0 | `Compliance.FinancialCockpit` |
| D Reporting | Balance Sheet / P&L Apps | Bilanz, GuV, periodischer Abschlussblick | Teilweise | Strategisch | P1 | `FiBu.Reporting.FinStatements` |
| D Reporting | Cash Flow Reporting | Zahlungsstrom/Finanzmittelrechnung | Nein | Strategisch | P1 | `FiBu.Reporting.CashFlow` |
| D Reporting | KPI Dashboards (Analytical) | Management-KPIs, Drilldowns | Teilweise | Optional | P2 | `FiBu.Analytics.KPIHub` |
| D Reporting | Embedded Analytics / Drilldown | Von KPI bis Beleg in wenigen Klicks | Teilweise | Strategisch | P1 | `FiBu.Analytics.Drilldown` |

---

## 3) Empfohlene neue/erweiterte VALEO-Module (Finance Suite 2.0)

### 3.1 P0-Module (kritisch zuerst)

1. **`FiBu.Periodenverwaltung`**
- Kernmasken: `Listenmaske Perioden`, `Detailmaske Periode`, `Dialog Sperren/Freigeben`
- Schnittstellen: Journal Posting API, Abschluss-Checklisten
- Datenobjekte: `accounting_period`, `period_status_history`, `period_lock_reason`

2. **`FiBu.Buchungserfassung2` + `FiBu.Buchungsjournal2`**
- Kernmasken: `Buchung erfassen`, `Journal-Worklist`, `Freigabe/Prüf-Dialog`
- Schnittstellen: Kontenplan, Steuerschlüssel, OP, Audit
- Datenobjekte: `journal_entry`, `journal_line`, `posting_validation_result`

3. **`FiBu.OP.Kreditoren` + `FiBu.OP.Debitoren+Matching`**
- Kernmasken: `OP-Liste`, `Matching-Dialog`, `Clearing-Dialog`, `Import-Fehlerdialog`
- Schnittstellen: Bankimport (CAMT/MT940), Zahlungsläufe, Mahnwesen
- Datenobjekte: `open_item`, `matching_rule`, `clearing_batch`

4. **`Compliance.AuditTrailWorkbench`**
- Kernmasken: `Audit-Listenmaske`, `Audit-Detail (Vorher/Nachher)`, `Prüferexport-Dialog`
- Schnittstellen: Audit-API, GoBD-Archiv, Export (CSV/ZIP)
- Datenobjekte: `audit_log`, `audit_export_job`, `audit_filter_profile`

### 3.2 P1-Module (struktureller Ausbau)

5. **`FiBu.Bankabgleich2`**
- CAMT/MT940 Reprocess, Trefferquote, manuelle Übersteuerung, Restposten-Logik

6. **`FiBu.CreditManagement`**
- Limitregeln, Exposure, Dispute/Blockierung, Freigabepfad

7. **`FiBu.Anlagenbuchhaltung` + `FiBu.Anlagen.AfALauf`**
- Voller Anlagenlebenszyklus inkl. periodischer Läufe und Reports

8. **`CO.*`-Suite (`Kostenstellen`, `Innenaufträge`, `ProfitCenter`, `Margin`, `ProductCosting`)**
- CO-Kernobjekte plus Durchstich ins GL/Reporting

9. **`FiBu.Reporting.CashFlow` + `FiBu.Analytics.Drilldown`**
- Cashflow-Darstellung und konsistenter Drilldown bis Beleg

---

## 4) Kritische Compliance-Gaps (GoBD/HGB/IFRS/E-Rechnung)

Abgleich gegen `docs/compliance/gobd-checklist.md` und `docs/GOBD-VORGEHENSPLAN.md`:

1. **Audit-Trail UI und Prüfersicht nicht durchgängig als Workbench**
- Risiko: Nachvollziehbarkeit praktisch eingeschränkt (UI-Filter/Export/Forensik nicht einheitlich)
- Maßnahme: `Compliance.AuditTrailWorkbench` als zentrale Historie inkl. Prüferexport

2. **Periodensperrlogik nicht konsequent in allen Buchungspfaden**
- Risiko: Buchungen in gesperrten Perioden möglich (GoBD/HGB-Abschlussrisiko)
- Maßnahme: zentrale Server-Policy `posting_guard(period_status)` + UI-Precheck

3. **WORM/Retention nur teilweise umgesetzt**
- Risiko: Unveränderbarkeit/Aufbewahrung nicht voll belastbar
- Maßnahme: technischer Nachweis Objekt-Lock/WORM + Retention-Automation

4. **Verfahrensdokumentation unvollständig/verteilt**
- Risiko: Betriebsprüfung, Prüferkommunikation
- Maßnahme: konsolidierte Verfahrensdoku inkl. Datenfluss, Kontrollen, Rollen, Exportpfade

5. **E-Rechnung flächendeckend (XRechnung/ZUGFeRD) noch uneinheitlich**
- Risiko: regulatorische und Prozessbrüche zwischen Modulen
- Maßnahme: einheitlicher E-Rechnungsservice mit Status-/Validierungsrückmeldung

6. **IFRS-relevante Revenue-Themen nicht als dediziertes Modul**
- Risiko: periodengerechte Umsatzabgrenzung bei komplexen Verträgen
- Maßnahme: `FiBu.RevenueAccounting` (P1), Start mit einfachen RevRec-Regeln

---

## 5) UX-Muster (Fiori → VALEO Mask Builder)

Zuordnung gemäß `docs/FIBU-SUITE-TODO.md` und bestehendem Mask-Builder:

- **Fiori List Report** → VALEO `ListReport/Worklist`  
  für: OP-Listen, Journal-Worklist, Audit-Listen

- **Fiori Object Page** → VALEO `ObjectPage`  
  für: Buchungsdetail, Periodendetail, Anlagenobjekt

- **Fiori Analytical List Page** → VALEO `OverviewPage + Drilldown`  
  für: KPI/Abschluss-Cockpit, Cashflow, Margin

- **Fiori Dialog/Wizard-Flow** → VALEO `Wizard/Dialog`  
  für: Matching, Freigabe, Periodenabschluss, Prüferexport

**Konkrete Blueprint-Empfehlung:**
- Dashboard-Masken: `OverviewPage`
- Massenverarbeitung (Import/Matching/Journal): `Worklist + Wizard`
- Drilldown-Analyse: `Analytical List + Detail Object`
- Workflow-Masken: `Inbox/Approval Worklist`

---

## 6) Priorisierte Roadmap (Phase 1–3)

### Phase 1 (0–12 Wochen) – Compliance + Kernprozesse
- FIBU-GL-05: Periodensteuerung + Sperrlogik E2E
- FIBU-COMP-01: AuditTrailWorkbench
- FIBU-AR-03: Zahlungseingang/Matching-UI
- FIBU-AP-02: Eingangsrechnungen durchgängiger Flow
- Abschlussnahe Kernreports (Trial Balance, Journal, OP-Listen) stabilisieren

### Phase 2 (12–24 Wochen) – Struktureller Ausbau
- Bankabgleich2 (Reprocess + Auto/Manuell-Hybrid)
- Credit Management
- Anlagenbuchhaltung vertiefen (AfA, Abgang, Umbuchung)
- Start CO-Suite (Kostenstellen + Innenaufträge)

### Phase 3 (24+ Wochen) – Optimierung/Analytics
- Profit Center / Margin / Product Costing
- Cashflow-Reporting
- Embedded Analytics (3-Klick-Drilldown bis Beleg)
- UX-Harmonisierung (PageToolbar/Command Palette, weniger Ribbon)

**Detaillierte Aufwandsschätzung (SP/PT):**  
Siehe [docs/roadmap/finance-suite-roadmap.md](../docs/roadmap/finance-suite-roadmap.md)

---

## 7) Optionaler Vertiefungspfad

1. **Finance-Gap-Matrix DE Mittelstand** (DATEV/SEPA/ELSTER/UStVA): +0,5–1 Tag  
2. **IFRS/HGB-Prioritäten 2026**: +0,5 Tag  
3. **Modularchitektur Finance 2.0 (Diagramm + Abhängigkeiten)**: +1 Tag  
4. **Roadmap mit Aufwandsschätzung (Story Points/Tage)**: ✅ umgesetzt in `docs/roadmap/finance-suite-roadmap.md`

---

## 8) Quellen (SOLL)

- SAP Fiori Apps Reference Library: https://fioriappslibrary.hana.ondemand.com/sap/fix/externalViewer/  
- SAP Help – *Post General Journal Entries (F0717A)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/6cb8e754ce884bc39de9f0f171ab5df8.html  
- SAP Help – *Manage Posting Periods (F2548)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/2d7f5773af9f4ca08c7f9f5930eb3b4e.html  
- SAP Help – *Trial Balance (F0996)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/c65a9fe319cc4dcfba4f98f1165f7f9c.html  
- SAP Help – *Verify General Journal Entries (F0711)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/3e5f90c3a6454ce18fb7487579dd068f.html  
- SAP Help – *Manage Cost Centers (F1600)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/9dd8b2db34e34f0494212217983f5531.html  
- SAP Help – *Display Customer Line Items (F0764)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/5f6ef31e7f2d42ab8c76f9f7e44b3658.html  
- SAP Help – *Manage Fixed Assets (F3066)*: https://help.sap.com/doc/34796706f38646f68d51a0fa0d4636e4/100/en-US/1f5abf824a7c43f5bc8197b53f38d56b.html

---

## 9) Quellen (IST intern)

- `gap/gaps.md`
- `gap/capability-model.md`
- `docs/specs/fibu_architektur_spezifikation.md`
- `docs/compliance/gobd-checklist.md`
- `docs/GOBD-VORGEHENSPLAN.md`
- `docs/FIBU-SUITE-TODO.md`
- `app/api/v1/api.py`
- `packages/frontend-web/src/app/navigation/manifest.tsx`
