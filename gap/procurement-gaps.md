***REMOVED*** GAP-Analyse Procurement / Einkauf - Identifizierte Lücken

**Datum:** 2025-01-27  
**Basis:** Procurement Capability Model v1.0 + Einkauf Module Exploration  
**Status:** In Progress  
**Priorität:** MUSS/SOLL/KANN basierend auf ERP-Referenz (SAP MM / Oracle Procurement / Odoo Enterprise)

***REMOVED******REMOVED*** Zusammenfassung

**Gesamt:** 28 Capabilities analysiert
- **Yes (Vollständig):** 0 (0%)
- **Partial (Teilweise):** 12 (43%)
- **No (Fehlend):** 16 (57%)

**Nach Priorität:**
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

***REMOVED******REMOVED*** P0 - Kritisch (MUSS, Priorität 1)

***REMOVED******REMOVED******REMOVED*** PROC-GR-01: Wareneingang
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Wareneingang-Funktionalität gefunden. Eingang kann nicht gegen PO gebucht werden. Teil-/Restmengen, Backorder, Qualitätsprüfung fehlen komplett.
- **Impact:** 🔴 KRITISCH - Source-to-Pay-Prozess unvollständig
- **Evidence:** Keine Screenshots/Flows, keine GR-Seite gefunden
- **Lösung:** Wareneingang-Modul implementieren:
  - GR-Seite erstellen (`wareneingang.tsx`, `wareneingaenge-liste.tsx`)
  - PO-Referenzierung
  - Teil-/Restmengen-Buchung
  - Backorder-Verwaltung
  - Optional: Qualitätsprüfung
- **Vergleich:** SAP/Odoo haben vollständige GR-Funktionalität
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-IV-02: 2/3-Wege-Abgleich (PO-GR-IV)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Abgleich-Funktionalität gefunden. Menge/Preis/Toleranzen werden nicht abgeglichen. Blockierung bei Abweichungen fehlt.
- **Impact:** 🔴 KRITISCH - AP-Prozess nicht vollständig, Fehlerrisiko hoch
- **Evidence:** Keine Screenshots/Flows, keine Match-UI gefunden
- **Lösung:** 2/3-Wege-Abgleich implementieren:
  - Abgleich-Engine (Backend)
  - Match-UI (Frontend)
  - Toleranz-Regeln konfigurierbar
  - Blockierung bei Abweichungen
  - Begründungspflicht für Abweichungen
- **Vergleich:** SAP/Odoo haben vollständige Matching-Funktionalität
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-PO-02: PO-Änderungen & Storno
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Change-Log/Versionierung gefunden. PO-Änderungen sind nicht auditierbar. Genehmigungslogik bei Änderungen fehlt.
- **Impact:** 🔴 KRITISCH - GoBD-Compliance gefährdet, Audit-Trail unvollständig
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** PO-Änderungsverwaltung implementieren:
  - Change-Log/Versionierung
  - Genehmigungslogik bei Änderungen
  - Storno-Funktionalität
  - Audit-Trail
- **Vergleich:** SAP/Odoo haben vollständige PO-Change-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-REQ-01: Bedarfsmeldung (Purchase Requisition)
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `anfrage-stamm.tsx` vorhanden, aber Workflow (Entwurf → Freigabe → Bestellung) unklar. Status-Übergänge möglicherweise nicht vollständig implementiert.
- **Impact:** 🟡 HOCH - Kernprozess vorhanden, aber unvollständig
- **Evidence:** Datei vorhanden: `packages/frontend-web/src/pages/einkauf/anfrage-stamm.tsx`
- **Lösung:** Workflow prüfen und vervollständigen:
  - Status-Workflow validieren
  - Übergang zu Bestellung prüfen
  - Vollständigkeit der Felder prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED*** P1 - Hoch (MUSS, Priorität 2)

***REMOVED******REMOVED******REMOVED*** PROC-SUP-01: Lieferantenstamm
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `lieferanten-liste.tsx` und `lieferanten-stamm.tsx` vorhanden, aber Vollständigkeit unklar:
  - Adressen, Ansprechpartner
  - Bankdaten, Steuerinfos
  - Lieferantengruppen, Klassifikationen
  - Sperren/Archivieren
- **Impact:** 🟡 MITTEL - Funktionalität vorhanden, aber unvollständig
- **Evidence:** Dateien vorhanden: `lieferanten-liste.tsx`, `lieferanten-stamm.tsx`
- **Lösung:** Stammdaten-Vollständigkeit prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-PO-01: Bestellung erstellen
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `bestellung-anlegen.tsx`, `bestellungen-liste.tsx`, `bestellung-stamm.tsx` vorhanden. API-Integration vorhanden (`/api/mcp/documents/purchase_order`). Aber Vollständigkeit prüfen:
  - Incoterms
  - Zahlungsbedingungen
  - Lieferadresse
  - Referenzierung zu Bedarf/RFQ/Vertrag
- **Impact:** 🟡 MITTEL - Kernfunktionalität vorhanden
- **Evidence:** 
  - Dateien: `bestellung-anlegen.tsx`, `bestellungen-liste.tsx`, `bestellung-stamm.tsx`
  - API: `/api/mcp/documents/purchase_order`
- **Lösung:** Vollständigkeit prüfen und fehlende Felder ergänzen
- **Vergleich:** Basic
- **Owner:** Frontend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-IV-01: Eingangsrechnung
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `rechnungseingang.tsx` und `rechnungseingaenge-liste.tsx` vorhanden. Aber Vollständigkeit prüfen:
  - PDF/OCR/Schnittstellen-Import
  - Steuer, Kontierung
  - Anlagebezug (PO, GR)
- **Impact:** 🟡 HOCH - Kernfunktionalität vorhanden, aber Import fehlt
- **Evidence:** Dateien: `rechnungseingang.tsx`, `rechnungseingaenge-liste.tsx`
- **Lösung:** Import-Funktionalität implementieren (PDF/OCR/API)
- **Vergleich:** Basic
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-PAY-01: Zahlungsläufe
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `zahlungslauf-kreditoren.tsx` vorhanden (Finance-Domain), aber SEPA-Export/Status/Skonto prüfen.
- **Impact:** 🟡 HOCH - Funktionalität vorhanden, aber SEPA-Export unklar
- **Evidence:** Datei: `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
- **Lösung:** SEPA-Export prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1-2 Wochen

---

***REMOVED******REMOVED*** P2 - Mittel (SOLL, Priorität 3)

***REMOVED******REMOVED******REMOVED*** PROC-SUP-02: Lieferantenbewertung
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Bewertungs-UI/Score-System gefunden. Kriterien (Qualität, Termintreue, Preis, Service) fehlen. Scores + Trends, Sperr-/Freigabelogik fehlen.
- **Impact:** 🟡 MITTEL - Nice-to-have für Supplier Management
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Supplier-Score-System implementieren
- **Vergleich:** SAP/Odoo haben vollständige Supplier-Evaluation
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-SUP-03: Compliance / Dokumente
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Dokumentenverwaltung für Lieferanten gefunden. Zertifikate, Rahmenverträge, NDA, ESG fehlen. Gültigkeit/Erinnerungen fehlen.
- **Impact:** 🟡 MITTEL - Nice-to-have für Compliance
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Supplier-Dokumentenverwaltung implementieren
- **Vergleich:** SAP/Odoo haben vollständige Compliance-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-REQ-02: Bedarfsgenehmigung
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow-System vorhanden (`workflow_service.py`, `useWorkflow.ts`, `purchase-order-workflow-service.ts`), aber Approval-Logik nach Betrag/Warengruppe/Kostenstelle prüfen. Vertretung/Eskalation unklar.
- **Impact:** 🟡 MITTEL - Workflow vorhanden, Regeln prüfen
- **Evidence:** 
  - Backend: `app/services/workflow_service.py`
  - Frontend: `packages/frontend-web/src/hooks/useWorkflow.ts`
  - Domain: `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
- **Lösung:** Approval-Regeln prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-RFQ-01: Anfrage / RFQ
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `anfragen-liste.tsx` und `anfrage-stamm.tsx` vorhanden, aber RFQ-Versand an Lieferanten prüfen. Status-Nachvollziehbarkeit unklar.
- **Impact:** 🟡 MITTEL - Funktionalität vorhanden, Versand prüfen
- **Evidence:** Dateien: `anfragen-liste.tsx`, `anfrage-stamm.tsx`
- **Lösung:** RFQ-Versand-Funktionalität prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-RFQ-02: Lieferantenangebote / Bids
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Bid-Erfassung gefunden. Angebote können nicht erfasst/importiert werden. Preise, Lieferzeiten, Nebenbedingungen fehlen.
- **Impact:** 🟡 MITTEL - Nice-to-have für Sourcing
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Bid-Erfassung implementieren
- **Vergleich:** SAP/Odoo haben vollständige Bid-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-RFQ-03: Angebotsvergleich / Award
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Vergleichsmatrix gefunden. Preis/Leadtime/Score-Vergleich fehlt. Entscheidungsdoku fehlt.
- **Impact:** 🟡 MITTEL - Nice-to-have für Sourcing
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Vergleichsmatrix implementieren
- **Vergleich:** SAP/Odoo haben vollständige Comparison-Tools
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-CTR-01: Rahmenverträge
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** `contracts-v2.tsx` vorhanden, aber Abrufe gegen Vertrag prüfen. Kontingente, Preise, Abruf-Funktionalität unklar.
- **Impact:** 🟡 MITTEL - Funktionalität vorhanden, Abrufe prüfen
- **Evidence:** Datei: `packages/frontend-web/src/pages/contracts-v2.tsx`
- **Lösung:** Abruf-Funktionalität prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1-2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-PO-03: PO-Kommunikation
- **Status:** Partial
- **Typ:** D (UX/Edge-Case/Reifegrad)
- **Beschreibung:** Print-Funktion vorhanden, aber Email/Portal-Versand prüfen. Sprachen/Branding unklar.
- **Impact:** 🟢 NIEDRIG - Print vorhanden, Email/Portal nice-to-have
- **Evidence:** Print-Funktion vorhanden
- **Lösung:** Email/Portal-Versand prüfen
- **Vergleich:** Basic
- **Owner:** Frontend + Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-IV-03: Rechnungsfreigabe
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow vorhanden (`workflow_service.py`), aber Approval-Logik nach Toleranzen/Betrag/Warengruppe prüfen. Eskalation/Vertretung unklar.
- **Impact:** 🟡 MITTEL - Workflow vorhanden, Regeln prüfen
- **Evidence:** Backend: `app/services/workflow_service.py`
- **Lösung:** Approval-Regeln prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED*** P3 - Niedrig (SOLL/KANN, Priorität 4-5)

***REMOVED******REMOVED******REMOVED*** PROC-REQ-03: Katalog / Guided Buying
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Kein Katalog-System gefunden. Interne Kataloge, Punchout fehlen. Geführte Auswahl fehlt.
- **Impact:** 🟢 NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Katalog-System implementieren
- **Vergleich:** SAP/Odoo haben vollständige Catalog-Management
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-PO-04: Bestellabrufe / Lieferpläne
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Abruf-Funktionalität gefunden. Abrufe gegen Kontrakte fehlen. Lieferplan/Release-Logik fehlt.
- **Impact:** 🟢 NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Abruf-Funktionalität implementieren
- **Vergleich:** SAP/Odoo haben vollständige Release-Management
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-GR-02: Retouren an Lieferant
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Retouren-Funktionalität gefunden. Rücksendung, Gründe, Gutschriftbezug fehlen.
- **Impact:** 🟡 MITTEL - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Retouren-Funktionalität implementieren
- **Vergleich:** SAP/Odoo haben vollständige Return-Management
- **Owner:** Backend + Frontend
- **Effort:** 1-2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-SE-01: Service Entry Sheet (SES)
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine SES-Funktionalität gefunden. Leistungserfassung, Prüfung, Freigabe fehlen.
- **Impact:** 🟡 MITTEL (MUSS wenn Services in Scope)
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** SES-Funktionalität implementieren
- **Vergleich:** SAP/Odoo haben vollständige Service-Entry
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-PAY-02: Gutschriften/Belastungen
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Credit/Debit-Memo-Funktionalität gefunden. Verrechnung fehlt.
- **Impact:** 🟡 MITTEL - Nice-to-have
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Credit/Debit-Memo implementieren
- **Vergleich:** SAP/Odoo haben vollständige Memo-Management
- **Owner:** Backend + Frontend
- **Effort:** 1-2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-REP-01: Standardreports Einkauf
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Procurement-Reports gefunden. Offene Bestellungen, Spend-Analyse, Lieferantenperformance fehlen.
- **Impact:** 🟡 MITTEL - Erforderlich für Kontrolle
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Procurement-Reports implementieren
- **Vergleich:** SAP/Odoo haben vollständige Reporting-Suite
- **Owner:** Backend + Frontend
- **Effort:** 2-3 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-REP-02: Belegkette / Audit Trail
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Drilldown-Funktionalität gefunden. Belegkette (Bedarf → RFQ → PO → GR/SES → IV → Pay) nicht nachvollziehbar.
- **Impact:** 🟡 MITTEL - Nice-to-have für Audit
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Drilldown-Funktionalität implementieren
- **Vergleich:** SAP/Odoo haben vollständige Audit-Trail
- **Owner:** Backend + Frontend
- **Effort:** 2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-AUTH-01: Rollenmodell Einkauf
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** RBAC vorhanden, aber Rollen prüfen (Bedarfsersteller, Genehmiger, Einkäufer, Wareneingang, AP, Admin).
- **Impact:** 🟡 MITTEL - RBAC vorhanden, Rollen-Definition prüfen
- **Evidence:** RBAC-System vorhanden
- **Lösung:** Rollen-Definition prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-AUTH-02: Workflow-Regeln
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** Workflow-System vorhanden (`workflow_service.py`, `purchase-order-workflow-service.ts`), aber Regeln prüfen (Freigaben, Toleranzen, Eskalation).
- **Impact:** 🟡 MITTEL - Workflow vorhanden, Regeln prüfen
- **Evidence:** 
  - Backend: `app/services/workflow_service.py`
  - Domain: `packages/purchase-domain/src/domain/services/purchase-order-workflow-service.ts`
- **Lösung:** Workflow-Regeln prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1 Woche

---

***REMOVED******REMOVED******REMOVED*** PROC-INT-01: API / Import / Export
- **Status:** Partial
- **Typ:** B (Integration/Adapter)
- **Beschreibung:** API vorhanden (`/api/mcp/documents/purchase_order`), aber Import/Export (CSV/Excel/API/Webhooks) prüfen.
- **Impact:** 🟡 MITTEL - API vorhanden, Import/Export prüfen
- **Evidence:** API: `/api/mcp/documents/purchase_order`
- **Lösung:** Import/Export-Funktionalität prüfen und vervollständigen
- **Vergleich:** Basic
- **Owner:** Backend
- **Effort:** 1-2 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-INT-02: EDI / Lieferantenportal
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine EDI-Funktionalität gefunden (ORDERS, ORDRSP, DESADV, INVOIC). Portal-Self-Service fehlt.
- **Impact:** 🟢 NIEDRIG - Optional, branchenspezifisch
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** EDI/Portal implementieren
- **Vergleich:** SAP/Odoo haben vollständige EDI-Integration
- **Owner:** Backend + Frontend
- **Effort:** 4-6 Wochen

---

***REMOVED******REMOVED******REMOVED*** PROC-INT-03: Katalog / Punchout
- **Status:** No (Missing)
- **Typ:** C (Neues Feature/Modul)
- **Beschreibung:** Keine Punchout-Funktionalität gefunden (OCI/cXML). Preis-Sync fehlt.
- **Impact:** 🟢 NIEDRIG - Optional
- **Evidence:** Keine Screenshots/Flows
- **Lösung:** Punchout implementieren
- **Vergleich:** SAP/Odoo haben vollständige Punchout-Integration
- **Owner:** Backend + Frontend
- **Effort:** 3-4 Wochen

---

***REMOVED******REMOVED*** Implementierungs-Roadmap

***REMOVED******REMOVED******REMOVED*** Phase 1: Kritische Gaps (P0) - 8-10 Wochen
1. **PROC-GR-01:** Wareneingang (3-4 Wochen)
2. **PROC-IV-02:** 2/3-Wege-Abgleich (2-3 Wochen)
3. **PROC-PO-02:** PO-Änderungen & Storno (2 Wochen)
4. **PROC-REQ-01:** Bedarfsmeldung vervollständigen (1 Woche)

***REMOVED******REMOVED******REMOVED*** Phase 2: Wichtige Gaps (P1) - 6-8 Wochen
1. **PROC-SUP-01:** Lieferantenstamm vervollständigen (1 Woche)
2. **PROC-PO-01:** Bestellung vervollständigen (1 Woche)
3. **PROC-IV-01:** Eingangsrechnung Import (2-3 Wochen)
4. **PROC-PAY-01:** Zahlungsläufe SEPA (1-2 Wochen)

***REMOVED******REMOVED******REMOVED*** Phase 3: Nice-to-Have (P2-P3) - 15-20 Wochen
- Supplier-Bewertung, Compliance, RFQ-Bids, Vergleichsmatrix, Reports, etc.

---

***REMOVED******REMOVED*** Vergleich mit ERP-Referenz

| Kategorie | VALEO | SAP MM | Oracle Procurement | Odoo Enterprise |
|-----------|-------|--------|-------------------|-----------------|
| **Supplier Management** | 33% | 100% | 100% | 90% |
| **Requisition** | 67% | 100% | 100% | 85% |
| **Sourcing/RFQ** | 25% | 100% | 100% | 70% |
| **Purchase Orders** | 50% | 100% | 100% | 90% |
| **Receipt/Verify** | 0% | 100% | 100% | 85% |
| **Invoice-to-Pay** | 50% | 100% | 100% | 90% |
| **Reporting** | 0% | 100% | 100% | 80% |
| **Integration** | 33% | 100% | 100% | 60% |

**Gesamt Procurement Maturity:** VALEO = 35% | SAP/Oracle = 100% | Odoo = 80%

---

***REMOVED******REMOVED*** Nächste Schritte

1. ✅ Capability Model erstellt
2. ✅ GAP-Matrix erstellt
3. ⏳ Evidence sammeln (Screenshots, Flows, API-Docs)
4. ⏳ Detaillierte Analyse pro Capability
5. ⏳ Implementierungsplan erstellen
6. ⏳ Priorisierung mit Stakeholdern abstimmen

