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

### FIBU-GL-05: Periodensteuerung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Perioden-Admin-Screen gefunden, keine Sperrlogik. Buchungen in gesperrter Periode werden nicht blockiert.
- **Impact:** Hohe - GoBD-Compliance gefährdet
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Periodensteuerung + Sperrlogik implementieren
- **Vergleich:** SAP/Odoo haben vollständige Periodensteuerung
- **Owner:** Backend + Frontend

### FIBU-COMP-01: GoBD / Audit Trail
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** GoBDAuditTrail in services/finance vorhanden, aber Audit-View/Historie/Logs-UI fehlt. Jede Änderung ist nicht mit User+Zeit protokolliert sichtbar.
- **Impact:** Hohe - GoBD-Compliance unvollständig
- **Evidence:** Backend vorhanden, UI fehlt
- **Lösung:** Audit-View-UI implementieren, Historie/Logs anzeigen
- **Vergleich:** SAP/Odoo haben vollständige Audit-Trail-UI
- **Owner:** Frontend

---

## P1 - Hoch (MUSS, Priorität 2)

### FIBU-GL-01: Kontenplan & Kontenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Kontenplan-Seite vorhanden (chart-of-accounts.tsx), aber Hierarchie/Hierarchieauswertung unklar. Konto kann möglicherweise angelegt werden, aber Hierarchieauswertung in Reports nicht sichtbar.
- **Impact:** Mittel - Funktionalität vorhanden, aber unvollständig
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Hierarchie-Funktionalität prüfen und vervollständigen
- **Vergleich:** Odoo-ähnlich
- **Owner:** Frontend

### FIBU-GL-02: Belegprinzip & Nummernkreise
- **Status:** Partial
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Nummernkreise in documents/router.py vorhanden, aber Belegprinzip/Storno-Dialog unklar. Belege sind möglicherweise nicht revisionssicher referenziert.
- **Impact:** Mittel - Funktionalität teilweise vorhanden
- **Evidence:** Backend vorhanden, UI unklar
- **Lösung:** Storno-Dialog implementieren, Belegprinzip dokumentieren
- **Vergleich:** Basic
- **Owner:** Backend + Frontend

### FIBU-AR-01: Debitorenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** debitoren-liste.tsx vorhanden, aber Stammdaten/Adressen/USt-ID/Kreditlimit unklar. Pflichtfelder + Dublettencheck möglicherweise nicht vollständig.
- **Impact:** Mittel - Funktionalität vorhanden, aber unvollständig
- **Evidence:** Screenshot: 20251124_095105_04_invoices_list.png
- **Lösung:** Stammdaten-Felder prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-AR-02: Ausgangsrechnungen
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Invoices-Liste und Create Invoice vorhanden, API finance_invoices.py erstellt, aber GL-Buchung/OP-Erzeugung unklar. Rechnung erzeugt möglicherweise keine GL-Buchung + OP.
- **Impact:** Mittel - Formular vorhanden, Backend-Integration unvollständig
- **Evidence:** Screenshots: 20251124_095105_04_invoices_list.png, 20251124_095108_05_create_invoice_form.png
- **Lösung:** GL-Buchung + OP-Erzeugung bei Rechnungserstellung implementieren
- **Vergleich:** Odoo-ähnlich
- **Owner:** Backend

### FIBU-AR-05: OP-Verwaltung & Ausgleich
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** op-debitoren.tsx vorhanden, aber Ausgleich/Verrechnung/Audit-Trail unklar. Vollständiger Audit Trail pro Ausgleich möglicherweise nicht vorhanden.
- **Impact:** Mittel - Funktionalität vorhanden, aber unvollständig
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Ausgleich/Verrechnung-Funktionalität prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-AP-01: Kreditorenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** kreditoren-stamm.tsx vorhanden, aber Stammdaten/Bankdaten/IBAN-Validierung unklar. Bankdaten möglicherweise nicht validierbar (IBAN).
- **Impact:** Mittel - Funktionalität vorhanden, aber unvollständig
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** IBAN-Validierung implementieren, Stammdaten vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-AP-05: OP-Verwaltung & Ausgleich
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine OP-Liste für Kreditoren gefunden. Kreditoren-OPs können nicht verwaltet werden.
- **Impact:** Mittel - Erforderlich für AP
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** OP-Liste für Kreditoren implementieren (ähnlich wie Debitoren)
- **Vergleich:** SAP/Odoo haben OP-Verwaltung für beide Seiten
- **Owner:** Backend + Frontend

### FIBU-BNK-01: Bankkontenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Bankkonten in database/schema.sql vorhanden, aber Bankstamm-UI unklar. Bankkonto möglicherweise nicht mit Gegenkonto verknüpft.
- **Impact:** Mittel - Schema vorhanden, UI fehlt
- **Evidence:** Schema vorhanden
- **Lösung:** Bankstamm-UI implementieren, Gegenkonto-Verknüpfung prüfen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-BNK-02: Kontoauszugsimport
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** bank-abgleich.tsx vorhanden, aber CAMT/MT940/CSV-Import unklar. Importfehler pro Zeile möglicherweise nicht sichtbar.
- **Impact:** Mittel - Seite vorhanden, Import-Formate unklar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Import-Formate (CAMT/MT940/CSV) implementieren, Import-Protokoll anzeigen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

### FIBU-BNK-04: Bankabstimmung
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** bank-abgleich.tsx vorhanden, aber Saldoabgleich/Differenzliste unklar. Differenzen erzeugen möglicherweise keinen Buchungsvorschlag.
- **Impact:** Mittel - Seite vorhanden, Funktionalität unklar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Saldoabgleich/Differenzliste-Funktionalität prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-TAX-01: Steuerschlüssel-System
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** steuerschluessel.tsx vorhanden, aber Steuerarten/Sätze/Länderlogik/Reverse-Charge unklar. Steuer bestimmt möglicherweise nicht korrekte Konten + Meldelogik.
- **Impact:** Mittel - Seite vorhanden, Vollständigkeit unklar
- **Evidence:** Screenshot: 20251124_095102_03_finance_module.png
- **Lösung:** Steuerarten/Sätze/Länderlogik/Reverse-Charge prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend

### FIBU-CLS-02: Nebenbuch-Abstimmung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Reconciliation-Reports gefunden. AR/AP/FA/Bank ↔ GL Abgleich nicht möglich. Differenzen sind nicht drilldown-fähig.
- **Impact:** Mittel - Erforderlich für Abschluss
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Reconciliation-Reports implementieren
- **Vergleich:** SAP/Odoo haben vollständige Nebenbuch-Abstimmung
- **Owner:** Backend + Frontend

### FIBU-REP-01: Standardreports
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Dashboard vorhanden, aber Bilanz/GuV/BWA/Saldenliste/Journal/OP-Listen unklar. Export (PDF/Excel) möglicherweise nicht verfügbar.
- **Impact:** Mittel - Dashboard vorhanden, Reports unklar
- **Evidence:** Screenshot: 20251124_095059_02_dashboard.png
- **Lösung:** Standardreports (Bilanz/GuV/BWA) implementieren, Export-Funktionalität prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend

---

## P2 - Mittel (SOLL, Priorität 3)

### FIBU-GL-04: Sammel-/Massenbuchungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Import-Screen für CSV/Excel/API gefunden. Import zeigt keine Fehler pro Zeile nachvollziehbar.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Import-Screen + Stapel-Postenliste implementieren
- **Vergleich:** SAP/Odoo haben vollständige Import-Funktionalität
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
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Closing-Checklist gefunden. Aufgaben je Periode/Status/Verantwortliche nicht verfügbar. Checklist steuert Abschlussprozess nicht.
- **Impact:** Niedrig - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Closing-Checklist implementieren
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

### Typ B (Integration/Adapter): 2 GAPs
- FIBU-AR-02: Ausgangsrechnungen (GL-Buchung/OP-Erzeugung)
- FIBU-COMP-01: GoBD / Audit Trail (UI fehlt)

### Typ C (Neues Feature/Modul): 21 GAPs
- Die meisten fehlenden Features erfordern neue Module

### Typ D (UX/Edge-Case/Reifegrad): 10 GAPs
- Viele vorhandene Seiten benötigen Funktionalitäts-Erweiterungen

## Nächste Schritte

1. **P0-GAPs beheben (Priorität 1):**
   - FIBU-AR-03: Zahlungseingänge & Matching
   - FIBU-AP-02: Eingangsrechnungen
   - FIBU-GL-05: Periodensteuerung
   - FIBU-COMP-01: GoBD / Audit Trail (UI)

2. **P1-GAPs beheben (Priorität 2):**
   - Alle Partial-Status GAPs prüfen und vervollständigen
   - FIBU-AP-05: OP-Verwaltung & Ausgleich (Kreditoren)
   - FIBU-CLS-02: Nebenbuch-Abstimmung

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
