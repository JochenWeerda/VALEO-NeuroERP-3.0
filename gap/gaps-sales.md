# GAP-Liste Verkauf (Order-to-Cash) – Valero NeuroERP

Stand: 2025-11-24

Scope: Verkauf / CRM / Quote-to-Cash / Fulfillment / Billing-to-Cash

Evidence-Quelle:

- /evidence/screenshots/sales/*

- /swarm/handoffs/ui-explorer-sales-*.md

- Playwright traces/videos

Referenz:

- gap/capability-model-sales.md

- gap/matrix-sales.csv

---

## 1) Priorisierungslogik

### 1.1 Bewertungsdimensionen (1–5)

**A) Business Impact (BI)**  

1 = geringe Auswirkung / selten genutzt  

3 = merkliche Auswirkung auf Umsatz/Prozess  

5 = kritisch für Kernumsatz / Kundenzufriedenheit / Cashflow  

**B) Pflichtgrad (PF)**  

MUSS = 5  

SOLL = 3  

KANN = 1  

**C) Risiko / Compliance (RC)**  

1 = kein Risiko  

3 = mittleres Risiko (z.B. vertraglich, steuerlich indirekt)  

5 = hohes Risiko (z.B. gesetzliche Pflicht, Audit-Lücke)  

**D) Implementierungsaufwand (IA)**  

1 = sehr klein (Konfig / Verdrahtung / UI-Feld)  

3 = mittel (Workflow, Adapter, 1–2 Screens + Logik)  

5 = groß (Neues Modul / tiefe Logik / viele Abhängigkeiten)

### 1.2 Score-Formel

**Prioritäts-Score (PS) = (BI × PF × RC) / IA**

- Ergebnis typischerweise 1–125  

- Je höher, desto früher umsetzen.  

- Bei Gleichstand: zuerst **MUSS**, dann niedrigere IA.

---

## 2) Zusammenfassung

### 2.1 TOP-Gaps nach Score

| Rank | Capability_ID | Gap-Titel | Status | PS | Lösungstyp | Owner |
|---|---|---|---|---:|---|---|
| 1 | SALES-CRM-02 | Kunden-/Kontaktstamm (Sales-Sicht) | No | 10.0 | C |  |
| 2 | SALES-PRD-01 | Produktkatalog Verkauf | No | 10.0 | C |  |
| 3 | SALES-PRC-01 | Preislisten & Preisfindung | No | 10.0 | C |  |
| 4 | SALES-PRC-03 | Steuern im Verkauf | No | 10.0 | C |  |
| 5 | SALES-QTN-01 | Angebotsmanagement | Partial | 10.0 | C | Frontend |
| 6 | SALES-ORD-01 | Auftragserfassung (Sales Order) | Partial | 10.0 | C | Frontend |
| 7 | SALES-ORD-02 | Auftragsänderung & Storno | No | 10.0 | C |  |
| 8 | SALES-DLV-01 | Lieferabwicklung | Partial | 10.0 | C | Frontend |
| 9 | SALES-BIL-01 | Rechnungsstellung | Partial | 10.0 | C | Frontend |
| 10 | SALES-PAY-01 | Zahlungseingänge & Ausgleich | No | 10.0 | C |  |

### 2.2 Abdeckung (Snapshot)

- Yes: 0  

- Partial: 4  

- No: 27  

- Gesamt: 31

---

## 3) GAP-Details (Solution-Cards)

> Jede Card ist ein umsetzbares Ticket-Paket.  

> Evidence MUSS immer Screenshot/Flow/Trace referenzieren.

---

### CARD SALES-002 — Kunden-/Kontaktstamm (Sales-Sicht)

**Capability_ID(s):** SALES-CRM-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-006 — Produktkatalog Verkauf

**Capability_ID(s):** SALES-PRD-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-007 — Preislisten & Preisfindung

**Capability_ID(s):** SALES-PRC-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-009 — Steuern im Verkauf

**Capability_ID(s):** SALES-PRC-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-010 — Angebotsmanagement

**Capability_ID(s):** SALES-QTN-01  

**Status in NeuroERP:** Partial  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): `20251124_131338_04_offers_list.png`, `20251124_131341_05_create_offer_form.png`  

- Flow(s): `SALES-QTN-01`, `SALES-QTN-02`  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

Angebotsliste und Create-Formular vorhanden, aber vollständige Funktionalität (Versionierung, Ablauf, Konvertierung) unklar

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-013 — Auftragserfassung (Sales Order)

**Capability_ID(s):** SALES-ORD-01  

**Status in NeuroERP:** Partial  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): `20251124_131349_06_orders_list.png`, `20251124_131352_07_create_order_form.png`  

- Flow(s): `SALES-ORD-01`, `SALES-ORD-02`  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

Orders-Liste und Create-Formular vorhanden, aber vollständige Funktionalität (Validierung, Status-Workflow, Bestätigung) unklar

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-014 — Auftragsänderung & Storno

**Capability_ID(s):** SALES-ORD-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-015 — Lieferabwicklung

**Capability_ID(s):** SALES-DLV-01  

**Status in NeuroERP:** Partial  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): `20251124_131359_08_deliveries_list.png`  

- Flow(s): `SALES-DLV-01`  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

Deliveries-Liste vorhanden, aber vollständige Funktionalität (Teil-/Restlieferungen, Lieferstatus, Tracking) unklar

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-018 — Rechnungsstellung

**Capability_ID(s):** SALES-BIL-01  

**Status in NeuroERP:** Partial  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): `20251124_131406_09_invoices_list.png`  

- Flow(s): `SALES-BIL-01`  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

Invoices-Liste vorhanden, aber vollständige Funktionalität (Rechnungserstellung aus Lieferung/Auftrag, Validierung, Versand) unklar

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-021 — Zahlungseingänge & Ausgleich

**Capability_ID(s):** SALES-PAY-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-024 — Standard-Reports

**Capability_ID(s):** SALES-REP-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-027 — Rollenmodell Sales

**Capability_ID(s):** SALES-AUTH-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-029 — API / Import / Export

**Capability_ID(s):** SALES-INT-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** MUSS  

**Score-Berechnung:**  

- BI = 3  

- PF = 5  

- RC = 2  

- IA = 3  

**PS = (3×5×2)/3 = 10.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-001 — Lead-Erfassung & Quellen

**Capability_ID(s):** SALES-CRM-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-003 — Opportunities / Pipeline

**Capability_ID(s):** SALES-CRM-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-004 — Aktivitäten & Aufgaben

**Capability_ID(s):** SALES-CRM-04  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-008 — Rabatte/Gutschriften/Bonifikationen

**Capability_ID(s):** SALES-PRC-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-011 — Angebotsdokumente

**Capability_ID(s):** SALES-QTN-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-016 — Versandarten & Tracking

**Capability_ID(s):** SALES-DLV-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-019 — E-Rechnung & Formate

**Capability_ID(s):** SALES-BIL-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-020 — Forderungsmanagement / Mahnung

**Capability_ID(s):** SALES-COL-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-022 — Retourenprozess (RMA)

**Capability_ID(s):** SALES-RMA-01  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-023 — Reklamation & Ersatz

**Capability_ID(s):** SALES-RMA-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-025 — Drilldown & Belegkette

**Capability_ID(s):** SALES-REP-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-028 — Freigabeworkflows

**Capability_ID(s):** SALES-AUTH-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** SOLL  

**Score-Berechnung:**  

- BI = 3  

- PF = 3  

- RC = 2  

- IA = 3  

**PS = (3×3×2)/3 = 6.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-005 — Forecasting & Ziele

**Capability_ID(s):** SALES-CRM-05  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-012 — Angebotsvergleich & Verhandlungsstatus

**Capability_ID(s):** SALES-QTN-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-017 — Dropship / Direktversand

**Capability_ID(s):** SALES-DLV-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-026 — Sales Analytics / KPI

**Capability_ID(s):** SALES-REP-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-030 — EDI / B2B Integration

**Capability_ID(s):** SALES-INT-02  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

### CARD SALES-031 — Shop / POS / Marktplätze

**Capability_ID(s):** SALES-INT-03  

**Status in NeuroERP:** No  

**Priorität (MUSS/SOLL/KANN):** KANN  

**Score-Berechnung:**  

- BI = 3  

- PF = 1  

- RC = 2  

- IA = 3  

**PS = (3×1×2)/3 = 2.0**

**Ist-Beobachtung (Evidence-basiert)**  

- Screenshot(s): *keine*  

- Flow(s): *keine*  

- Trace(s): *keine*  

- Kurze Beschreibung der aktuellen UI/Logik: *Zu ergänzen*

**Gap-Beschreibung (gegen Referenzmodell)**  

*Zu ergänzen - siehe capability-model-sales.md*

**Zielverhalten / Akzeptanzkriterien**  

- *Zu definieren*

**Lösungstyp**  

- C = neues Feature/Modul

**Technische Umsetzung (Pflichten-Skizze)**  

*Zu ergänzen:*
- UI: neue Screens/Felder/Validierungen  
- Workflow/RBAC: Rollen, Freigaben  
- Backend/API: Endpoints, Regeln, Datenmodell  
- Migration/Seeds (falls nötig)

**Playwright-Nachweis**  

*Zu ergänzen:*
- Neue/angepasste Tests: `tests/e2e/sales/<...>.spec.ts`  
- Testfälle (IDs) aus Plan: `<spec refs>`

**Abhängigkeiten**  

*keine*

**Rollout/DoD**  

- Test grün  

- Evidence aktualisiert  

- Dok/Training falls relevant

---

## 4) Nächste Schritte

1. UI-Explorer durch Verkaufsmodule jagen (Lead → Quote → Order → Delivery → Invoice → Payment).  

2. Evidence in matrix-sales.csv eintragen.  

3. Aus matrix automatisch Cards befüllen (Agent).  

4. Feature-Backlog + Umsetzung nach Score.

---

## 5) Agent-Loop Integration

**ROLE: Feature-Engineer**

Input:

- gap/gaps-sales.md

- gap/matrix-sales.csv

- evidence + traces

Task:

1. Nimm die höchste Card (Rank 1).

2. Erstelle Pflichten-Umsetzung:

   - Konfig/Workflow/Code

3. Ergänze/Erstelle Playwright-Tests.

4. Evidence aktualisieren.

5. PR/Branch erstellen.

Output:

- Code + Tests

- Evidence

- Update matrix-sales.csv (Status -> Yes)

- Notiz /swarm/handoffs/feature-sales-top1.md

