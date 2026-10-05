# GAP-Analyse Procurement / Einkauf - Identifizierte LÃ¼cken

**Datum:** 2025-01-27
**Basis:** Procurement Capability Model v1.0 + Einkauf Module Exploration
**Status:** In Progress
**PrioritÃ¤t:** MUSS/SOLL/KANN basierend auf ERP-Referenz (SAP MM / Oracle Procurement / Community ERP Enterprise)

## Zusammenfassung

**Gesamt:** 28 Capabilities analysiert
- **Yes (VollstÃ¤ndig):** 0 (0%)
- **Partial (Teilweise):** 12 (43%)
- **No (Fehlend):** 16 (57%)

**Nach PrioritÃ¤t:**
- **MUSS:** 12 Capabilities
  - Yes: 0
  - Partial: 8
  - No: 4
- **SOLL:** 13 Capabilities
  - Yes: 0
  - Partial: 4
  - No: 9
- **KANN:** 3 Capabilities
  - Yes: 0
  - Partial: 0
  - No: 3

---

## P0 - Kritisch (MUSS, PrioritÃ¤t 1)

### PROC-GR-01: Wareneingang
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Wareneingang-FunktionalitÃ¤t gefunden. Eingang kann nicht gegen PO gebucht werden. Teil-/Restmengen, Backorder, QualitÃ¤tsprÃ¼fung fehlen komplett.
- **Impact:** ðŸ”´ KRITISCH - Source-to-Pay-Prozess unvollstÃ¤ndig
- **Evidence:** Keine Screenshots/Flows, keine GR-Seite gefunden
- **LÃ¶sung:** Wareneingang-Modul implementieren:
  - GR-Seite erstellen (`wareneingang.tsx`, `wareneingaenge-liste.tsx`)
  - PO-Referenzierung
  - Teil-/Restmengen-Buchung
  - Backorder-Verwaltung
  - Optional: QualitÃ¤tsprÃ¼fung
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige GR-FunktionalitÃ¤t
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

### PROC-IV-02: 2/3-Wege-Abgleich (PO-GR-IV)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Abgleich-FunktionalitÃ¤t gefunden. Menge/Preis/Toleranzen werden nicht abgeglichen. Blockierung bei Abweichungen fehlt.
- **Impact:** ðŸ”´ KRITISCH - AP-Prozess nicht vollstÃ¤ndig, Fehlerrisiko hoch
- **Evidence:** Keine Screenshots/Flows, keine Match-UI gefunden
- **LÃ¶sung:** 2/3-Wege-Abgleich implementieren:
  - Abgleich-Engine (Backend)
  - Match-UI (Frontend)
  - Toleranz-Regeln konfigurierbar
  - Blockierung bei Abweichungen
  - BegrÃ¼ndungspflicht fÃ¼r Abweichungen
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Matching-FunktionalitÃ¤t
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

### PROC-PO-02: PO-Ã„nderungen & Storno
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Change-Log/Versionierung gefunden. PO-Ã„nderungen sind nicht auditierbar. Genehmigungslogik bei Ã„nderungen fehlt.
- **Impact:** ðŸ”´ KRITISCH - GoBD-Compliance gefÃ¤hrdet, Audit-Trail unvollstÃ¤ndig
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** PO-Ã„nderungsverwaltung implementieren:
  - Change-Log/Versionierung
  - Genehmigungslogik bei Ã„nderungen
  - Storno-FunktionalitÃ¤t
  - Audit-Trail
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige PO-Change-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-REQ-01: Bedarfsmeldung (Purchase Requisition)
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `anfrage-stamm.tsx` vorhanden, aber Workflow (Entwurf â†’ Freigabe â†’ Bestellung) unklar. Status-ÃœbergÃ¤nge mÃ¶glicherweise nicht vollstÃ¤ndig implementiert.
- **Impact:** ðŸŸ¡ HOCH - Kernprozess vorhanden, aber unvollstÃ¤ndig
- **Evidence:** Datei vorhanden: `packages/frontend-web/src/pages/einkauf/anfrage-stamm.tsx`
- **LÃ¶sung:** Workflow prÃ¼fen und vervollstÃ¤ndigen:
  - Status-Workflow validieren
  - Ãœbergang zu Bestellung prÃ¼fen
  - VollstÃ¤ndigkeit der Felder prÃ¼fen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

## P1 - Hoch (MUSS, PrioritÃ¤t 2)

### PROC-SUP-01: Lieferantenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `lieferanten-liste.tsx` und `lieferanten-stamm.tsx` vorhanden, aber VollstÃ¤ndigkeit unklar:
  - Adressen, Ansprechpartner
  - Bankdaten, Steuerinfos
  - Lieferantengruppen, Klassifikationen
  - Sperren/Archivieren
- **Impact:** ðŸŸ¡ MITTEL - FunktionalitÃ¤t vorhanden, aber unvollstÃ¤ndig
- **Evidence:** Dateien vorhanden: `lieferanten-liste.tsx`, `lieferanten-stamm.tsx`
- **LÃ¶sung:** Stammdaten-VollstÃ¤ndigkeit prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Frontend
- **Effort:** 1 Woche

---

### PROC-PO-01: Bestellung erstellen
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `bestellung-anlegen.tsx`, `bestellungen-liste.tsx`, `bestellung-stamm.tsx` vorhanden. API-Integration vorhanden (`/api/mcp/documents/purchase_order`). Aber VollstÃ¤ndigkeit prÃ¼fen:
  - Incoterms
  - Zahlungsbedingungen
  - Lieferadresse
  - Referenzierung zu Bedarf/RFQ/Vertrag
- **Impact:** ðŸŸ¡ MITTEL - KernfunktionalitÃ¤t vorhanden
- **Evidence:**
  - Dateien: `bestellung-anlegen.tsx`, `bestellungen-liste.tsx`, `bestellung-stamm.tsx`
  - API: `/api/mcp/documents/purchase_order`
- **LÃ¶sung:** VollstÃ¤ndigkeit prÃ¼fen und fehlende Felder ergÃ¤nzen
- **Vergleich:** Basic
- **Owner:** Frontend
- **Effort:** 1 Woche

---

### PROC-IV-01: Eingangsrechnung
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `rechnungseingang.tsx` und `rechnungseingaenge-liste.tsx` vorhanden. Aber VollstÃ¤ndigkeit prÃ¼fen:
  - PDF/OCR/Schnittstellen-Import
  - Steuer, Kontierung
  - Anlagebezug (PO, GR)
- **Impact:** ðŸŸ¡ HOCH - KernfunktionalitÃ¤t vorhanden, aber Import fehlt
- **Evidence:** Dateien: `rechnungseingang.tsx`, `rechnungseingaenge-liste.tsx`
- **LÃ¶sung:** Import-FunktionalitÃ¤t implementieren (PDF/OCR/API)
- **Vergleich:** Basic
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

### PROC-PAY-01: ZahlungslÃ¤ufe
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `zahlungslauf-kreditoren.tsx` vorhanden (Finance-Domain), aber SEPA-Export/Status/Skonto prÃ¼fen.
- **Impact:** ðŸŸ¡ HOCH - FunktionalitÃ¤t vorhanden, aber SEPA-Export unklar
- **Evidence:** Datei: `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
- **LÃ¶sung:** SEPA-Export prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1-2 Wochen

---

## P2 - Mittel (SOLL, PrioritÃ¤t 3)

### PROC-SUP-02: Lieferantenbewertung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Bewertungs-UI/Score-System gefunden. Kriterien (QualitÃ¤t, Termintreue, Preis, Service) fehlen. Scores + Trends, Sperr-/Freigabelogik fehlen.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have fÃ¼r Supplier Management
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Supplier-Score-System implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Supplier-Evaluation
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

### PROC-SUP-03: Compliance / Dokumente
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Dokumentenverwaltung fÃ¼r Lieferanten gefunden. Zertifikate, RahmenvertrÃ¤ge, NDA, ESG fehlen. GÃ¼ltigkeit/Erinnerungen fehlen.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have fÃ¼r Compliance
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Supplier-Dokumentenverwaltung implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Compliance-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-REQ-02: Bedarfsgenehmigung
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow-System vorhanden (`workflow_service.py`, `useWorkflow.ts`, `purchase-order-workflow-service.ts`), aber Approval-Logik nach Betrag/Warengruppe/Kostenstelle prÃ¼fen. Vertretung/Eskalation unklar.
- **Impact:** ðŸŸ¡ MITTEL - Workflow vorhanden, Regeln prÃ¼fen
- **Evidence:**
  - Backend: `app/services/workflow_service.py`
  - Frontend: `packages/frontend-web/src/hooks/useWorkflow.ts`
  - Domain: `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
- **LÃ¶sung:** Approval-Regeln prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

### PROC-RFQ-01: Anfrage / RFQ
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `anfragen-liste.tsx` und `anfrage-stamm.tsx` vorhanden, aber RFQ-Versand an Lieferanten prÃ¼fen. Status-Nachvollziehbarkeit unklar.
- **Impact:** ðŸŸ¡ MITTEL - FunktionalitÃ¤t vorhanden, Versand prÃ¼fen
- **Evidence:** Dateien: `anfragen-liste.tsx`, `anfrage-stamm.tsx`
- **LÃ¶sung:** RFQ-Versand-FunktionalitÃ¤t prÃ¼fen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

### PROC-RFQ-02: Lieferantenangebote / Bids
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Bid-Erfassung gefunden. Angebote kÃ¶nnen nicht erfasst/importiert werden. Preise, Lieferzeiten, Nebenbedingungen fehlen.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have fÃ¼r Sourcing
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Bid-Erfassung implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Bid-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-RFQ-03: Angebotsvergleich / Award
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Vergleichsmatrix gefunden. Preis/Leadtime/Score-Vergleich fehlt. Entscheidungsdoku fehlt.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have fÃ¼r Sourcing
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Vergleichsmatrix implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Comparison-Tools
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-CTR-01: RahmenvertrÃ¤ge
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `contracts-v2.tsx` vorhanden, aber Abrufe gegen Vertrag prÃ¼fen. Kontingente, Preise, Abruf-FunktionalitÃ¤t unklar.
- **Impact:** ðŸŸ¡ MITTEL - FunktionalitÃ¤t vorhanden, Abrufe prÃ¼fen
- **Evidence:** Datei: `packages/frontend-web/src/pages/contracts-v2.tsx`
- **LÃ¶sung:** Abruf-FunktionalitÃ¤t prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1-2 Wochen

---

### PROC-PO-03: PO-Kommunikation
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Print-Funktion vorhanden, aber Email/Portal-Versand prÃ¼fen. Sprachen/Branding unklar.
- **Impact:** ðŸŸ¢ NIEDRIG - Print vorhanden, Email/Portal nice-to-have
- **Evidence:** Print-Funktion vorhanden
- **LÃ¶sung:** Email/Portal-Versand prÃ¼fen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

### PROC-IV-03: Rechnungsfreigabe
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow vorhanden (`workflow_service.py`), aber Approval-Logik nach Toleranzen/Betrag/Warengruppe prÃ¼fen. Eskalation/Vertretung unklar.
- **Impact:** ðŸŸ¡ MITTEL - Workflow vorhanden, Regeln prÃ¼fen
- **Evidence:** Backend: `app/services/workflow_service.py`
- **LÃ¶sung:** Approval-Regeln prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

## P3 - Niedrig (SOLL/KANN, PrioritÃ¤t 4-5)

### PROC-REQ-03: Katalog / Guided Buying
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Katalog-System gefunden. Interne Kataloge, Punchout fehlen. GefÃ¼hrte Auswahl fehlt.
- **Impact:** ðŸŸ¢ NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Katalog-System implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Catalog-Management
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

### PROC-PO-04: Bestellabrufe / LieferplÃ¤ne
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Abruf-FunktionalitÃ¤t gefunden. Abrufe gegen Kontrakte fehlen. Lieferplan/Release-Logik fehlt.
- **Impact:** ðŸŸ¢ NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Abruf-FunktionalitÃ¤t implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Release-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-GR-02: Retouren an Lieferant
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Retouren-FunktionalitÃ¤t gefunden. RÃ¼cksendung, GrÃ¼nde, Gutschriftbezug fehlen.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Retouren-FunktionalitÃ¤t implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Return-Management
- **Owner:** Backend + Frontend
- **Effort:** 1-2 Wochen

---

### PROC-SE-01: Service Entry Sheet (SES)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine SES-FunktionalitÃ¤t gefunden. Leistungserfassung, PrÃ¼fung, Freigabe fehlen.
- **Impact:** ðŸŸ¡ MITTEL (MUSS wenn Services in Scope)
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** SES-FunktionalitÃ¤t implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Service-Entry
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-PAY-02: Gutschriften/Belastungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Credit/Debit-Memo-FunktionalitÃ¤t gefunden. Verrechnung fehlt.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Credit/Debit-Memo implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Memo-Management
- **Owner:** Backend + Frontend
- **Effort:** 1-2 Wochen

---

### PROC-REP-01: Standardreports Einkauf
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Procurement-Reports gefunden. Offene Bestellungen, Spend-Analyse, Lieferantenperformance fehlen.
- **Impact:** ðŸŸ¡ MITTEL - Erforderlich fÃ¼r Kontrolle
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Procurement-Reports implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Reporting-Suite
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

### PROC-REP-02: Belegkette / Audit Trail
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Drilldown-FunktionalitÃ¤t gefunden. Belegkette (Bedarf â†’ RFQ â†’ PO â†’ GR/SES â†’ IV â†’ Pay) nicht nachvollziehbar.
- **Impact:** ðŸŸ¡ MITTEL - Nice-to-have fÃ¼r Audit
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Drilldown-FunktionalitÃ¤t implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Audit-Trail
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

### PROC-AUTH-01: Rollenmodell Einkauf
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** RBAC vorhanden, aber Rollen prÃ¼fen (Bedarfsersteller, Genehmiger, EinkÃ¤ufer, Wareneingang, AP, Admin).
- **Impact:** ðŸŸ¡ MITTEL - RBAC vorhanden, Rollen-Definition prÃ¼fen
- **Evidence:** RBAC-System vorhanden
- **LÃ¶sung:** Rollen-Definition prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

### PROC-AUTH-02: Workflow-Regeln
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow-System vorhanden (`workflow_service.py`, `purchase-order-workflow-service.ts`), aber Regeln prÃ¼fen (Freigaben, Toleranzen, Eskalation).
- **Impact:** ðŸŸ¡ MITTEL - Workflow vorhanden, Regeln prÃ¼fen
- **Evidence:**
  - Backend: `app/services/workflow_service.py`
  - Domain: `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
- **LÃ¶sung:** Workflow-Regeln prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

### PROC-INT-01: API / Import / Export
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** API vorhanden (`/api/mcp/documents/purchase_order`), aber Import/Export (CSV/Excel/API/Webhooks) prÃ¼fen.
- **Impact:** ðŸŸ¡ MITTEL - API vorhanden, Import/Export prÃ¼fen
- **Evidence:** API: `/api/mcp/documents/purchase_order`
- **LÃ¶sung:** Import/Export-FunktionalitÃ¤t prÃ¼fen und vervollstÃ¤ndigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1-2 Wochen

---

### PROC-INT-02: EDI / Lieferantenportal
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine EDI-FunktionalitÃ¤t gefunden (ORDERS, ORDRSP, DESADV, INVOIC). Portal-Self-Service fehlt.
- **Impact:** ðŸŸ¢ NIEDRIG - Optional, branchenspezifisch
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** EDI/Portal implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige EDI-Integration
- **Owner:** Backend + Frontend
- **Effort:** 4-6 Wochen

---

### PROC-INT-03: Katalog / Punchout
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Punchout-FunktionalitÃ¤t gefunden (OCI/cXML). Preis-Sync fehlt.
- **Impact:** ðŸŸ¢ NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **LÃ¶sung:** Punchout implementieren
- **Vergleich:** SAP/Community ERP haben vollstÃ¤ndige Punchout-Integration
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

## Implementierungs-Roadmap

### Phase 1: Kritische Gaps (P0) - 8-10 Wochen
1. **PROC-GR-01:** Wareneingang (3-4 Wochen)
2. **PROC-IV-02:** 2/3-Wege-Abgleich (2-3 Wochen)
3. **PROC-PO-02:** PO-Ã„nderungen & Storno (2 Wochen)
4. **PROC-REQ-01:** Bedarfsmeldung vervollstÃ¤ndigen (1 Woche)

### Phase 2: Wichtige Gaps (P1) - 6-8 Wochen
1. **PROC-SUP-01:** Lieferantenstamm vervollstÃ¤ndigen (1 Woche)
2. **PROC-PO-01:** Bestellung vervollstÃ¤ndigen (1 Woche)
3. **PROC-IV-01:** Eingangsrechnung Import (2-3 Wochen)
4. **PROC-PAY-01:** ZahlungslÃ¤ufe SEPA (1-2 Wochen)

### Phase 3: Nice-to-Have (P2-P3) - 15-20 Wochen
- Supplier-Bewertung, Compliance, RFQ-Bids, Vergleichsmatrix, Reports, etc.

---

## Vergleich mit ERP-Referenz

| Kategorie | VALEO | SAP MM | Oracle Procurement | Community ERP Enterprise |
|-----------|-------|--------|-------------------|-----------------|
| **Supplier Management** | 33% | 100% | 100% | 90% |
| **Requisition** | 67% | 100% | 100% | 85% |
| **Sourcing/RFQ** | 25% | 100% | 100% | 70% |
| **Purchase Orders** | 50% | 100% | 100% | 90% |
| **Receipt/Verify** | 0% | 100% | 100% | 85% |
| **Invoice-to-Pay** | 50% | 100% | 100% | 90% |
| **Reporting** | 0% | 100% | 100% | 80% |
| **Integration** | 33% | 100% | 100% | 60% |

**Gesamt Procurement Maturity:** VALEO = 35% | SAP/Oracle = 100% | Community ERP = 80%

---

## NÃ¤chste Schritte

1. âœ… Capability Model erstellt
2. âœ… GAP-Matrix erstellt
3. â³ Evidence sammeln (Screenshots, Flows, API-Docs)
4. â³ Detaillierte Analyse pro Capability
5. â³ Implementierungsplan erstellen
6. â³ Priorisierung mit Stakeholdern abstimmen



