# Feature Implementation Plan - Finance Invoice Form

**Erstellt:** 2025-11-24  
**Basis:** GAP-FIN-002 (Create Invoice Formular unvollständig)  
**Status:** Planned  
**Priorität:** P0 (Kritisch)

## Problem

Das Create Invoice Formular zeigt nur 1 Feld (Suchfeld) und ist damit nicht funktionsfähig. Rechnungen können nicht erstellt werden.

## Anforderungen

### Funktionale Anforderungen

1. **Grundinformationen**
   - Rechnungsnummer (automatisch generiert)
   - Rechnungsdatum (Standard: heute)
   - Fälligkeitsdatum (basierend auf Zahlungsbedingungen)
   - Kunde (Pflichtfeld, Suche/Auswahl)
   - Rechnungsadresse (automatisch vom Kunden übernommen, editierbar)

2. **Positionen**
   - Artikel/Leistung (Pflichtfeld)
   - Beschreibung
   - Menge (Pflichtfeld)
   - Einheit (Stk, kg, m, etc.)
   - Einzelpreis (Pflichtfeld)
   - Rabatt (%)
   - Nettobetrag (automatisch berechnet)
   - MwSt-Satz (19%, 7%, 0%)
   - MwSt-Betrag (automatisch berechnet)
   - Bruttobetrag (automatisch berechnet)

3. **Zusammenfassung**
   - Summe Netto
   - Summe MwSt
   - Summe Brutto
   - Zahlungsbedingungen (30 Tage netto, etc.)
   - Zahlungsart (Überweisung, Lastschrift, etc.)

4. **Aktionen**
   - Speichern (als Entwurf)
   - Speichern und buchen
   - Abbrechen
   - Vorschau/PDF

### Technische Anforderungen

1. **Frontend**
   - React-Komponente für Invoice-Formular
   - Form-Validation (Zod Schema)
   - Auto-Berechnung von Beträgen
   - Responsive Design

2. **Backend**
   - API-Endpoint: `POST /api/v1/finance/invoices`
   - API-Endpoint: `GET /api/v1/finance/invoices/{id}`
   - API-Endpoint: `PUT /api/v1/finance/invoices/{id}`
   - Datenbank-Schema für Invoices

3. **Integration**
   - Kunden-Daten aus CRM-Modul
   - Artikel-Daten aus Inventory-Modul
   - MwSt-Berechnung aus Steuer-Modul

## Implementierungsplan

### Phase 1: Backend API (Priorität: Hoch)

1. **Datenbank-Schema**
   - Tabelle `invoices`
   - Tabelle `invoice_lines`
   - Beziehungen zu `customers`, `articles`, `tax_codes`

2. **API-Endpoints**
   - `POST /api/v1/finance/invoices` - Rechnung erstellen
   - `GET /api/v1/finance/invoices/{id}` - Rechnung abrufen
   - `PUT /api/v1/finance/invoices/{id}` - Rechnung aktualisieren
   - `GET /api/v1/finance/invoices` - Rechnungen auflisten

3. **Business Logic**
   - Rechnungsnummer-Generierung
   - Betrags-Berechnung (Netto, MwSt, Brutto)
   - Validierung

### Phase 2: Frontend Formular (Priorität: Hoch)

1. **Komponenten**
   - `InvoiceForm.tsx` - Hauptformular
   - `InvoiceLineItem.tsx` - Positionen-Zeile
   - `InvoiceSummary.tsx` - Zusammenfassung
   - `CustomerSelector.tsx` - Kunden-Auswahl

2. **Form-Validation**
   - Zod Schema für Invoice
   - Client-side Validation
   - Error-Handling

3. **UI/UX**
   - Responsive Layout
   - Auto-Berechnung
   - Loading States
   - Success/Error Messages

### Phase 3: Integration (Priorität: Mittel)

1. **Kunden-Integration**
   - Kunden-Suche aus CRM
   - Kunden-Daten laden
   - Rechnungsadresse übernehmen

2. **Artikel-Integration**
   - Artikel-Suche aus Inventory
   - Artikel-Daten laden
   - Preise übernehmen

3. **Steuer-Integration**
   - MwSt-Sätze aus Steuer-Modul
   - MwSt-Berechnung

### Phase 4: Testing (Priorität: Hoch)

1. **Unit Tests**
   - Form-Validation
   - Betrags-Berechnung
   - API-Endpoints

2. **Integration Tests**
   - End-to-End Create Invoice Flow
   - Kunden-Integration
   - Artikel-Integration

3. **E2E Tests**
   - Playwright-Tests basierend auf Test-Plan

## Vergleich mit Referenz-Systemen

### SAP
- Vollständiges Invoice-Formular mit allen Feldern
- Auto-Berechnung von Beträgen
- Integration mit Kunden, Artikeln, Steuern
- Workflow (Entwurf → Gebucht)

### Odoo
- Einfacheres Formular, aber vollständig
- Auto-Berechnung
- Integration mit anderen Modulen
- Direktes Buchen möglich

## Akzeptanzkriterien

- [ ] Formular zeigt alle notwendigen Felder
- [ ] Rechnung kann erstellt werden
- [ ] Beträge werden automatisch berechnet
- [ ] Kunde kann ausgewählt werden
- [ ] Positionen können hinzugefügt/entfernt werden
- [ ] Rechnung kann gespeichert werden
- [ ] Rechnung kann gebucht werden
- [ ] Validierung funktioniert korrekt
- [ ] Integration mit Kunden funktioniert
- [ ] Integration mit Artikeln funktioniert

## Geschätzter Aufwand

- **Backend API:** 2-3 Tage
- **Frontend Formular:** 3-4 Tage
- **Integration:** 2-3 Tage
- **Testing:** 2-3 Tage
- **Gesamt:** 9-13 Tage

## Nächste Schritte

1. **Backend-Entwickler:** Beginne mit Datenbank-Schema und API-Endpoints
2. **Frontend-Entwickler:** Beginne mit Formular-Komponenten
3. **Tester:** Erstelle Test-Cases basierend auf diesem Plan

## Referenzen

- GAP-Analyse: `gap/gaps.md` (GAP-FIN-002)
- Test-Plan: `specs/finance.md` (TC-FIN-003)
- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- Screenshot: `evidence/screenshots/finance/20251124_095108_05_create_invoice_form.png`

