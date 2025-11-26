# Einkauf / Procurement Capability Model (Referenz für GAP-Analyse)

**Version:** 1.0  
**Datum:** 2025-01-27  
**Zweck:** Referenzmodell zur Funktionsabdeckung von Valero NeuroERP im Bereich Einkauf (Source-to-Pay)  
**Baseline:** Vollumfängliches ERP-Niveau (SAP MM / Oracle Procurement / Odoo Enterprise Purchase)

## Legende Priorität

- **MUSS** = rechtlich/operativ zwingend / Kernprozess
- **SOLL** = Standard in großen ERPs
- **KANN** = nice-to-have / branchenspezifisch

## Beleg-Evidence

- UI-Screenshots (ID/Dateiname)
- Playwright-Trace/Video
- Flow-ID aus UI-Explorer JSON
- API-Responses/Schemas (falls vorhanden)

---

## 1. Supplier Lifecycle & Stammdaten

### PROC-SUP-01 Lieferantenstamm

**Priorität:** MUSS  

**Inhalt:**
- Lieferant anlegen/ändern/sperren/archivieren
- Adressen, Ansprechpartner, Bankdaten, Steuerinfos
- Lieferantengruppen, Klassifikationen

**Evidence:** Supplier-Create/Edit UI  

**Akzeptanz:**
- Pflichtfelder + Dublettencheck + Historie

---

### PROC-SUP-02 Lieferantenbewertung

**Priorität:** SOLL  

**Inhalt:**
- Kriterien: Qualität, Termintreue, Preis, Service
- Scores + Trends, Sperr-/Freigabelogik

**Evidence:** Supplier-Score UI/Report  

**Akzeptanz:**
- Bewertung wirkt auf Auswahl/Workflows

---

### PROC-SUP-03 Compliance / Dokumente

**Priorität:** SOLL  

**Inhalt:**
- Zertifikate, Rahmenverträge, NDA, ESG
- Gültigkeit/Erinnerungen

**Evidence:** Supplier-Docs UI  

**Akzeptanz:**
- Ablauf löst Hinweis/Sperre aus

---

## 2. Bedarf / Requisition-to-Order

### PROC-REQ-01 Bedarfsmeldung (Purchase Requisition)

**Priorität:** MUSS  

**Inhalt:**
- Bedarf erfassen (Artikel/Service/Projekt)
- Mengen, Termin, Kostenstelle/Projekt
- Status: Entwurf → Freigabe → Bestellung

**Evidence:** Requisition-Flow  

**Akzeptanz:**
- Bedarf erzeugt prüfbaren Vorgang

---

### PROC-REQ-02 Bedarfsgenehmigung

**Priorität:** MUSS/SOLL je Unternehmen  

**Inhalt:**
- Freigabe nach Betrag/Warengruppe/Kostenstelle
- Vertretung/Eskalation

**Evidence:** Approval-UI  

**Akzeptanz:**
- Ohne Freigabe keine Bestellung

---

### PROC-REQ-03 Katalog / Guided Buying

**Priorität:** KANN/SOLL  

**Inhalt:**
- interne Kataloge, Punchout
- geführte Auswahl

**Evidence:** Catalog-UI  

**Akzeptanz:**
- Requisition aus Katalog möglich

---

## 3. Sourcing / RFQ / Angebotsvergleich

### PROC-RFQ-01 Anfrage / RFQ

**Priorität:** SOLL  

**Inhalt:**
- Lieferanten auswählen, RFQ versenden
- Positionen, Spezifikationen, Fristen

**Evidence:** RFQ-Create/Send  

**Akzeptanz:**
- RFQ-Status nachvollziehbar

---

### PROC-RFQ-02 Lieferantenangebote / Bids

**Priorität:** SOLL  

**Inhalt:**
- Angebote erfassen/importieren
- Preise, Lieferzeiten, Nebenbedingungen

**Evidence:** Bid-UI  

**Akzeptanz:**
- Mehrere Angebote pro RFQ möglich

---

### PROC-RFQ-03 Angebotsvergleich / Award

**Priorität:** SOLL  

**Inhalt:**
- Vergleichsmatrix Preis/Leadtime/Score
- Entscheidungsdoku

**Evidence:** Comparison-UI  

**Akzeptanz:**
- Award erzeugt Vorschlag für Bestellung

---

### PROC-CTR-01 Rahmenverträge

**Priorität:** SOLL  

**Inhalt:**
- Vertragslaufzeit, Kontingente, Preise
- Abrufe gegen Vertrag

**Evidence:** Contract-UI  

**Akzeptanz:**
- Order referenziert Vertrag

---

## 4. Bestellung / Purchase Order Management

### PROC-PO-01 Bestellung (PO) erstellen

**Priorität:** MUSS  

**Inhalt:**
- PO aus Bedarf/RFQ/Vertrag oder direkt
- Positionen, Lieferadresse, Incoterms, Zahlungsbedingungen

**Evidence:** PO-Create-Flow  

**Akzeptanz:**
- PO hat eindeutige Nummer, Status

---

### PROC-PO-02 PO-Änderungen & Storno

**Priorität:** MUSS  

**Inhalt:**
- Change-Log, Versionierung
- Genehmigungslogik bei Änderungen

**Evidence:** PO-Change-Flow  

**Akzeptanz:**
- Jede Änderung auditierbar

---

### PROC-PO-03 PO-Kommunikation

**Priorität:** SOLL  

**Inhalt:**
- PO-Dokumente (PDF/Email/Portal)
- Sprachen/Branding

**Evidence:** PO-Print/Send  

**Akzeptanz:**
- Lieferant erhält korrekte PO

---

### PROC-PO-04 Bestellabrufe / Lieferpläne

**Priorität:** KANN/SOLL  

**Inhalt:**
- Abrufe gegen Kontrakte
- Lieferplan/Release-Logik

**Evidence:** Schedule-UI  

**Akzeptanz:**
- Abrufe reduzieren Kontingent

---

## 5. Wareneingang / Service Entry (Receipt-to-Verify)

### PROC-GR-01 Wareneingang

**Priorität:** MUSS  

**Inhalt:**
- Eingang buchen gegen PO
- Teil-/Restmengen, Backorder
- Qualitätsprüfung optional

**Evidence:** GR-Flow  

**Akzeptanz:**
- GR erzeugt Lagerbewegung + Status

---

### PROC-GR-02 Retouren an Lieferant

**Priorität:** SOLL  

**Inhalt:**
- Rücksendung, Gründe, Gutschriftbezug

**Evidence:** Return-Flow  

**Akzeptanz:**
- Rückgabe korrigiert Lager/FiBU

---

### PROC-SE-01 Leistungsnachweis (Service Entry Sheet)

**Priorität:** SOLL (MUSS wenn Services in Scope)  

**Inhalt:**
- Leistungen erfassen, prüfen, freigeben

**Evidence:** SES-Flow  

**Akzeptanz:**
- SES Voraussetzung für Rechnung

---

## 6. Rechnungsprüfung / Invoice-to-Pay

### PROC-IV-01 Eingangsrechnung

**Priorität:** MUSS  

**Inhalt:**
- Rechnung erfassen/importieren (PDF/OCR/API)
- Steuer, Kontierung, Anlagebezug

**Evidence:** Invoice-Create-Flow  

**Akzeptanz:**
- Rechnung erzeugt AP-OP

---

### PROC-IV-02 2/3-Wege-Abgleich (PO-GR-IV)

**Priorität:** MUSS  

**Inhalt:**
- Abgleich Menge/Preis/Toleranzen
- Blockierung bei Abweichungen

**Evidence:** Match-UI  

**Akzeptanz:**
- Abweichungen werden begründet/gelöst

---

### PROC-IV-03 Rechnungsfreigabe

**Priorität:** MUSS/SOLL  

**Inhalt:**
- Freigabe nach Toleranzen/Betrag/Warengruppe
- Eskalation/Vertretung

**Evidence:** Approval-Flow  

**Akzeptanz:**
- Ohne Freigabe keine Zahlung

---

### PROC-PAY-01 Zahlungsläufe

**Priorität:** MUSS (wenn AP-Zahlung in Scope)  

**Inhalt:**
- SEPA Export, Zahlungsstatus, Skonto

**Evidence:** Payment-Run UI  

**Akzeptanz:**
- Zahlung gleicht OP aus

---

### PROC-PAY-02 Lieferantengutschriften / Belastungen

**Priorität:** SOLL  

**Inhalt:**
- Credit Memo, Debit Memo, Verrechnung

**Evidence:** Memo-Flow  

**Akzeptanz:**
- Korrekte FiBU-Buchung

---

## 7. Reporting & Kontrolle

### PROC-REP-01 Standardreports Einkauf

**Priorität:** MUSS  

**Inhalt:**
- Offene Bestellungen, Spend-Analyse
- Lieferantenperformance
- Toleranz-/Abweichungsreports

**Evidence:** Dashboards/Reports  

**Akzeptanz:**
- Filter, Drilldown, Export

---

### PROC-REP-02 Belegkette / Audit Trail

**Priorität:** SOLL  

**Inhalt:**
- Bedarf → RFQ → PO → GR/SES → IV → Pay

**Evidence:** Drilldown-Trace  

**Akzeptanz:**
- lückenlose Nachvollziehbarkeit

---

## 8. Rollen, Berechtigungen, Workflows

### PROC-AUTH-01 Rollenmodell Einkauf

**Priorität:** MUSS  

**Inhalt:**
- Bedarfsersteller, Genehmiger, Einkäufer, Wareneingang, AP, Admin

**Evidence:** Role-Setup  

**Akzeptanz:**
- RBAC verhindert unberechtigte Aktionen

---

### PROC-AUTH-02 Workflow-Regeln

**Priorität:** MUSS/SOLL  

**Inhalt:**
- Freigaben, Toleranzen, Eskalation

**Evidence:** Workflow-UI  

**Akzeptanz:**
- Regeln sind konfigurierbar

---

## 9. Schnittstellen & Integrationen

### PROC-INT-01 API / Import / Export

**Priorität:** MUSS  

**Inhalt:**
- Supplier/Item/PO/GR/IV
- CSV/Excel/API/Webhooks

**Evidence:** Import-UI, API-Docs  

**Akzeptanz:**
- Datenrundtrip möglich

---

### PROC-INT-02 EDI / Lieferantenportal

**Priorität:** KANN/SOLL je Branche  

**Inhalt:**
- ORDERS, ORDRSP, DESADV, INVOIC
- Portal-Self-Service

**Evidence:** EDI/Portal-Flows  

**Akzeptanz:**
- Statusmapping sauber

---

### PROC-INT-03 Katalog/Punchout

**Priorität:** KANN  

**Inhalt:**
- OCI/cXML Punchout, Preis-Sync

**Evidence:** Punchout-UI  

**Akzeptanz:**
- Requisition aus Punchout möglich

---

## Zusammenfassung

**Gesamt Capabilities:** 28  
**MUSS:** 12  
**SOLL:** 13  
**KANN:** 3

**Nächste Schritte:**
1. GAP-Analyse durchführen (Status: Yes/Partial/No)
2. Evidence sammeln (Screenshots, Flows, API-Docs)
3. GAP-Matrix aktualisieren (`gap/matrix.csv`)
4. Implementierungsplan erstellen

