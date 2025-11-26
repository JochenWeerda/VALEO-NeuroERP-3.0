# Implementierungs-Roadmap - VALEO NeuroERP GAP-Schließung

**Datum:** 2025-01-27  
**Status:** Planung  
**Zweck:** Detaillierte Roadmap zur Schließung kritischer Gaps

---

## 📊 Executive Summary

**Gesamt Capabilities:** 124 analysiert  
**Kritische Gaps (P0):** 12-15 Capabilities  
**Geschätzter Gesamtaufwand:** 52-70 Wochen (~12-18 Monate)  
**Priorität:** Kritische Gaps zuerst, dann wichtige, dann nice-to-have

---

## 🎯 Phase 1: Kritische Gaps (P0) - 12-16 Wochen

### Sprint 1-2: Finance - Zahlungseingänge & Matching (4-6 Wochen)

#### Task 1.1: Payment-Match-UI (2-3 Wochen)
- **Capability:** FIBU-AR-03
- **Owner:** Frontend + Backend
- **Tasks:**
  - [ ] Payment-Match-Seite erstellen (`zahlungseingaenge-match.tsx`)
  - [ ] Match-Engine Backend implementieren
  - [ ] Bankimport-Funktionalität (CAMT/MT940/CSV)
  - [ ] Automatisches Matching (Regel-basiert)
  - [ ] Manuelles Matching-UI
  - [ ] OP-Status-Update nach Matching
- **Dependencies:** Bankimport-Funktionalität
- **Acceptance Criteria:**
  - Zahlungseingänge können importiert werden
  - Automatisches Matching funktioniert
  - OP-Status wird korrekt aktualisiert
  - Audit-Trail vorhanden

#### Task 1.2: Eingangsrechnungen vervollständigen (2-3 Wochen)
- **Capability:** FIBU-AP-02
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] Eingangsrechnungen-Seite prüfen (`rechnungseingang.tsx` vorhanden)
  - [ ] Backend-API vervollständigen (`ap_invoices.py` vorhanden)
  - [ ] GL-Buchung/OP-Erzeugung implementieren
  - [ ] Workflow-Integration prüfen
- **Dependencies:** Workflow-System
- **Acceptance Criteria:**
  - Eingangsrechnungen können vollständig erfasst werden
  - GL-Buchung wird automatisch erzeugt
  - OP wird korrekt angelegt

---

### Sprint 3-4: Finance - Periodensteuerung & Audit Trail (3-4 Wochen)

#### Task 2.1: Periodensteuerung (2 Wochen)
- **Capability:** FIBU-GL-05
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] Perioden-Admin-Screen erstellen (`perioden-verwaltung.tsx`)
  - [ ] Perioden-Sperrlogik implementieren
  - [ ] Buchungen in gesperrter Periode blockieren
  - [ ] Perioden-Status-Management
- **Dependencies:** GL-System
- **Acceptance Criteria:**
  - Perioden können verwaltet werden
  - Sperrlogik funktioniert korrekt
  - Buchungen in gesperrter Periode werden blockiert
  - GoBD-Compliance gewährleistet

#### Task 2.2: GoBD / Audit Trail UI (1-2 Wochen)
- **Capability:** FIBU-COMP-01
- **Owner:** Frontend
- **Tasks:**
  - [ ] Audit-View-UI erstellen (`audit-trail-view.tsx`)
  - [ ] Historie/Logs-Anzeige implementieren
  - [ ] Filter nach User/Zeit/Entity
  - [ ] Export-Funktionalität
- **Dependencies:** Backend Audit-Trail vorhanden
- **Acceptance Criteria:**
  - Jede Änderung ist mit User+Zeit sichtbar
  - Historie kann gefiltert werden
  - Export funktioniert

---

### Sprint 5-7: Procurement - Wareneingang & Abgleich (7-9 Wochen)

#### Task 3.1: Wareneingang (3-4 Wochen)
- **Capability:** PROC-GR-01
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] Wareneingang-Seite erstellen (`wareneingang.tsx`, `wareneingaenge-liste.tsx`)
  - [ ] PO-Referenzierung implementieren
  - [ ] Teil-/Restmengen-Buchung
  - [ ] Backorder-Verwaltung
  - [ ] Lagerbewegung-Integration
  - [ ] Optional: Qualitätsprüfung
- **Dependencies:** PO-System, Inventory-System
- **Acceptance Criteria:**
  - Wareneingang kann gegen PO gebucht werden
  - Teil-/Restmengen werden korrekt behandelt
  - Lagerbewegung wird erzeugt
  - Backorder wird verwaltet

#### Task 3.2: 2/3-Wege-Abgleich (2-3 Wochen)
- **Capability:** PROC-IV-02
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] Abgleich-Engine implementieren (Backend)
  - [ ] Match-UI erstellen (`rechnung-abgleich.tsx`)
  - [ ] Toleranz-Regeln konfigurierbar machen
  - [ ] Blockierung bei Abweichungen
  - [ ] Begründungspflicht für Abweichungen
- **Dependencies:** PO-System, GR-System, Invoice-System
- **Acceptance Criteria:**
  - PO-GR-IV Abgleich funktioniert automatisch
  - Toleranzen werden berücksichtigt
  - Abweichungen werden blockiert
  - Begründung ist erforderlich

#### Task 3.3: PO-Änderungen & Storno (2 Wochen)
- **Capability:** PROC-PO-02
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] Change-Log/Versionierung implementieren
  - [ ] Genehmigungslogik bei Änderungen
  - [ ] Storno-Funktionalität
  - [ ] Audit-Trail für Änderungen
- **Dependencies:** PO-System, Workflow-System
- **Acceptance Criteria:**
  - Jede PO-Änderung ist auditierbar
  - Genehmigung bei Änderungen erforderlich
  - Storno funktioniert korrekt

---

### Sprint 8: Procurement - Bedarfsmeldung vervollständigen (1 Woche)

#### Task 4.1: Bedarfsmeldung Workflow (1 Woche)
- **Capability:** PROC-REQ-01
- **Owner:** Frontend + Backend
- **Tasks:**
  - [ ] Workflow-Status-Übergänge prüfen
  - [ ] Übergang zu Bestellung implementieren
  - [ ] Vollständigkeit der Felder prüfen
- **Dependencies:** Workflow-System, PO-System
- **Acceptance Criteria:**
  - Workflow funktioniert vollständig
  - Übergang zu Bestellung funktioniert

---

## 🎯 Phase 2: Wichtige Gaps (P1) - 10-14 Wochen

### Sprint 9-10: Finance - Wichtige Gaps (4-6 Wochen)

#### Task 5.1: Debitorenstamm vervollständigen (1 Woche)
- **Capability:** FIBU-AR-01
- **Owner:** Frontend
- **Tasks:**
  - [ ] Stammdaten-Vollständigkeit prüfen
  - [ ] Adressen, USt-ID, Kreditlimit ergänzen
  - [ ] Dublettencheck implementieren

#### Task 5.2: Kreditorenstamm vervollständigen (1 Woche)
- **Capability:** FIBU-AP-01
- **Owner:** Frontend
- **Tasks:**
  - [ ] Stammdaten-Vollständigkeit prüfen
  - [ ] Bankdaten, IBAN-Validierung ergänzen

#### Task 5.3: Zahlungsläufe SEPA vervollständigen (1-2 Wochen)
- **Capability:** FIBU-AP-04, PROC-PAY-01
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] SEPA XML Export prüfen
  - [ ] Status-Verwaltung
  - [ ] Rückläufer-Verarbeitung

#### Task 5.4: OP-Verwaltung vervollständigen (1-2 Wochen)
- **Capability:** FIBU-AR-05, FIBU-AP-05
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] OP-Liste für Kreditoren
  - [ ] Ausgleich/Verrechnung
  - [ ] Audit-Trail

---

### Sprint 11-12: Procurement - Wichtige Gaps (4-6 Wochen)

#### Task 6.1: Lieferantenstamm vervollständigen (1 Woche)
- **Capability:** PROC-SUP-01
- **Owner:** Frontend
- **Tasks:**
  - [ ] Bankdaten, Steuerinfos ergänzen
  - [ ] Lieferantengruppen, Klassifikationen
  - [ ] Sperren/Archivieren

#### Task 6.2: Bestellung vervollständigen (1 Woche)
- **Capability:** PROC-PO-01
- **Owner:** Frontend
- **Tasks:**
  - [ ] Incoterms ergänzen
  - [ ] Referenzierung zu Bedarf/RFQ/Vertrag

#### Task 6.3: Eingangsrechnung Import (2-3 Wochen)
- **Capability:** PROC-IV-01
- **Owner:** Backend + Frontend
- **Tasks:**
  - [ ] PDF-Import implementieren
  - [ ] OCR-Integration
  - [ ] API-Import
  - [ ] Steuer, Kontierung automatisch

#### Task 6.4: Bedarfsgenehmigung vervollständigen (1 Woche)
- **Capability:** PROC-REQ-02
- **Owner:** Backend
- **Tasks:**
  - [ ] Approval-Regeln nach Betrag/Warengruppe/Kostenstelle
  - [ ] Vertretung/Eskalation

---

## 🎯 Phase 3: Nice-to-Have (P2-P3) - 30-40 Wochen

### Finance Nice-to-Have (18 Capabilities)
- Sammel-/Massenbuchungen
- Fremdwährung & Wechselkurse
- Automatische Buchungsschemata
- Kostenrechnung-Integrationspunkte
- Mahnwesen vervollständigen
- Prüf-/Freigabeworkflow
- Automatisches Matching
- USt-Voranmeldung Export
- E-Rechnung
- Abschlusschecklisten
- Nebenbuch-Abstimmung
- Abgrenzungen/Rückstellungen
- Reporting vervollständigen
- Drilldown & Analyse
- Intercompany
- etc.

### Procurement Nice-to-Have (12 Capabilities)
- Lieferantenbewertung
- Compliance / Dokumente
- Katalog / Guided Buying
- Lieferantenangebote / Bids
- Angebotsvergleich / Award
- PO-Kommunikation Email/Portal
- Bestellabrufe / Lieferpläne
- Retouren an Lieferant
- Service Entry Sheet
- Gutschriften/Belastungen
- Standardreports Einkauf
- Belegkette / Audit Trail
- EDI / Lieferantenportal
- Katalog / Punchout

---

## 📅 Sprint-Planung

### Q1 2025 (Wochen 1-12)
- **Sprint 1-4:** Finance kritische Gaps (Zahlungseingänge, Eingangsrechnungen, Periodensteuerung, Audit Trail)
- **Sprint 5-7:** Procurement kritische Gaps (Wareneingang, Abgleich, PO-Änderungen)

### Q2 2025 (Wochen 13-24)
- **Sprint 8:** Procurement Bedarfsmeldung
- **Sprint 9-12:** Finance wichtige Gaps
- **Sprint 13-16:** Procurement wichtige Gaps

### Q3-Q4 2025 (Wochen 25-52)
- **Sprint 17-52:** Nice-to-Have Features
- **Sales & CRM Gaps** (wenn priorisiert)
- **Weitere Domains** (Inventory, Production, Quality, etc.)

---

## 👥 Team-Zuordnung

### Frontend-Team
- Payment-Match-UI
- Audit-Trail-UI
- Wareneingang-UI
- Abgleich-UI
- Stammdaten-Vervollständigung
- Perioden-Verwaltung

### Backend-Team
- Payment-Match-Engine
- Bankimport
- Perioden-Sperrlogik
- Wareneingang-Backend
- Abgleich-Engine
- PO-Change-Management
- SEPA-Export

### Full-Stack-Team
- Eingangsrechnungen
- Workflow-Integration
- Invoice-Import (PDF/OCR)
- Approval-Regeln

---

## 📊 Erfolgs-Metriken

### Phase 1 (P0)
- **Ziel:** 12-15 kritische Gaps geschlossen
- **Maturity Finance:** 48% → 65%
- **Maturity Procurement:** 35% → 60%
- **Gesamt Maturity:** 38% → 50%

### Phase 2 (P1)
- **Ziel:** 15-20 wichtige Gaps geschlossen
- **Maturity Finance:** 65% → 75%
- **Maturity Procurement:** 60% → 70%
- **Gesamt Maturity:** 50% → 65%

### Phase 3 (P2-P3)
- **Ziel:** Nice-to-Have Features
- **Maturity Finance:** 75% → 85%
- **Maturity Procurement:** 70% → 80%
- **Gesamt Maturity:** 65% → 80%

---

## 🚨 Risiken & Mitigation

### Risiko 1: Abhängigkeiten zwischen Domains
- **Mitigation:** Klare Dependency-Map, frühe Integration-Tests

### Risiko 2: Workflow-System unvollständig
- **Mitigation:** Workflow-System zuerst vervollständigen

### Risiko 3: Inventory-System Integration
- **Mitigation:** Inventory-API früh definieren, Mock-Implementierung

### Risiko 4: Scope Creep
- **Mitigation:** Strikte Priorisierung, Change-Request-Prozess

---

## 📝 Nächste Schritte

1. ✅ Roadmap erstellt
2. ⏳ Mit Stakeholdern abstimmen
3. ⏳ Sprint-Planung detaillieren
4. ⏳ Team-Zuordnung finalisieren
5. ⏳ Evidence-Sammlung starten
6. ⏳ Sprint 1 starten

---

**Letzte Aktualisierung:** 2025-01-27

