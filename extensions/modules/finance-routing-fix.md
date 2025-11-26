# Feature Implementation Plan - Finance Routing Fix

**Erstellt:** 2025-11-24  
**Basis:** GAP-FIN-001 (Routing-Inkonsistenz Finance-Modul)  
**Status:** Planned  
**Priorität:** P0 (Kritisch)

## Problem

Finance-Modul zeigt falsche URLs:
- Finance-Modul URL: `http://localhost:3000/crm/betriebsprofile` (sollte `/finance` sein)
- Invoices URL: `http://localhost:3000/sales/invoice` (sollte `/finance/invoices` sein)

## Anforderungen

### Routing-Korrekturen

1. **Finance-Modul Übersicht**
   - URL: `/finance` (statt `/crm/betriebsprofile`)
   - Zeigt Finance-Modul Übersicht mit Navigation zu:
     - General Ledger
     - Accounts Receivable (Invoices)
     - Accounts Payable
     - Treasury
     - Tax

2. **Invoices-Liste**
   - URL: `/finance/invoices` (statt `/sales/invoice`)
   - Zeigt Liste der Rechnungen

3. **Create Invoice**
   - URL: `/finance/invoices/new` (statt `/finance/bookings/new`)
   - Zeigt Create Invoice Formular

## Implementierungsplan

### Phase 1: Routing-Definitionen (Priorität: Hoch)

1. **Frontend Routes**
   - `packages/frontend-web/src/app/route-aliases.json`
     - `/finance` → Finance-Modul Übersicht
     - `/finance/invoices` → Invoices-Liste
     - `/finance/invoices/new` → Create Invoice

2. **Auto-Routing**
   - Prüfe ob Auto-Routing korrekt funktioniert
   - Falls nicht, manuelle Routes in `App.tsx` hinzufügen

### Phase 2: Navigation-Komponenten (Priorität: Hoch)

1. **Finance-Modul Übersicht**
   - Erstelle `packages/frontend-web/src/pages/finance/index.tsx`
   - Zeigt Finance-Modul Übersicht mit Navigation

2. **Navigation-Links**
   - Korrigiere Links in Navigation-Menü
   - Stelle sicher, dass alle Finance-Links auf `/finance/*` zeigen

### Phase 3: Komponenten-Migration (Priorität: Mittel)

1. **Invoices-Liste**
   - Prüfe ob `packages/frontend-web/src/pages/sales/invoice.tsx` existiert
   - Falls ja, migriere zu `packages/frontend-web/src/pages/finance/invoices.tsx`
   - Falls nein, erstelle neue Komponente

2. **Create Invoice**
   - Prüfe ob `packages/frontend-web/src/pages/finance/bookings/new.tsx` existiert
   - Falls ja, migriere zu `packages/frontend-web/src/pages/finance/invoices/new.tsx`
   - Falls nein, erstelle neue Komponente

### Phase 4: Testing (Priorität: Hoch)

1. **Navigation Tests**
   - Teste Navigation zu `/finance`
   - Teste Navigation zu `/finance/invoices`
   - Teste Navigation zu `/finance/invoices/new`

2. **Routing Tests**
   - Verifiziere, dass URLs korrekt sind
   - Verifiziere, dass keine 404-Fehler auftreten

## Vergleich mit Referenz-Systemen

### SAP
- Klare Modul-Trennung: `/finance`, `/sales`, `/procurement`
- Konsistente URL-Struktur
- Keine Überschneidungen zwischen Modulen

### Odoo
- Modul-basierte URLs: `/finance/invoices`, `/sales/orders`
- Klare Hierarchie
- Konsistente Navigation

## Akzeptanzkriterien

- [ ] `/finance` zeigt Finance-Modul Übersicht
- [ ] `/finance/invoices` zeigt Invoices-Liste
- [ ] `/finance/invoices/new` zeigt Create Invoice Formular
- [ ] Navigation-Menü zeigt korrekte Links
- [ ] Keine 404-Fehler bei Navigation
- [ ] URLs sind konsistent und logisch

## Geschätzter Aufwand

- **Routing-Definitionen:** 0.5 Tage
- **Navigation-Komponenten:** 1 Tag
- **Komponenten-Migration:** 1-2 Tage
- **Testing:** 0.5 Tage
- **Gesamt:** 3-4 Tage

## Nächste Schritte

1. **Frontend-Entwickler:** Beginne mit Routing-Definitionen
2. **Frontend-Entwickler:** Erstelle Finance-Modul Übersicht
3. **Frontend-Entwickler:** Migriere/Erstelle Invoices-Komponenten
4. **Tester:** Teste Navigation und Routing

## Referenzen

- GAP-Analyse: `gap/gaps.md` (GAP-FIN-001)
- Test-Plan: `specs/finance.md` (TC-FIN-001, TC-FIN-002)
- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- Screenshots: 
  - `evidence/screenshots/finance/20251124_095102_03_finance_module.png`
  - `evidence/screenshots/finance/20251124_095105_04_invoices_list.png`

