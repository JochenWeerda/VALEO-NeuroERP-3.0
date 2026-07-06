# Einkauf / Procurement Capability Model (Referenz fÃ¼r GAP-Analyse)

**Version:** 1.0
**Datum:** 2025-01-27
**Zweck:** Referenzmodell zur Funktionsabdeckung von Valero NeuroERP im Bereich Einkauf (Source-to-Pay)
**Baseline:** VollumfÃ¤ngliches ERP-Niveau (SAP MM / Oracle Procurement / Community ERP Enterprise Purchase)

## Legende PrioritÃ¤t

- **MUSS** = rechtlich/operativ zwingend / Kernprozess
- **SOLL** = Standard in groÃŸen ERPs
- **KANN** = nice-to-have / branchenspezifisch

## Beleg-Evidence

- UI-Screenshots (ID/Dateiname)
- Playwright-Trace/Video
- Flow-ID aus UI-Explorer JSON
- API-Responses/Schemas (falls vorhanden)

---

## 1. Supplier Lifecycle & Stammdaten

### PROC-SUP-01 Lieferantenstamm

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Lieferant anlegen/Ã¤ndern/sperren/archivieren
- Adressen, Ansprechpartner, Bankdaten, Steuerinfos
- Lieferantengruppen, Klassifikationen

**Evidence:** Supplier-Create/Edit UI

**Akzeptanz:**
- Pflichtfelder + Dublettencheck + Historie

---

### PROC-SUP-02 Lieferantenbewertung

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Kriterien: QualitÃ¤t, Termintreue, Preis, Service
- Scores + Trends, Sperr-/Freigabelogik

**Evidence:** Supplier-Score UI/Report

**Akzeptanz:**
- Bewertung wirkt auf Auswahl/Workflows

---

### PROC-SUP-03 Compliance / Dokumente

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Zertifikate, RahmenvertrÃ¤ge, NDA, ESG
- GÃ¼ltigkeit/Erinnerungen

**Evidence:** Supplier-Docs UI

**Akzeptanz:**
- Ablauf lÃ¶st Hinweis/Sperre aus

---

## 2. Bedarf / Requisition-to-Order

### PROC-REQ-01 Bedarfsmeldung (Purchase Requisition)

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Bedarf erfassen (Artikel/Service/Projekt)
- Mengen, Termin, Kostenstelle/Projekt
- Status: Entwurf â†’ Freigabe â†’ Bestellung

**Evidence:** Requisition-Flow

**Akzeptanz:**
- Bedarf erzeugt prÃ¼fbaren Vorgang

---

### PROC-REQ-02 Bedarfsgenehmigung

**PrioritÃ¤t:** MUSS/SOLL je Unternehmen

**Inhalt:**
- Freigabe nach Betrag/Warengruppe/Kostenstelle
- Vertretung/Eskalation

**Evidence:** Approval-UI

**Akzeptanz:**
- Ohne Freigabe keine Bestellung

---

### PROC-REQ-03 Katalog / Guided Buying

**PrioritÃ¤t:** KANN/SOLL

**Inhalt:**
- interne Kataloge, Punchout
- gefÃ¼hrte Auswahl

**Evidence:** Catalog-UI

**Akzeptanz:**
- Requisition aus Katalog mÃ¶glich

---

## 3. Sourcing / RFQ / Angebotsvergleich

### PROC-RFQ-01 Anfrage / RFQ

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Lieferanten auswÃ¤hlen, RFQ versenden
- Positionen, Spezifikationen, Fristen

**Evidence:** RFQ-Create/Send

**Akzeptanz:**
- RFQ-Status nachvollziehbar

---

### PROC-RFQ-02 Lieferantenangebote / Bids

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Angebote erfassen/importieren
- Preise, Lieferzeiten, Nebenbedingungen

**Evidence:** Bid-UI

**Akzeptanz:**
- Mehrere Angebote pro RFQ mÃ¶glich

---

### PROC-RFQ-03 Angebotsvergleich / Award

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Vergleichsmatrix Preis/Leadtime/Score
- Entscheidungsdoku

**Evidence:** Comparison-UI

**Akzeptanz:**
- Award erzeugt Vorschlag fÃ¼r Bestellung

---

### PROC-CTR-01 RahmenvertrÃ¤ge

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Vertragslaufzeit, Kontingente, Preise
- Abrufe gegen Vertrag

**Evidence:** Contract-UI

**Akzeptanz:**
- Order referenziert Vertrag

---

## 4. Bestellung / Purchase Order Management

### PROC-PO-01 Bestellung (PO) erstellen

**PrioritÃ¤t:** MUSS

**Inhalt:**
- PO aus Bedarf/RFQ/Vertrag oder direkt
- Positionen, Lieferadresse, Incoterms, Zahlungsbedingungen

**Evidence:** PO-Create-Flow

**Akzeptanz:**
- PO hat eindeutige Nummer, Status

---

### PROC-PO-02 PO-Ã„nderungen & Storno

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Change-Log, Versionierung
- Genehmigungslogik bei Ã„nderungen

**Evidence:** PO-Change-Flow

**Akzeptanz:**
- Jede Ã„nderung auditierbar

---

### PROC-PO-03 PO-Kommunikation

**PrioritÃ¤t:** SOLL

**Inhalt:**
- PO-Dokumente (PDF/Email/Portal)
- Sprachen/Branding

**Evidence:** PO-Print/Send

**Akzeptanz:**
- Lieferant erhÃ¤lt korrekte PO

---

### PROC-PO-04 Bestellabrufe / LieferplÃ¤ne

**PrioritÃ¤t:** KANN/SOLL

**Inhalt:**
- Abrufe gegen Kontrakte
- Lieferplan/Release-Logik

**Evidence:** Schedule-UI

**Akzeptanz:**
- Abrufe reduzieren Kontingent

---

## 5. Wareneingang / Service Entry (Receipt-to-Verify)

### PROC-GR-01 Wareneingang

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Eingang buchen gegen PO
- Teil-/Restmengen, Backorder
- QualitÃ¤tsprÃ¼fung optional

**Evidence:** GR-Flow

**Akzeptanz:**
- GR erzeugt Lagerbewegung + Status

---

### PROC-GR-02 Retouren an Lieferant

**PrioritÃ¤t:** SOLL

**Inhalt:**
- RÃ¼cksendung, GrÃ¼nde, Gutschriftbezug

**Evidence:** Return-Flow

**Akzeptanz:**
- RÃ¼ckgabe korrigiert Lager/FiBU

---

### PROC-SE-01 Leistungsnachweis (Service Entry Sheet)

**PrioritÃ¤t:** SOLL (MUSS wenn Services in Scope)

**Inhalt:**
- Leistungen erfassen, prÃ¼fen, freigeben

**Evidence:** SES-Flow

**Akzeptanz:**
- SES Voraussetzung fÃ¼r Rechnung

---

## 6. RechnungsprÃ¼fung / Invoice-to-Pay

### PROC-IV-01 Eingangsrechnung

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Rechnung erfassen/importieren (PDF/OCR/API)
- Steuer, Kontierung, Anlagebezug

**Evidence:** Invoice-Create-Flow

**Akzeptanz:**
- Rechnung erzeugt AP-OP

---

### PROC-IV-02 2/3-Wege-Abgleich (PO-GR-IV)

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Abgleich Menge/Preis/Toleranzen
- Blockierung bei Abweichungen

**Evidence:** Match-UI

**Akzeptanz:**
- Abweichungen werden begrÃ¼ndet/gelÃ¶st

---

### PROC-IV-03 Rechnungsfreigabe

**PrioritÃ¤t:** MUSS/SOLL

**Inhalt:**
- Freigabe nach Toleranzen/Betrag/Warengruppe
- Eskalation/Vertretung

**Evidence:** Approval-Flow

**Akzeptanz:**
- Ohne Freigabe keine Zahlung

---

### PROC-PAY-01 ZahlungslÃ¤ufe

**PrioritÃ¤t:** MUSS (wenn AP-Zahlung in Scope)

**Inhalt:**
- SEPA Export, Zahlungsstatus, Skonto

**Evidence:** Payment-Run UI

**Akzeptanz:**
- Zahlung gleicht OP aus

---

### PROC-PAY-02 Lieferantengutschriften / Belastungen

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Credit Memo, Debit Memo, Verrechnung

**Evidence:** Memo-Flow

**Akzeptanz:**
- Korrekte FiBU-Buchung

---

## 7. Reporting & Kontrolle

### PROC-REP-01 Standardreports Einkauf

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Offene Bestellungen, Spend-Analyse
- Lieferantenperformance
- Toleranz-/Abweichungsreports

**Evidence:** Dashboards/Reports

**Akzeptanz:**
- Filter, Drilldown, Export

---

### PROC-REP-02 Belegkette / Audit Trail

**PrioritÃ¤t:** SOLL

**Inhalt:**
- Bedarf â†’ RFQ â†’ PO â†’ GR/SES â†’ IV â†’ Pay

**Evidence:** Drilldown-Trace

**Akzeptanz:**
- lÃ¼ckenlose Nachvollziehbarkeit

---

## 8. Rollen, Berechtigungen, Workflows

### PROC-AUTH-01 Rollenmodell Einkauf

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Bedarfsersteller, Genehmiger, EinkÃ¤ufer, Wareneingang, AP, Admin

**Evidence:** Role-Setup

**Akzeptanz:**
- RBAC verhindert unberechtigte Aktionen

---

### PROC-AUTH-02 Workflow-Regeln

**PrioritÃ¤t:** MUSS/SOLL

**Inhalt:**
- Freigaben, Toleranzen, Eskalation

**Evidence:** Workflow-UI

**Akzeptanz:**
- Regeln sind konfigurierbar

---

## 9. Schnittstellen & Integrationen

### PROC-INT-01 API / Import / Export

**PrioritÃ¤t:** MUSS

**Inhalt:**
- Supplier/Item/PO/GR/IV
- CSV/Excel/API/Webhooks

**Evidence:** Import-UI, API-Docs

**Akzeptanz:**
- Datenrundtrip mÃ¶glich

---

### PROC-INT-02 EDI / Lieferantenportal

**PrioritÃ¤t:** KANN/SOLL je Branche

**Inhalt:**
- ORDERS, ORDRSP, DESADV, INVOIC
- Portal-Self-Service

**Evidence:** EDI/Portal-Flows

**Akzeptanz:**
- Statusmapping sauber

---

### PROC-INT-03 Katalog/Punchout

**PrioritÃ¤t:** KANN

**Inhalt:**
- OCI/cXML Punchout, Preis-Sync

**Evidence:** Punchout-UI

**Akzeptanz:**
- Requisition aus Punchout mÃ¶glich

---

## Zusammenfassung

**Gesamt Capabilities:** 28
**MUSS:** 12
**SOLL:** 13
**KANN:** 3

**NÃ¤chste Schritte:**
1. GAP-Analyse durchfÃ¼hren (Status: Yes/Partial/No)
2. Evidence sammeln (Screenshots, Flows, API-Docs)
3. GAP-Matrix aktualisieren (`gap/matrix.csv`)
4. Implementierungsplan erstellen



