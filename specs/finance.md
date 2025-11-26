***REMOVED*** Test Plan - Finance Module

**Erstellt:** 2025-11-24  
**Basis:** UI-Explorer Handoff `ui-explorer-finance-2025-11-24T08-51-19.344194.md`  
**Status:** Draft

***REMOVED******REMOVED*** Test Scope

Basierend auf der UI-Exploration wurden folgende Flows identifiziert:

1. **Finance Module Navigation**
2. **Invoices List View**
3. **Create Invoice Form**

***REMOVED******REMOVED*** Test Objectives

- ✅ Verifizieren, dass Finance-Modul erreichbar ist
- ✅ Verifizieren, dass Invoices-Liste korrekt angezeigt wird
- ✅ Verifizieren, dass Create Invoice Formular funktioniert
- ✅ Verifizieren, dass Navigation zwischen Bereichen funktioniert

***REMOVED******REMOVED*** Test Cases

***REMOVED******REMOVED******REMOVED*** TC-FIN-001: Finance Module Navigation

**Priority:** High  
**Type:** Navigation Test

**Preconditions:**
- User ist auf Dashboard (`http://localhost:3000/`)
- Login ist nicht aktiviert (kein Login erforderlich)

**Test Steps:**
1. Navigiere zu Finance-Modul
   - Erwartung: Finance-Modul wird angezeigt
   - Screenshot: `20251124_095102_03_finance_module.png`

**Expected Results:**
- Finance-Modul ist erreichbar
- Finance-Übersichtsseite wird korrekt angezeigt

**Evidence:**
- Screenshot: `evidence/screenshots/finance/20251124_095102_03_finance_module.png`
- URL: `http://localhost:3000/crm/betriebsprofile` (Hinweis: URL zeigt CRM, möglicher Routing-Fehler)

---

***REMOVED******REMOVED******REMOVED*** TC-FIN-002: Invoices List View

**Priority:** High  
**Type:** List View Test

**Preconditions:**
- User ist im Finance-Modul

**Test Steps:**
1. Navigiere zu Invoices-Liste
   - Erwartung: Invoices-Liste wird angezeigt
   - Screenshot: `20251124_095105_04_invoices_list.png`

**Expected Results:**
- Invoices-Liste ist erreichbar
- Liste zeigt Rechnungen an (falls vorhanden)
- Suchfunktion ist verfügbar

**Evidence:**
- Screenshot: `evidence/screenshots/finance/20251124_095105_04_invoices_list.png`
- URL: `http://localhost:3000/sales/invoice` (Hinweis: URL zeigt Sales, möglicher Routing-Fehler)

**Findings:**
- Formular-Analyse zeigt 1 Feld: "Suche Belegnummer, Konto, Text..." (Suchfeld)

---

***REMOVED******REMOVED******REMOVED*** TC-FIN-003: Create Invoice Form

**Priority:** High  
**Type:** Form Test

**Preconditions:**
- User ist auf Invoices-Liste

**Test Steps:**
1. Klicke auf "Neue Rechnung" oder "Create Invoice" Button
2. Prüfe, ob Formular geöffnet wird
   - Erwartung: Create Invoice Formular wird angezeigt
   - Screenshot: `20251124_095108_05_create_invoice_form.png`

**Expected Results:**
- Create Invoice Formular ist erreichbar
- Formular zeigt alle notwendigen Felder
- Formular kann ausgefüllt werden

**Evidence:**
- Screenshot: `evidence/screenshots/finance/20251124_095108_05_create_invoice_form.png`
- URL: `http://localhost:3000/finance/bookings/new`

**Findings:**
- Formular-Analyse zeigt nur 1 Feld (Suchfeld)
- Möglicherweise unvollständiges Formular oder Formular noch nicht vollständig geladen

---

***REMOVED******REMOVED******REMOVED*** TC-FIN-004: Dashboard Navigation

**Priority:** Medium  
**Type:** Navigation Test

**Preconditions:**
- User startet auf Homepage

**Test Steps:**
1. Navigiere zu Homepage (`http://localhost:3000/`)
2. Prüfe, ob Dashboard angezeigt wird
   - Erwartung: Dashboard wird angezeigt
   - Screenshot: `20251124_095059_02_dashboard.png`

**Expected Results:**
- Dashboard ist erreichbar
- Dashboard zeigt relevante Informationen

**Evidence:**
- Screenshot: `evidence/screenshots/finance/20251124_095059_02_dashboard.png`
- URL: `http://localhost:3000/`

---

***REMOVED******REMOVED*** Test Data Requirements

- Keine speziellen Test-Daten erforderlich (Login nicht aktiviert)
- Falls Invoices vorhanden sein sollen, müssen diese vorher erstellt werden

***REMOVED******REMOVED*** Test Environment

- **Base URL:** `http://localhost:3000`
- **Browser:** Chromium (Playwright)
- **Viewport:** 1920x1080
- **Login:** Nicht erforderlich (nicht aktiviert)

***REMOVED******REMOVED*** Test Execution Strategy

***REMOVED******REMOVED******REMOVED*** Smoke Tests (Quick Check)
- TC-FIN-001: Finance Module Navigation
- TC-FIN-002: Invoices List View

***REMOVED******REMOVED******REMOVED*** Full Tests
- Alle Test Cases (TC-FIN-001 bis TC-FIN-004)

***REMOVED******REMOVED*** Known Issues / Findings

1. **Routing-Inkonsistenz:**
   - Finance-Modul URL zeigt `http://localhost:3000/crm/betriebsprofile` (sollte Finance sein)
   - Invoices URL zeigt `http://localhost:3000/sales/invoice` (sollte Finance sein)
   - **Action:** Routing prüfen und korrigieren

2. **Create Invoice Formular:**
   - Formular-Analyse zeigt nur 1 Feld (Suchfeld)
   - Möglicherweise unvollständiges Formular
   - **Action:** Formular-Felder prüfen und vervollständigen

3. **Payments-Bereich:**
   - Exploration versuchte Payments zu finden, aber kein Screenshot erstellt
   - **Action:** Payments-Bereich explizit testen

***REMOVED******REMOVED*** Acceptance Criteria

- [ ] Alle Test Cases können erfolgreich ausgeführt werden
- [ ] Navigation funktioniert korrekt
- [ ] Invoices-Liste zeigt Daten an
- [ ] Create Invoice Formular ist vollständig funktionsfähig
- [ ] Routing-Inkonsistenzen sind behoben

***REMOVED******REMOVED*** Next Steps

1. **Test-Generator:** Erstelle Playwright-Tests basierend auf diesem Plan
2. **Test-Healer:** Führe Tests aus und behebe flaky/failing Tests
3. **Feature-Engineer:** Behebe identifizierte Issues (Routing, Formular)

***REMOVED******REMOVED*** References

- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- JSON Summary: `evidence/screenshots/finance/finance_mission_2025-11-24T08-51-19.344194.json`
- Screenshots: `evidence/screenshots/finance/`

