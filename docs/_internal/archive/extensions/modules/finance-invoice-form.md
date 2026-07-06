# Feature Implementation Plan - Finance Invoice Form

**Erstellt:** 2025-11-24
**Basis:** GAP-FIN-002 (Create Invoice Formular unvollstÃ¤ndig)
**Status:** Planned
**PrioritÃ¤t:** P0 (Kritisch)

## Problem

Das Create Invoice Formular zeigt nur 1 Feld (Suchfeld) und ist damit nicht funktionsfÃ¤hig. Rechnungen kÃ¶nnen nicht erstellt werden.

## Anforderungen

### Funktionale Anforderungen

1. **Grundinformationen**
   - Rechnungsnummer (automatisch generiert)
   - Rechnungsdatum (Standard: heute)
   - FÃ¤lligkeitsdatum (basierend auf Zahlungsbedingungen)
   - Kunde (Pflichtfeld, Suche/Auswahl)
   - Rechnungsadresse (automatisch vom Kunden Ã¼bernommen, editierbar)

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
   - Zahlungsart (Ãœberweisung, Lastschrift, etc.)

4. **Aktionen**
   - Speichern (als Entwurf)
   - Speichern und buchen
   - Abbrechen
   - Vorschau/PDF

### Technische Anforderungen

1. **Frontend**
   - React-Komponente fÃ¼r Invoice-Formular
   - Form-Validation (Zod Schema)
   - Auto-Berechnung von BetrÃ¤gen
   - Responsive Design

2. **Backend**
   - API-Endpoint: `POST /api/v1/finance/invoices`
   - API-Endpoint: `GET /api/v1/finance/invoices/{id}`
   - API-Endpoint: `PUT /api/v1/finance/invoices/{id}`
   - Datenbank-Schema fÃ¼r Invoices

3. **Integration**
   - Kunden-Daten aus CRM-Modul
   - Artikel-Daten aus Inventory-Modul
   - MwSt-Berechnung aus Steuer-Modul

## Implementierungsplan

### Phase 1: Backend API (PrioritÃ¤t: Hoch)

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

### Phase 2: Frontend Formular (PrioritÃ¤t: Hoch)

1. **Komponenten**
   - `InvoiceForm.tsx` - Hauptformular
   - `InvoiceLineItem.tsx` - Positionen-Zeile
   - `InvoiceSummary.tsx` - Zusammenfassung
   - `CustomerSelector.tsx` - Kunden-Auswahl

2. **Form-Validation**
   - Zod Schema fÃ¼r Invoice
   - Client-side Validation
   - Error-Handling

3. **UI/UX**
   - Responsive Layout
   - Auto-Berechnung
   - Loading States
   - Success/Error Messages

### Phase 3: Integration (PrioritÃ¤t: Mittel)

1. **Kunden-Integration**
   - Kunden-Suche aus CRM
   - Kunden-Daten laden
   - Rechnungsadresse Ã¼bernehmen

2. **Artikel-Integration**
   - Artikel-Suche aus Inventory
   - Artikel-Daten laden
   - Preise Ã¼bernehmen

3. **Steuer-Integration**
   - MwSt-SÃ¤tze aus Steuer-Modul
   - MwSt-Berechnung

### Phase 4: Testing (PrioritÃ¤t: Hoch)

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
- VollstÃ¤ndiges Invoice-Formular mit allen Feldern
- Auto-Berechnung von BetrÃ¤gen
- Integration mit Kunden, Artikeln, Steuern
- Workflow (Entwurf â†’ Gebucht)

### Community ERP
- Einfacheres Formular, aber vollstÃ¤ndig
- Auto-Berechnung
- Integration mit anderen Modulen
- Direktes Buchen mÃ¶glich

## Akzeptanzkriterien

- [ ] Formular zeigt alle notwendigen Felder
- [ ] Rechnung kann erstellt werden
- [ ] BetrÃ¤ge werden automatisch berechnet
- [ ] Kunde kann ausgewÃ¤hlt werden
- [ ] Positionen kÃ¶nnen hinzugefÃ¼gt/entfernt werden
- [ ] Rechnung kann gespeichert werden
- [ ] Rechnung kann gebucht werden
- [ ] Validierung funktioniert korrekt
- [ ] Integration mit Kunden funktioniert
- [ ] Integration mit Artikeln funktioniert

## GeschÃ¤tzter Aufwand

- **Backend Modul:** 2-3 Tage
- **Frontend Formular:** 3-4 Tage
- **Integration:** 2-3 Tage
- **Testing:** 2-3 Tage
- **Gesamt:** 9-13 Tage

## NÃ¤chste Schritte

1. **Backend-Entwickler:** Beginne mit Datenbank-Schema und API-Endpoints
2. **Frontend-Entwickler:** Beginne mit Formular-Komponenten
3. **Tester:** Erstelle Test-Cases basierend auf diesem Plan

## Referenzen

- GAP-Analyse: `gap/gaps.md` (GAP-FIN-002)
- Test-Plan: `specs/finance.md` (TC-FIN-003)
- Handoff-Notiz: `swarm/handoffs/ui-explorer-finance-2025-11-24T08-51-19.344194.md`
- Screenshot: `evidence/screenshots/finance/20251124_095108_05_create_invoice_form.png`



