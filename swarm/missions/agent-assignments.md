# Agenten-Zuordnung - 124 Capabilities

**Datum:** 2025-01-27  
**Status:** Final  
**Zweck:** Detaillierte Capability-Zuordnung zu Agenten

---

## 📊 Übersicht

| Agent | Domain | Capabilities | Priorität |
|-------|--------|--------------|-----------|
| **Agent-1** | Finance/FiBU | 33 | P0: 4, P1: 7, P2-P3: 22 |
| **Agent-2** | Procurement | 28 | P0: 4, P1: 4, P2-P3: 20 |
| **Agent-3** | Sales/CRM | 63 | P0: Top, P1: Top, P2-P3: Rest |
| **Agent-4** | Infrastructure | Cross-Domain | Alle Phasen |

---

## 💰 Agent-1: Finance & Accounting (33 Capabilities)

### P0 - Kritisch (4 Capabilities)
- **FIBU-AR-03:** Zahlungseingänge & Matching
- **FIBU-AP-02:** Eingangsrechnungen
- **FIBU-GL-05:** Periodensteuerung
- **FIBU-COMP-01:** GoBD / Audit Trail UI

### P1 - Hoch (7 Capabilities)
- **FIBU-GL-01:** Kontenplan & Kontenstamm
- **FIBU-GL-02:** Belegprinzip & Nummernkreise
- **FIBU-AR-01:** Debitorenstamm
- **FIBU-AR-05:** OP-Verwaltung & Ausgleich
- **FIBU-AP-01:** Kreditorenstamm
- **FIBU-AP-04:** Zahlungsläufe / SEPA
- **FIBU-AP-05:** OP-Verwaltung & Ausgleich

### P2 - Mittel (13 Capabilities)
- **FIBU-GL-04:** Sammel-/Massenbuchungen
- **FIBU-GL-06:** Fremdwährung & Wechselkurse
- **FIBU-GL-07:** Automatische Buchungsschemata
- **FIBU-AR-04:** Mahnwesen / Dunning
- **FIBU-AP-03:** Prüf-/Freigabeworkflow
- **FIBU-BNK-01:** Bankkontenstamm
- **FIBU-BNK-02:** Kontoauszugsimport
- **FIBU-BNK-03:** Automatisches Matching
- **FIBU-BNK-04:** Bankabstimmung
- **FIBU-TAX-01:** Steuerschlüssel-System
- **FIBU-TAX-02:** USt-Voranmeldung / ZM / OSS
- **FIBU-TAX-03:** E-Rechnung
- **FIBU-CLS-02:** Nebenbuch-Abstimmung

### P3 - Niedrig (9 Capabilities)
- **FIBU-GL-08:** Kostenrechnung-Integrationspunkte
- **FIBU-FA-01 bis FIBU-FA-05:** Anlagen (5)
- **FIBU-CLS-01:** Abschlusschecklisten
- **FIBU-CLS-03:** Abgrenzungen/Rückstellungen
- **FIBU-REP-02:** Drilldown & Analyse
- **FIBU-IC-01 bis FIBU-IC-02:** Intercompany (2)

---

## 🛒 Agent-2: Procurement & Supply Chain (28 Capabilities)

### P0 - Kritisch (4 Capabilities)
- **PROC-GR-01:** Wareneingang
- **PROC-IV-02:** 2/3-Wege-Abgleich
- **PROC-PO-02:** PO-Änderungen & Storno
- **PROC-REQ-01:** Bedarfsmeldung vervollständigen

### P1 - Hoch (4 Capabilities)
- **PROC-SUP-01:** Lieferantenstamm
- **PROC-PO-01:** Bestellung erstellen
- **PROC-IV-01:** Eingangsrechnung
- **PROC-PAY-01:** Zahlungsläufe

### P2 - Mittel (9 Capabilities)
- **PROC-SUP-02:** Lieferantenbewertung
- **PROC-SUP-03:** Compliance / Dokumente
- **PROC-REQ-02:** Bedarfsgenehmigung
- **PROC-RFQ-01:** Anfrage / RFQ
- **PROC-RFQ-02:** Lieferantenangebote / Bids
- **PROC-RFQ-03:** Angebotsvergleich / Award
- **PROC-CTR-01:** Rahmenverträge
- **PROC-IV-03:** Rechnungsfreigabe
- **PROC-PAY-02:** Gutschriften/Belastungen

### P3 - Niedrig (11 Capabilities)
- **PROC-REQ-03:** Katalog / Guided Buying
- **PROC-PO-03:** PO-Kommunikation
- **PROC-PO-04:** Bestellabrufe / Lieferpläne
- **PROC-GR-02:** Retouren an Lieferant
- **PROC-SE-01:** Service Entry Sheet
- **PROC-REP-01:** Standardreports Einkauf
- **PROC-REP-02:** Belegkette / Audit Trail
- **PROC-AUTH-01:** Rollenmodell Einkauf
- **PROC-AUTH-02:** Workflow-Regeln
- **PROC-INT-02:** EDI / Lieferantenportal
- **PROC-INT-03:** Katalog / Punchout

---

## 📊 Agent-3: Sales & CRM (63 Capabilities)

### Sales (31 Capabilities)
**P0 - Kritisch:**
- Top kritische Gaps aus `gaps-sales.md`

**P1 - Hoch:**
- Sales wichtige Gaps

**P2-P3 - Mittel/Niedrig:**
- Restliche Sales Capabilities

### CRM/Marketing (32 Capabilities)
**P0 - Kritisch:**
- **CRM-OPP-01:** Opportunities / Deals
- **CRM-CNS-01:** Opt-in/Opt-out & Consent Log
- **CRM-CNS-02:** DSGVO-Funktionen

**P1 - Hoch:**
- **MKT-SEG-01:** Segmente & Zielgruppen
- **CRM-LED-03:** Lead-Routing / Zuweisung
- **CRM-REP-01:** Standard-CRM-Reports

**P2-P3 - Mittel/Niedrig:**
- Restliche CRM/Marketing Capabilities

---

## 🔧 Agent-4: Infrastructure & Integration

### Cross-Domain Features
- **Workflow-Engine:** Vervollständigung für alle Domains
- **RBAC/Rollen-System:** Vervollständigung
- **Reporting-Infrastructure:** Cross-Domain Reporting
- **API-Gateway:** Integrationen
- **EDI-Integrationen:** EDI für Procurement/Sales
- **Performance-Optimierung:** System-weit
- **Monitoring & Observability:** System-weit

### Support für andere Agenten
- **Agent-1 Support:**
  - Bankimport-Infrastructure
  - Payment-Match-Engine Basis
  - Audit-Trail-Infrastructure

- **Agent-2 Support:**
  - Abgleich-Engine
  - Change-Log/Versionierung
  - Inventory-Integration

- **Agent-3 Support:**
  - CRM-Infrastructure
  - Marketing-Automation-Engine
  - Sales-Pipeline-Infrastructure

---

## 🔄 Dependencies & Koordination

### Agent-1 ↔ Agent-4
- **Bankimport:** Agent-4 stellt Infrastructure, Agent-1 implementiert UI
- **Payment-Match:** Agent-4 stellt Engine, Agent-1 implementiert UI
- **Audit-Trail:** Agent-4 stellt Backend, Agent-1 implementiert UI

### Agent-2 ↔ Agent-4
- **Abgleich-Engine:** Agent-4 stellt Engine, Agent-2 implementiert UI
- **Change-Log:** Agent-4 stellt System, Agent-2 nutzt es
- **Inventory-Integration:** Agent-4 koordiniert, Agent-2 implementiert

### Agent-2 ↔ Agent-1
- **Eingangsrechnungen:** Agent-1 implementiert, Agent-2 nutzt es
- **Zahlungsläufe:** Agent-1 implementiert, Agent-2 nutzt es

### Agent-3 ↔ Agent-4
- **Workflow-Engine:** Agent-4 stellt Engine, Agent-3 nutzt es
- **RBAC:** Agent-4 stellt System, Agent-3 nutzt es

---

## 📅 Implementierungs-Reihenfolge

### Phase 1 (P0) - Sprint 1-8
1. **Sprint 1-2:** Agent-1 (Finance P0) + Agent-4 (Infrastructure)
2. **Sprint 3-4:** Agent-1 (Finance P0) + Agent-2 (Procurement P0 Start) + Agent-4
3. **Sprint 5-7:** Agent-2 (Procurement P0) + Agent-4
4. **Sprint 8:** Agent-2 (Procurement P0 Finalisierung)

### Phase 2 (P1) - Sprint 9-16
**Parallele Arbeit:**
- Agent-1: Finance P1
- Agent-2: Procurement P1
- Agent-3: Sales/CRM P1
- Agent-4: Infrastructure P1

### Phase 3 (P2-P3) - Sprint 17-52
**Parallele Arbeit:**
- Agent-1: Finance P2-P3
- Agent-2: Procurement P2-P3
- Agent-3: Sales/CRM P2-P3
- Agent-4: Infrastructure P2-P3

---

**Letzte Aktualisierung:** 2025-01-27

